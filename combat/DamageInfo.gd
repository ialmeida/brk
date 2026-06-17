class_name DamageInfo extends RefCounted

var amount: float
var defense_debuff: float
var source: Node
var is_finisher: bool

func _init(p_amount := 0.0, p_defense_debuff := 0.0, p_source: Node = null, p_is_finisher := false) -> void:
	amount = p_amount
	defense_debuff = p_defense_debuff
	source = p_source
	is_finisher = p_is_finisher
