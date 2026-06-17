class_name Boss extends CharacterBody2D

@export var ai_enabled: bool = true
@export var attack_range: float = 40.0

@onready var sm: BossStateMachine = $StateMachine
@onready var stats: StatsComponent = $StatsComponent
@onready var health: HealthComponent = $HealthComponent
@onready var hitbox: Hitbox = $Hitbox
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var stagger_timer: Timer = $StaggerTimer
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
	add_to_group("boss")
	hitbox.owner_stats = stats
	hurtbox.health = health
	hurtbox.stats = stats
	hurtbox.damage_received.connect(_on_damage_received)
	health.died.connect(_on_died)
	sm.setup(self)
	var player := get_tree().get_first_node_in_group("player")
	if player:
		player.master_final_landed.connect(_on_staggered)

func play_anim(anim_name: String) -> void:
	if animation_player.has_animation(anim_name):
		animation_player.play(anim_name)
	if animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(anim_name):
		animated_sprite.play(anim_name)

func is_player_in_attack_range() -> bool:
	var player := get_tree().get_first_node_in_group("player")
	return player != null and global_position.distance_to(player.global_position) <= attack_range

func _on_staggered(target) -> void:
	if target == self and not health.is_dead():
		sm.transition_to("BossStagger")

func _on_damage_received(_info: DamageInfo) -> void:
	if health.is_dead():
		return
	if sm.current is BossIdle or sm.current is BossAttack:
		sm.transition_to("BossHurt")

func _on_died() -> void:
	sm.transition_to("BossDead")
