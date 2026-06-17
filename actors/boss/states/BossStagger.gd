class_name BossStagger extends BossState

func enter(_msg := {}) -> void:
	boss.velocity = Vector2.ZERO
	boss.play_anim("stagger")
	boss.stagger_timer.timeout.connect(_on_stagger_done, CONNECT_ONE_SHOT)
	boss.stagger_timer.start(CombatConfig.STAGGER_DURATION)

func _on_stagger_done() -> void:
	sm.transition_to("BossIdle")
