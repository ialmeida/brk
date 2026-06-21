class_name RecoverState extends State

# Brief settle that plays after the final hit of a combo so the character eases back to neutral
# instead of snapping. Mirrors HurtState's "play a short anim, then return to Idle" shape, but
# uses a guarded timer (the recover visual has no hitbox/AnimationPlayer combat track). The
# settle is cancelable into movement or another attack so it never feels like dead time.

const RECOVER_TIME := 0.15  # keep in sync with update_player_tscn.RECOVER_GAMEPLAY_LENGTH
var _gen := 0

func enter(_msg := {}) -> void:
	player.velocity = Vector2.ZERO
	player.play_anim("recover")
	_gen += 1
	_return_to_idle_after(_gen)

func _return_to_idle_after(gen: int) -> void:
	await player.get_tree().create_timer(RECOVER_TIME).timeout
	# Ignore a stale timer if we already left Recover (or re-entered it since).
	if sm.current == self and gen == _gen:
		sm.transition_to("Idle")

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
		return
	player.velocity = Vector2.ZERO
	player.move_and_slide()
