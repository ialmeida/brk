class_name BossIdle extends BossState

func enter(_msg := {}) -> void:
	boss.velocity = Vector2.ZERO
	boss.play_anim("idle")

func physics_update(_delta: float) -> void:
	if boss.ai_enabled and boss.is_player_in_attack_range():
		sm.transition_to("BossAttack")
