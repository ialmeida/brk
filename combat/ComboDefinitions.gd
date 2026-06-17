class_name ComboDefinitions extends RefCounted

const COMBOS := {
	"basic_punch": { "seq": ["P", "P", "P"],       "mult": [1.0, 1.2, 1.5] },
	"basic_kick":  { "seq": ["K", "K", "K"],       "mult": [1.0, 1.3, 1.7] },
	"master":      { "seq": ["P", "K", "K", "P"],  "mult": [1.0, 1.2, 1.4, 2.2],
					  "on_final": "stagger" },
}
