class_name IdleState extends State

func enter(_msg := {}) -> void:
	player.velocity = Vector2.ZERO
	player.play_anim("idle")

func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("punch"):
		sm.transition_to("Attack", { "token": "P" })
	elif event.is_action_pressed("kick"):
		sm.transition_to("Attack", { "token": "K" })
	elif event.is_action_pressed("charge"):
		sm.transition_to("Charge")

func physics_update(_delta: float) -> void:
	if player.get_input_dir() != Vector2.ZERO:
		sm.transition_to("Move")
