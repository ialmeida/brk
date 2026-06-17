class_name ChargeState extends State

var charge_t := 0.0
var is_ultimate := false

func enter(_msg := {}) -> void:
	var verdict := player.evaluate_charge_start()
	if verdict == "too_early":
		sm.transition_to("Idle")
		return
	is_ultimate = verdict == "linked"
	charge_t = 0.0
	player.play_anim("charge_loop")

func physics_update(delta: float) -> void:
	charge_t += delta
	var slow := CombatConfig.CHARGE_MOVE_PENALTY
	player.velocity = player.get_input_dir() * player.stats.move_speed * slow
	player.move_and_slide()
	if not Input.is_action_pressed("charge"):
		sm.transition_to("Release", { "ultimate": is_ultimate, "charge_t": charge_t })
