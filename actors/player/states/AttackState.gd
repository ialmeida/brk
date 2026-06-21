class_name AttackState extends State

var active_combo: Dictionary

func enter(msg := {}) -> void:
	active_combo = {}
	if msg.has("token"):
		_queue(msg.token)

func exit() -> void:
	player.hitbox.disable()

func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("punch"):
		_queue("P")
	elif event.is_action_pressed("kick"):
		_queue("K")
	elif event.is_action_pressed("charge"):
		sm.transition_to("Charge")

func _queue(token: String) -> void:
	player.combo.push(token)
	var result := player.combo.match_combo()
	if result.is_empty():
		player.combo.clear()
		sm.transition_to("Idle")
		return
	active_combo = result
	player.hitbox.pending_result = result
	player.play_combo_anim(result)
	SkillProgression.record_use(result.name, false)
	# AnimationPlayer call-method track enables hitbox on active frames,
	# then calls _on_step_finished() to gate the next input or return to Idle.

func physics_update(_delta: float) -> void:
	player.velocity = Vector2.ZERO
	player.move_and_slide()

func _on_step_finished() -> void:
	if active_combo.get("is_complete", false):
		player.combo.clear()
		sm.transition_to("Recover")
