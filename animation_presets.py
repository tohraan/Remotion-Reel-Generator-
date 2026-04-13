"""
animation_presets.py - Royal Chic / Swiss Style Presets

Strict adherence to "Royal Chic" technical brief.
"""

import json
import sys
from pathlib import Path
from typing import Dict


class AnimationPresets:
    """Manage Swiss Style animation presets"""
    
    PRESETS = {
        "royal_chic": {
            "name": "Royal Chic",
            "description": "Swiss International Style. Helvetica. Monochromatic.",
            "camera": {
                "zoom": True,
                "zoom_intensity": 1.05, # "Slow, imperceptible zoom"
                "pan": False,
                "rotation": False,
            },
            "typography": {
                "style": "swiss_reveal",
                "font_family": "Helvetica Neue",
                "mix_weights": True, # Light + Bold mixing
            },
            "effects": {
                "white_void": True,
                "high_contrast": True,
            }
        },
        
        # Keeping a variation of the old ones just in case, but mapped to new style
        "default": {
            "name": "Royal Chic (Standard)",
            "description": "Default execution of the Royal Chic paradigm.",
            "camera": { "zoom": True, "zoom_intensity": 1.02 },
            "effects": { "white_void": True }
        }
    }
    
    def __init__(self, presets_file: str = "animation_presets.json"):
        self.presets_file = Path(presets_file)
    
    def get_preset(self, preset_id: str) -> Dict:
        """Get preset configuration"""
        # Force everything to Royal Chic logic for now as requested
        return self.PRESETS["royal_chic"]
        
    def export_for_remotion(self, preset_id: str, output_file: str = "animation_config.json"):
        preset = self.get_preset(preset_id)
        with open(output_file, 'w') as f:
            json.dump(preset, f, indent=2)
        return output_file

def main():
    print("Royal Chic System Active.")

if __name__ == "__main__":
    main()