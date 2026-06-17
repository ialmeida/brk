class_name BossAttack extends BossState

func enter(_msg := {}) -> void:
	boss.velocity = Vector2.ZERO
	boss.hitbox.pending_result = { "name": "boss_attack", "mult": 1.0 }
	boss.aim_at_player()
	boss.play_anim("attack")

func exit() -> void:
	boss.hitbox.disable()

func _on_attack_finished() -> void:
	sm.transition_to("BossIdle")
