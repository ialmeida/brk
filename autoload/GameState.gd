extends Node

enum Scene { DOJO, BOSS_ARENA }

const SCENE_PATHS := {
	Scene.DOJO: "res://scenes/Dojo.tscn",
	Scene.BOSS_ARENA: "res://scenes/BossArena.tscn",
}

var current_scene: Scene = Scene.DOJO
var tutorial_complete: bool = false

func goto_scene(scene: Scene) -> void:
	current_scene = scene
	get_tree().change_scene_to_file(SCENE_PATHS[scene])
