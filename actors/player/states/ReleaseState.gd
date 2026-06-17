class_name ReleaseState extends State

const ENERGY_SHOT_SCENE := preload("res://actors/projectile/EnergyShot.tscn")

func enter(msg := {}) -> void:
	player.velocity = Vector2.ZERO
	var is_ultimate: bool = msg.get("ultimate", false)
	var charge_t: float = msg.get("charge_t", 0.0)
	_fire(is_ultimate, charge_t)
	SkillProgression.record_use("charge", true)
	player.play_anim("release")
	sm.transition_to("Idle")

func _fire(is_ultimate: bool, charge_t: float) -> void:
	var shot: EnergyShot = ENERGY_SHOT_SCENE.instantiate()
	player.get_tree().current_scene.add_child(shot)
	shot.global_position = player.global_position
	shot.launch(player, is_ultimate, charge_t)
