class_name BossState extends Node

var boss: Boss
var sm: BossStateMachine

func enter(_msg := {}) -> void: pass
func exit() -> void: pass
func physics_update(_delta: float) -> void: pass
