extends Node2D

enum Stage { PUNCH, KICK, MASTER, DONE }

var stage: Stage = Stage.PUNCH

@onready var player: Player = $Player
@onready var dummy: Boss = $TrainingDummy
@onready var prompt_label: Label = $TutorialUI/PromptLabel

func _ready() -> void:
	GameState.current_scene = GameState.Scene.DOJO
	dummy.ai_enabled = false
	player.hitbox.hit_landed.connect(_on_player_hit_landed)
	_update_prompt()

func _on_player_hit_landed(_target: Node, combo_result: Dictionary) -> void:
	if not combo_result.get("is_complete", false):
		return
	match stage:
		Stage.PUNCH:
			if combo_result.get("name") == "basic_punch":
				stage = Stage.KICK
		Stage.KICK:
			if combo_result.get("name") == "basic_kick":
				stage = Stage.MASTER
		Stage.MASTER:
			if combo_result.get("name") == "master":
				stage = Stage.DONE
				GameState.tutorial_complete = true
	_update_prompt()

func _update_prompt() -> void:
	match stage:
		Stage.PUNCH:
			prompt_label.text = "Land a 3-hit Punch combo (P P P)"
		Stage.KICK:
			prompt_label.text = "Land a 3-hit Kick combo (K K K)"
		Stage.MASTER:
			prompt_label.text = "Execute the Master Combo (P K K P), then time a Charge to link the Ultimate"
		Stage.DONE:
			prompt_label.text = "Tutorial complete!"
