class_name StateMachine extends Node

@export var initial_state: NodePath
var current: State
var states := {}

func setup(owner_player: Player) -> void:
	for child in get_children():
		if child is State:
			child.player = owner_player
			child.sm = self
			states[child.name.to_lower()] = child
	current = get_node(initial_state)
	current.enter()

func transition_to(state_name: String, msg := {}) -> void:
	var key := state_name.to_lower()
	if not states.has(key) or states[key] == current:
		return
	current.exit()
	current = states[key]
	current.enter(msg)

func _unhandled_input(event: InputEvent) -> void:
	if current: current.handle_input(event)

func _physics_process(delta: float) -> void:
	if current: current.physics_update(delta)
