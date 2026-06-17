class_name StatsComponent extends Node

const SPEED_SCALE := 0.15
const STR_SCALE := 0.2

@export var strength: float = 1.0
@export var speed: float = 1.0
@export var defense: float = 0.0
@export var base_move_speed: float = 120.0

var move_speed: float:
	get: return base_move_speed * (1.0 + speed * SPEED_SCALE)

var damage_mult: float:
	get: return 1.0 + strength * STR_SCALE

func apply_defense_debuff(amount: float) -> void:
	defense = max(0.0, defense - amount)
