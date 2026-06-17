class_name Player extends CharacterBody2D

signal master_final_landed(target)

enum LinkState { NONE, PENDING, OPEN, EXPIRED }
var link_state: int = LinkState.NONE
var facing := Vector2.RIGHT

@onready var sm: StateMachine = $StateMachine
@onready var combo: ComboBuffer = $ComboBuffer
@onready var stats: StatsComponent = $StatsComponent
@onready var health: HealthComponent = $HealthComponent
@onready var hitbox: Hitbox = $Hitbox
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var link_timer: Timer = $LinkWindowTimer
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
	add_to_group("player")
	hitbox.owner_stats = stats
	hurtbox.health = health
	hurtbox.stats = stats
	hitbox.hit_landed.connect(_on_hit_landed)
	hurtbox.damage_received.connect(_on_damage_received)
	sm.setup(self)

func get_input_dir() -> Vector2:
	var dir := Vector2(
		Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
		Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
	)
	return dir.normalized() if dir.length() > 1.0 else dir

func get_facing_direction() -> Vector2:
	return facing

func set_facing(dir: Vector2) -> void:
	if dir.x != 0.0:
		facing = Vector2(sign(dir.x), 0.0)
		animated_sprite.flip_h = dir.x < 0.0

func play_anim(anim_name: String) -> void:
	if animation_player.has_animation(anim_name):
		animation_player.play(anim_name)
	if animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(anim_name):
		animated_sprite.play(anim_name)

func play_combo_anim(combo_result: Dictionary) -> void:
	var anim_name := "%s_%d" % [combo_result.name, combo_result.step_index + 1]
	play_anim(anim_name)

func _on_hit_landed(target: Node, combo_result: Dictionary) -> void:
	SkillProgression.record_use(combo_result.get("name", ""), true)
	if combo_result.get("is_complete") and combo_result.get("on_final") == "stagger":
		master_final_landed.emit(target)
		_arm_link_window()

func _on_damage_received(_info: DamageInfo) -> void:
	if not health.is_dead():
		sm.transition_to("Hurt")

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
