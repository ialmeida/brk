class_name Hitbox extends Area2D

signal hit_landed(target: Node, combo_result: Dictionary)

@export var base_damage: float = 10.0
@export var reach: float = 13.0

var owner_stats: StatsComponent
var pending_result: Dictionary = {}
var _hit_targets: Array = []

@onready var _shape: CollisionShape2D = $CollisionShape2D

func enable() -> void:
	_hit_targets.clear()
	_shape.disabled = false

func disable() -> void:
	_shape.disabled = true

func aim(dir: Vector2) -> void:
	if dir == Vector2.ZERO:
		return
	var d := dir.normalized()
	position = d * reach
	rotation = d.angle()

func _physics_process(_delta: float) -> void:
	if _shape.disabled:
		return
	for area in get_overlapping_areas():
		_try_hit(area)

func _try_hit(area: Area2D) -> void:
	if not area is Hurtbox or area in _hit_targets:
		return
	_hit_targets.append(area)
	var info := _build_damage_info()
	area.receive_hit(info)
	hit_landed.emit(area.get_parent(), pending_result)

func _build_damage_info() -> DamageInfo:
	var mult: float = pending_result.get("mult", 1.0)
	var dmg_mult := owner_stats.damage_mult if owner_stats else 1.0
	return DamageInfo.new(base_damage * mult * dmg_mult, 0.0, get_parent(), false)
