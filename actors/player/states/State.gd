class_name State extends Node

var player: Player
var sm: StateMachine

func enter(_msg := {}) -> void: pass
func exit() -> void: pass
func handle_input(_event: InputEvent) -> void: pass
func physics_update(_delta: float) -> void: pass
