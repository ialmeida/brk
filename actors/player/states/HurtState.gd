class_name HurtState extends State

func enter(_msg := {}) -> void:
	player.velocity = Vector2.ZERO
	player.combo.clear()
	player.play_anim("hurt")

func _on_hurt_finished() -> void:
	sm.transition_to("Idle")
