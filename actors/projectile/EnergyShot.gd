class_name EnergyShot extends Area2D

@export var speed: float = 360.0
@export var chip_damage: float = 6.0
@export var chip_defense_debuff: float = 0.5
@export var ultimate_defense_debuff: float = 0.5
@export var lifetime: float = 3.0

var _velocity := Vector2.ZERO
var _source: Node
var _is_ultimate := false
var _age := 0.0

func _ready() -> void:
	monitoring = true
	area_entered.connect(_on_area_entered)

func launch(source: Node, is_ultimate: bool, _charge_t: float) -> void:
	_source = source
	_is_ultimate = is_ultimate
	var dir := Vector2.RIGHT
	if source.has_method("get_facing_direction"):
		dir = source.get_facing_direction()
	_velocity = dir * speed
	rotation = dir.angle()

func _physics_process(delta: float) -> void:
	position += _velocity * delta
	_age += delta
	if _age >= lifetime:
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	if not area is Hurtbox:
		return
	area.receive_hit(_build_damage_info())
	queue_free()

func _build_damage_info() -> DamageInfo:
	var amount := chip_damage
	var debuff := chip_defense_debuff
	if _is_ultimate:
		amount *= CombatConfig.ULTIMATE_DAMAGE_MULT
		debuff = ultimate_defense_debuff
	if _source and "stats" in _source and _source.stats:
		amount *= _source.stats.damage_mult
	return DamageInfo.new(amount, debuff, _source, _is_ultimate)
