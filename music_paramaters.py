import numpy as np
import pandas as pd

class MusicParameterProcessor:
    def __init__(self):
        self.mood_theory_mappings = self.create_music_theory_mappings()
    
    def create_music_theory_mappings(self):
        """Detailed music theory mappings"""
        return {
            "happy": {
                "scales": ["major", "mixolydian", "lydian"],
                "chord_progressions": [["I", "V", "vi", "IV"], ["I", "vi", "IV", "V"]],
                "rhythmic_patterns": ["straight", "swing"],
                "typical_keys": ["C", "G", "D", "A", "E"]
            },
            "sad": {
                "scales": ["natural_minor", "harmonic_minor", "dorian"],
                "chord_progressions": [["i", "VII", "VI", "VII"], ["i", "iv", "V", "i"]],
                "rhythmic_patterns": ["straight", "rubato"],
                "typical_keys": ["Am", "Em", "Bm", "F#m"]
            },
            "calm": {
                "scales": ["major", "pentatonic", "aeolian"],
                "chord_progressions": [["I", "vi", "IV", "V"], ["I", "V", "vi", "iii"]],
                "rhythmic_patterns": ["legato", "sustained"],
                "typical_keys": ["C", "F", "Bb", "Eb"]
            },
            "energetic": {
                "scales": ["major", "minor", "blues"],
                "chord_progressions": [["I", "IV", "V", "I"], ["i", "VII", "VI", "VII"]],
                "rhythmic_patterns": ["staccato", "syncopated"],
                "typical_keys": ["E", "A", "D", "G"]
            },
            "mysterious": {
                "scales": ["harmonic_minor", "phrygian", "locrian"],
                "chord_progressions": [["i", "II", "i", "VII"], ["i", "bII", "bVII", "i"]],
                "rhythmic_patterns": ["irregular", "sparse"],
                "typical_keys": ["Dm", "Gm", "Cm", "F#m"]
            },
            "romantic": {
                "scales": ["major", "dorian", "natural_minor"],
                "chord_progressions": [["I", "vi", "ii", "V"], ["i", "VI", "III", "VII"]],
                "rhythmic_patterns": ["waltz", "ballad"],
                "typical_keys": ["F", "Bb", "Eb", "Ab"]
            }
        }
    
    def enhance_parameters(self, base_params):
        """Add detailed music theory parameters"""
        mood = base_params["mood_category"]
        mapping = self.mood_theory_mappings.get(mood, self.mood_theory_mappings["calm"])
        
        enhanced = base_params.copy()
        enhanced.update({
            "chord_progression": np.random.choice(len(mapping["chord_progressions"])),
            "scale_type": np.random.choice(mapping["scales"]),
            "rhythmic_pattern": np.random.choice(mapping["rhythmic_patterns"]),
            "suggested_key": np.random.choice(mapping["typical_keys"]),
            "dynamics": self.map_energy_to_dynamics(base_params["energy_level"]),
            "texture": self.map_energy_to_texture(base_params["energy_level"])
        })
        
        # Get actual chord progression
        enhanced["chord_progression"] = mapping["chord_progressions"][enhanced["chord_progression"]]
        
        return enhanced
    
    def map_energy_to_dynamics(self, energy):
        if energy <= 3: return "pp"
        elif energy <= 5: return "mp"
        elif energy <= 7: return "mf"
        else: return "f"
    
    def map_energy_to_texture(self, energy):
        if energy <= 4: return "monophonic"
        elif energy <= 7: return "homophonic"
        else: return "polyphonic"