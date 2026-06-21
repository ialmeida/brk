# Spec: 2D Action-RPG Demo (Godot 4.x)

## Context

Greenfield project. We are building an offline, single-player, 16-bit pixel-art action RPG
**demo** in Godot 4.x / GDScript. The demo proves out a melee-combo + chargeable-energy
combat loop whose centerpiece is a **Master Combo timing link**: `Punch → Kick → Kick →
Punch` staggers the enemy, and a precisely-timed energy charge initiation during that
stagger window links into a heavy ultimate finisher.

Decisions locked:
- **Engine:** Godot **4.x** (`CharacterBody2D`, `await`, typed GDScript 2.0, signals as Callables).
- **Player FSM:** **Node-based** — each state is a child `Node` with `enter/exit/physics_update/handle_input`.
- **Hit detection:** **Hitbox/Hurtbox `Area2D`** overlap, attack frames driven by `AnimationPlayer`.

---

## 1. Project Structure

```
brk/
├── project.godot
├── icon.svg
├── autoload/
│   ├── GameState.gd          # singleton: current scene, demo flags
│   └── CombatConfig.gd       # singleton: tunable combat constants (windows, multipliers)
├── components/               # reusable, scene-agnostic nodes
│   ├── Hitbox.gd / Hitbox.tscn
│   ├── Hurtbox.gd / Hurtbox.tscn
│   ├── HealthComponent.gd
│   └── StatsComponent.gd     # Strength, Speed, derived multipliers
├── combat/
│   ├── ComboDefinitions.gd   # data: named combo sequences + per-step multipliers
│   ├── ComboBuffer.gd        # input buffer + sequence matcher
│   └── DamageInfo.gd         # RefCounted payload: amount, debuff, source, is_finisher
├── actors/
│   ├── player/
│   │   ├── Player.tscn
│   │   ├── Player.gd
│   │   └── states/
│   │       ├── StateMachine.gd
│   │       ├── State.gd            # base class
│   │       ├── IdleState.gd
│   │       ├── MoveState.gd
│   │       ├── AttackState.gd      # handles ALL melee combo steps (punch/kick)
│   │       ├── ChargeState.gd      # holding energy charge (slowed movement)
│   │       ├── ReleaseState.gd     # fire projectile (normal OR ultimate)
│   │       └── HurtState.gd
│   ├── boss/
│   │   ├── Boss.tscn
│   │   ├── Boss.gd
│   │   └── states/ (BossIdle, BossAttack, BossStagger, BossHurt, BossDead)
│   └── projectile/
│       ├── EnergyShot.tscn
│       └── EnergyShot.gd     # carries chip dmg + defense-debuff; ultimate variant = heavy
├── skills/
│   └── SkillProgression.gd   # usage-based skill leveling (no global XP pool)
└── scenes/
    ├── Dojo.tscn / Dojo.gd        # Scene 1: tutorial
    └── BossArena.tscn / BossArena.gd  # Scene 2: final boss
```

**Autoloads (Project Settings → Globals):** `GameState`, `CombatConfig`, `SkillProgression`.

---

## 2. Node Trees

### Player (`Player.tscn`)
```
Player (CharacterBody2D)            # Player.gd
├── AnimatedSprite2D                # 16-bit frames; per-combo-step animations
├── Camera2D                        # zoom 3x; follows the player (child of Player)
├── CollisionShape2D                # body collision (world)
├── StateMachine (Node)             # StateMachine.gd, exports initial_state
│   ├── Idle (Node)                 # IdleState.gd
│   ├── Move (Node)
│   ├── Attack (Node)
│   ├── Charge (Node)
│   ├── Release (Node)
│   └── Hurt (Node)
├── Hitbox (Area2D)                 # Hitbox.gd — enabled only on attack frames
│   └── CollisionShape2D (disabled by default)
├── Hurtbox (Area2D)                # Hurtbox.gd — receives DamageInfo
│   └── CollisionShape2D
├── StatsComponent (Node)           # Strength, Speed
├── HealthComponent (Node)
├── ComboBuffer (Node)              # ComboBuffer.gd
├── AnimationPlayer                 # call-method tracks toggle Hitbox on active frames
└── LinkWindowTimer (Timer)         # one-shot; used for charge-link timing (see §5)
```

