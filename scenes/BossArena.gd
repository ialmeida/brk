extends Node2D

@onready var player: Player = $Player
@onready var boss: Boss = $Boss
@onready var player_hp_bar: ProgressBar = $HUD/PlayerHP
@onready var boss_hp_bar: ProgressBar = $HUD/BossHP
@onready var charge_meter: ProgressBar = $HUD/ChargeMeter

func _ready() -> void:
	GameState.current_scene = GameState.Scene.BOSS_ARENA
	boss.ai_enabled = true
	player.health.health_changed.connect(_on_player_health_changed)
	boss.health.health_changed.connect(_on_boss_health_changed)
	_on_player_health_changed(player.health.current_health, player.health.max_health)
	_on_boss_health_changed(boss.health.current_health, boss.health.max_health)

func _process(_delta: float) -> void:
	if player.sm.current is ChargeState:
		var charge_state := player.sm.current as ChargeState
		var pct: float = clamp(charge_state.charge_t / CombatConfig.CHARGE_FULL_TIME, 0.0, 1.0)
		charge_meter.value = pct * charge_meter.max_value
	else:
		charge_meter.value = 0.0

func _on_player_health_changed(current: float, max_value: float) -> void:
	player_hp_bar.max_value = max_value
	player_hp_bar.value = current

func _on_boss_health_changed(current: float, max_value: float) -> void:
	boss_hp_bar.max_value = max_value
	boss_hp_bar.value = current
