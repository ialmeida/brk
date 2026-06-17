class_name BossHurt extends BossState

func enter(_msg := {}) -> void:
	boss.velocity = Vector2.ZERO
	boss.play_anim("hurt")

func _on_hurt_finished() -> void:
	sm.transition_to("BossIdle")