### Boss (`Boss.tscn`)
```
Boss (CharacterBody2D)              # Boss.gd
├── AnimatedSprite2D
├── CollisionShape2D
├── StateMachine (Node)
│   ├── BossIdle / BossAttack / BossStagger / BossHurt / BossDead
├── Hitbox (Area2D)
├── Hurtbox (Area2D)               # applies defense debuff when hit by EnergyShot
├── HealthComponent (Node)
├── StatsComponent (Node)          # includes 'defense' that the debuff lowers
├── StaggerTimer (Timer)           # one-shot; defines stagger duration / recovery
└── AnimationPlayer
```

### Dojo (`Dojo.tscn`) — Scene 1 tutorial
```
Dojo (Node2D)                       # Dojo.gd — drives staged tutorial prompts
├── TileMapLayer                    # floor/walls
├── Player (instance of Player.tscn)
├── TrainingDummy (instance of Boss.tscn, AI disabled / passive)
├── TutorialUI (CanvasLayer)
│   └── PromptLabel
└── StageTriggers (Node)            # Area2D triggers advancing: punch→kick→master combo
```

### Boss Arena (`BossArena.tscn`) — Scene 2
```
BossArena (Node2D)
├── TileMapLayer
├── Player (instance)               # carries its own follow Camera2D
├── Boss (instance, AI enabled)
└── HUD (CanvasLayer): player HP, boss HP, charge meter
```

---

## 3. Stats & Skill Progression

`StatsComponent.gd` (exported, tunable):
- `strength: float`, `speed: float`, `defense: float`.
- Derived: `move_speed = base_move_speed * (1.0 + speed * SPEED_SCALE)`.
- Derived: `damage_mult = 1.0 + strength * STR_SCALE`.

`SkillProgression.gd` (autoload, **no global XP pool** — per-skill usage counters):
- Tracks `punch`, `kick`, `charge`, `master_combo` usage counts.
- On each successful use, increment counter; at thresholds, bump the relevant stat or
  unlock a combo multiplier tier. Persisted in-memory for the demo (save optional).
- Public: `record_use(skill_id: String, landed: bool)` called from `AttackState`/`ReleaseState`.

---

## 4. Combat Data

`ComboDefinitions.gd` — sequences are arrays of `"P"`/`"K"` tokens with per-step multipliers:
```gdscript
const COMBOS := {
    "basic_punch": { "seq": ["P", "P", "P"],       "mult": [1.0, 1.2, 1.5] },
    "basic_kick":  { "seq": ["K", "K", "K"],       "mult": [1.0, 1.3, 1.7] },
    "master":      { "seq": ["P", "K", "K", "P"],  "mult": [1.0, 1.2, 1.4, 2.2],
                      "on_final": "stagger" },
}
```

`EnergyShot.gd` payload (via `DamageInfo`):
- Normal: low `amount` (chip) + `defense_debuff` (persistent on target).
- Ultimate (linked): large `amount`, also keeps the debuff. `is_finisher = true`.

`CombatConfig.gd` constants (single tuning surface):
```gdscript
const CHARGE_MOVE_PENALTY  := 0.4    # movement multiplier while charging
const CHARGE_FULL_TIME     := 1.0    # seconds to full normal charge
const STAGGER_DURATION     := 0.55   # boss stagger length
const LINK_OPEN_DELAY      := 0.12   # closed window before it opens (too-early zone)
const LINK_WINDOW          := 0.22   # valid window to START charge for link
const ULTIMATE_DAMAGE_MULT := 4.0
```

---

## 5. Core Logic: Combo Buffer, Master Combo → Stagger, Charge-Link Timing

Three cooperating pieces:

**(a) Input buffering** — `ComboBuffer` records `"P"`/`"K"` presses with timestamps, drops
tokens older than a TTL window, and prefix-matches against `ComboDefinitions`. A partial
prefix keeps the chain alive; a complete match fires.

