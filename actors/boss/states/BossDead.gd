class_name BossDead extends BossState

func enter(_msg := {}) -> void:
	boss.velocity = Vector2.ZERO
	boss.hitbox.disable()
	boss.hurtbox.monitorable = false
	boss.sm.set_physics_process(false)
	boss.play_anim("dead")
