extends Node

signal skill_leveled(skill_id: String, level: int)

const LEVEL_UP_THRESHOLD := 5

var _usage_counts := {}
var _levels := {}

func record_use(skill_id: String, landed: bool) -> void:
	if skill_id.is_empty() or not landed:
		return
	_usage_counts[skill_id] = _usage_counts.get(skill_id, 0) + 1
	_levels[skill_id] = _levels.get(skill_id, 0)
	var new_level: int = _usage_counts[skill_id] / LEVEL_UP_THRESHOLD
	if new_level > _levels[skill_id]:
		_levels[skill_id] = new_level
		skill_leveled.emit(skill_id, new_level)

func get_usage(skill_id: String) -> int:
	return _usage_counts.get(skill_id, 0)

func get_level(skill_id: String) -> int:
	return _levels.get(skill_id, 0)