**(b) Master-combo → stagger** — When `AttackState` lands the *final* `P` of the `master`
sequence on the boss's hurtbox, the player emits `master_final_landed`. The boss FSM
transitions to `BossStagger` (starts `StaggerTimer`). Simultaneously the player arms its
**link window**.

**(c) Charge-link timing** — On `master_final_landed`, the player enters `LinkState.PENDING`
for `LINK_OPEN_DELAY` seconds (pressing charge here = **too early → fail**), then
`LinkState.OPEN` for `LINK_WINDOW` seconds (press here = **linked ultimate**), then
`LinkState.EXPIRED` (press = **too late → normal charge**).

### `State.gd` (base)
```gdscript
class_name State extends Node

var player: Player
var sm: StateMachine

func enter(_msg := {}) -> void: pass
func exit() -> void: pass
func handle_input(_event: InputEvent) -> void: pass
func physics_update(_delta: float) -> void: pass
```

### `StateMachine.gd`
```gdscript
class_name StateMachine extends Node

@export var initial_state: NodePath
var current: State
var states := {}

func setup(owner_player: Player) -> void:
    for child in get_children():
        if child is State:
            child.player = owner_player
            child.sm = self
            states[child.name.to_lower()] = child
    current = get_node(initial_state)
    current.enter()

func transition_to(state_name: String, msg := {}) -> void:
    var key := state_name.to_lower()
    if not states.has(key) or states[key] == current:
        return
    current.exit()
    current = states[key]
    current.enter(msg)

func _unhandled_input(event: InputEvent) -> void:
    if current: current.handle_input(event)

func _physics_process(delta: float) -> void:
    if current: current.physics_update(delta)
```

### `ComboBuffer.gd`
```gdscript
class_name ComboBuffer extends Node

const TOKEN_TTL := 0.6

var _tokens: Array = []   # [{ "t": "P"/"K", "time": float }]

func push(token: String) -> void:
    _tokens.append({ "t": token, "time": Time.get_ticks_msec() / 1000.0 })
    _prune()

func _prune() -> void:
    var now := Time.get_ticks_msec() / 1000.0
    _tokens = _tokens.filter(func(x): return now - x.time <= TOKEN_TTL)

func clear() -> void:
    _tokens.clear()

func current_sequence() -> Array:
    _prune()
    return _tokens.map(func(x): return x.t)

# Returns { name, step_index, mult, is_complete, on_final } or {} if no prefix matches.
func match_combo() -> Dictionary:
    var seq := current_sequence()
    if seq.is_empty(): return {}
    for combo_name in ComboDefinitions.COMBOS:
        var def = ComboDefinitions.COMBOS[combo_name]
        var target: Array = def.seq
        if seq.size() > target.size(): continue
        var ok := true
        for i in seq.size():
            if seq[i] != target[i]: ok = false; break
        if ok:
            var idx := seq.size() - 1
            return {
                "name": combo_name,
                "step_index": idx,
                "mult": def.mult[idx],
                "is_complete": seq.size() == target.size(),
                "on_final": def.get("on_final", ""),
            }
    return {}
```

### `Player.gd`
```gdscript
class_name Player extends CharacterBody2D

signal master_final_landed(target)

enum LinkState { NONE, PENDING, OPEN, EXPIRED }
var link_state: int = LinkState.NONE

@onready var sm: StateMachine     = $StateMachine
@onready var combo: ComboBuffer   = $ComboBuffer
@onready var stats: StatsComponent = $StatsComponent
@onready var hitbox: Hitbox       = $Hitbox
@onready var link_timer: Timer    = $LinkWindowTimer

func _ready() -> void:
    sm.setup(self)
    hitbox.hit_landed.connect(_on_hit_landed)

func _on_hit_landed(target, combo_result: Dictionary) -> void:
    if combo_result.get("is_complete") and combo_result.get("on_final") == "stagger":
        master_final_landed.emit(target)
        _arm_link_window()

func _arm_link_window() -> void:
    link_state = LinkState.PENDING
    link_timer.start(CombatConfig.LINK_OPEN_DELAY)
    link_timer.timeout.connect(_open_link_window, CONNECT_ONE_SHOT)

func _open_link_window() -> void:
    link_state = LinkState.OPEN
    link_timer.start(CombatConfig.LINK_WINDOW)
    link_timer.timeout.connect(_expire_link_window, CONNECT_ONE_SHOT)

func _expire_link_window() -> void:
    link_state = LinkState.EXPIRED

# "linked" -> ultimate  |  "too_early" -> fail  |  "normal" -> standard charge
func evaluate_charge_start() -> String:
    match link_state:
        LinkState.OPEN:
            link_state = LinkState.NONE
            return "linked"
        LinkState.PENDING:
            link_state = LinkState.NONE
            return "too_early"
        _:
            return "normal"
```

