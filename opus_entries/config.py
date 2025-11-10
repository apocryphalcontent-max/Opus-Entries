"""
Configuration management for Opus-Entries
"""
import json
import os
from typing import Dict, Any, List


class Config:
    """Configuration manager for the Opus-Entries system"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration from file"""
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        else:
            # Use default configuration
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "llm": {
                "default_model": "llama2",
                "base_url": "http://localhost:11434",
                "timeout": 300
            },
            "entry": {
                "min_word_count": 11000,
                "max_word_count": 14000,
                "sections": [
                    {"name": "Introduction", "min_words": 1500, "max_words": 2000},
                    {"name": "The Patristic Mind", "min_words": 2000, "max_words": 2500},
                    {"name": "Symphony of Clashes", "min_words": 2000, "max_words": 2500},
                    {"name": "Orthodox Affirmation", "min_words": 2000, "max_words": 2500},
                    {"name": "Synthesis", "min_words": 1500, "max_words": 2000},
                    {"name": "Conclusion", "min_words": 1500, "max_words": 2000}
                ]
            },
            "quality_tiers": {
                "CELESTIAL": {"min_score": 95, "max_score": 100},
                "ADAMANTINE": {"min_score": 90, "max_score": 94},
                "PLATINUM": {"min_score": 85, "max_score": 89},
                "GOLD": {"min_score": 80, "max_score": 84},
                "SILVER": {"min_score": 75, "max_score": 79},
                "BRONZE": {"min_score": 70, "max_score": 74}
            },
            "validation": {
                "weights": {
                    "word_count": 0.2,
                    "theological_depth": 0.3,
                    "coherence": 0.25,
                    "section_balance": 0.15,
                    "orthodox_perspective": 0.1
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section_configs(self) -> List[Dict[str, Any]]:
        """Get section configurations"""
        return self.get("entry.sections", [])
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.get("llm", {})
    
    def get_validation_weights(self) -> Dict[str, float]:
        """Get validation weights"""
        return self.get("validation.weights", {})
    
    def get_quality_tiers(self) -> Dict[str, Dict[str, int]]:
        """Get quality tier definitions"""
        return self.get("quality_tiers", {})
