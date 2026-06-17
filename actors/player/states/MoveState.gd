class_name MoveState extends State

func enter(_msg := {}) -> void:
	player.play_anim("move")

func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("punch"):
		sm.transition_to("Attack", { "token": "P" })
	elif event.is_action_pressed("kick"):
		sm.transition_to("Attack", { "token": "K" })
	elif event.is_action_pressed("charge"):
		sm.transition_to("Charge")

func physics_update(_delta: float) -> void:
	var dir := player.get_input_dir()
	if dir == Vector2.ZERO:
		sm.transition_to("Idle")
		return
	player.set_facing(dir)
	player.velocity = dir * player.stats.move_speed
	player.move_and_slide()