### `AttackState.gd`
```gdscript
class_name AttackState extends State

var active_combo: Dictionary

func handle_input(event: InputEvent) -> void:
    if event.is_action_pressed("punch"): _queue("P")
    elif event.is_action_pressed("kick"): _queue("K")
    elif event.is_action_pressed("charge"): sm.transition_to("Charge")

func _queue(token: String) -> void:
    player.combo.push(token)
    var result := player.combo.match_combo()
    if result.is_empty():
        player.combo.clear()
        sm.transition_to("Idle")
        return
    active_combo = result
    player.hitbox.pending_result = result
    player.animated_sprite_play(result)
    SkillProgression.record_use(result.name, false)
    # AnimationPlayer call-method track enables hitbox on active frames,
    # then calls _on_step_finished() to gate the next input or return to Idle.
```

### `ChargeState.gd`
```gdscript
class_name ChargeState extends State

var charge_t := 0.0
var is_ultimate := false

func enter(_msg := {}) -> void:
    var verdict := player.evaluate_charge_start()
    if verdict == "too_early":
        sm.transition_to("Idle")
        return
    is_ultimate = verdict == "linked"
    charge_t = 0.0

func physics_update(delta: float) -> void:
    charge_t += delta
    var slow := CombatConfig.CHARGE_MOVE_PENALTY
    player.velocity = player.get_input_dir() * player.stats.move_speed * slow
    player.move_and_slide()
    if not Input.is_action_pressed("charge"):
        sm.transition_to("Release", { "ultimate": is_ultimate, "charge_t": charge_t })
```

### Boss stagger hook (`Boss.gd`)
```gdscript
func _ready() -> void:
    get_tree().get_first_node_in_group("player").master_final_landed.connect(_on_staggered)

func _on_staggered(target) -> void:
    if target == self:
        sm.transition_to("BossStagger")
```

---

## 6. Demo Scenes / Flow

- **Dojo.gd** — tutorial state list: (1) land `basic_punch`, (2) land `basic_kick`,
  (3) execute `master` and time the charge link. Training dummy uses `Boss.tscn` with
  AI disabled (can stagger, cannot retaliate).
- **BossArena.gd** — Boss AI enabled. Win condition: boss `HealthComponent` reaches 0.
  Intended kill path: positioning + Master Combo → linked ultimate.
- `GameState` autoload stores the active scene and "tutorial complete" flag.

---

## 7. Verification

1. **Open in Godot 4.x** — no script errors; all three autoloads load.
2. **Dojo (`F6` on Dojo.tscn):**
   - Three punches → `basic_punch` chain, escalating damage.
   - Three kicks → `basic_kick` chain.
   - P-K-K-P → dummy staggers on final punch.
3. **Timing-link (instrument `evaluate_charge_start()` with `print`):**
   - Charge immediately → `"too_early"`.
   - Charge within `LINK_OPEN_DELAY + LINK_WINDOW` → `"linked"`, release fires ultimate.
   - Charge after window → `"normal"`.
   - Charge with no prior master combo → `"normal"`, movement slowed.
4. **EnergyShot** — chip damage + persistent defense debuff on normal hit; heavy damage on ultimate.
5. **Boss arena** — full loop ends in boss death.
6. **Skill progression** — usage counters increment; no global XP pool.

---

## 8. Open Items
- `AnimatedSprite2D` frames and `AnimationPlayer` hitbox-toggle tracks need real 16-bit art.
- Boss AI is intentionally minimal (Idle/Attack/Stagger).
- `SkillProgression` is in-memory; serialization is optional.
