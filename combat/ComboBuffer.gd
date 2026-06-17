class_name ComboBuffer extends Node

const TOKEN_TTL := 0.6

var _tokens: Array = []   # [{ "t": "P"/"K", "time": float }]

func push(token: String) -> void:
	_tokens.append({ "t": token, "time": Time.get_ticks_msec() / 1000.0 })
	_prune()

func _prune() -> void:
	var now := Time.get_ticks_msec() / 1000.0
	_tokens = _tokens.filter(func(x): return now - x.time <= TOKEN_TTL)

func clear() -> void:
	_tokens.clear()

func current_sequence() -> Array:
	_prune()
	return _tokens.map(func(x): return x.t)

# Returns { name, step_index, mult, is_complete, on_final } or {} if no prefix matches.
func match_combo() -> Dictionary:
	var seq := current_sequence()
	if seq.is_empty(): return {}
	for combo_name in ComboDefinitions.COMBOS:
		var def = ComboDefinitions.COMBOS[combo_name]
		var target: Array = def.seq
		if seq.size() > target.size(): continue
		var ok := true
		for i in seq.size():
			if seq[i] != target[i]: ok = false; break
		if ok:
			var idx := seq.size() - 1
			return {
				"name": combo_name,
				"step_index": idx,
				"mult": def.mult[idx],
				"is_complete": seq.size() == target.size(),
				"on_final": def.get("on_final", ""),
			}
	return {}
