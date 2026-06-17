class_name Hurtbox extends Area2D

signal damage_received(info: DamageInfo)

var health: HealthComponent
var stats: StatsComponent

func receive_hit(info: DamageInfo) -> void:
	var final_amount: float = info.amount
	if stats:
		final_amount = max(0.0, final_amount - stats.defense)
		if info.defense_debuff > 0.0:
			stats.apply_defense_debuff(info.defense_debuff)
	if health:
		health.take_damage(final_amount)
	damage_received.emit(info)
