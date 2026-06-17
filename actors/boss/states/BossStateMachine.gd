class_name BossStateMachine extends Node

@export var initial_state: NodePath
var current: BossState
var states := {}

func setup(owner_boss: Boss) -> void:
	for child in get_children():
		if child is BossState:
			child.boss = owner_boss
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

func _physics_process(delta: float) -> void:
	if current: current.physics_update(delta)
