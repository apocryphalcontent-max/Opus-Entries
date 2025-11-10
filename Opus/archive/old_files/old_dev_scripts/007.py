"""
FILE 7: CONFIGURATION SYSTEM
Centralized configuration management with environment overrides.
File 7 of 20: Configuration
Optimized for: Hardware Auto-Detection (Edit 16) | Aggressive Generation Limits (Edit 17)
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
import json
import logging
import torch # Needed for hardware detection

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Model inference configuration."""
    n_ctx: int = 8192      # Default, overridden by Edit 16 on high-spec systems
    n_batch: int = 512     # Default, overridden by Edit 16
    n_gpu_layers: int = -1 # All layers on GPU
    n_threads: int = 8     # Default, overridden by Edit 16
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1

@dataclass
class GenerationConfig:
    """Entry generation configuration (Edit 17 optimized defaults)."""
    max_section_attempts: int = 3      # Reduced from 5 for faster fail-retry cycles
    max_expansion_attempts: int = 2    # Reduced from 3
    min_word_count: int = 10000
    min_section_words: int = 1200
    max_section_words: int = 3000      # Increased from 2500 (VRAM permits larger sections)
    uniqueness_threshold: float = 0.75
    similarity_threshold: float = 0.80
    quality_threshold: float = 0.85

@dataclass
class PathsConfig:
    """Directory paths configuration."""
    output_dir: Path = Path("GENERATED_ENTRIES_MASTER")
    golden_dir: Path = Path("OPUS_MAXIMUS_INDIVIDUALIZED/Enhancement_Corpus")
    models_dir: Path = Path("models")
    chroma_path: Path = Path("research_db_chroma")
    faiss_index: Path = Path("uniqueness.faiss")
    telemetry_db: Path = Path("telemetry.db")
    cache_dir: Path = Path(".cache")
    logs_dir: Path = Path("logs")

@dataclass
class DatabaseConfig:
    """Database configuration."""
    chroma_collection: str = "patristic_corpus"
    faiss_metric: str = "cosine"
    sqlite_path: Path = Path("metadata.db")
    auto_backup: bool = True
    backup_interval_hours: int = 24

@dataclass
class ValidationConfig:
    """Validation configuration."""
    check_theology: bool = True
    check_style: bool = True
    check_plagiarism: bool = True
    check_citations: bool = True
    strict_mode: bool = False
    report_level: str = "detailed"

@dataclass
class Config:
    """Master configuration container."""
    paths: PathsConfig = field(default_factory=PathsConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    debug: bool = False
    log_level: str = "INFO"

    def __post_init__(self):
        """Initialize paths."""
        for attr_name in dir(self.paths):
            if not attr_name.startswith('_'):
                path = getattr(self.paths, attr_name)
                if isinstance(path, Path):
                    path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> 'Config':
        """Load from YAML file with hardware auto-optimization (Edit 16)."""
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            config = cls.from_dict(data)
        else:
            config = cls()

        # Edit 16: Auto-detect hardware and optimize
        try:
            if torch.cuda.is_available():
                # Check for ~16GB VRAM (allowing slight under-reporting by drivers)
                gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                if gpu_mem_gb >= 15.0:
                    logger.info(f"High-end GPU detected ({gpu_mem_gb:.1f}GB VRAM). Applying optimizations.")
                    # Override defaults if they weren't explicitly set higher in YAML
                    if config.model.n_ctx < 16384: config.model.n_ctx = 16384
                    if config.model.n_batch < 1024: config.model.n_batch = 1024
                    if config.model.n_threads < 16: config.model.n_threads = 16
        except Exception as e:
            logger.warning(f"Hardware auto-optimization failed: {e}")

        return config

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create from dict."""
        paths_data = data.get('paths', {})
        model_data = data.get('model', {})
        generation_data = data.get('generation', {})
        database_data = data.get('database', {})
        validation_data = data.get('validation', {})

        return cls(
            paths=PathsConfig(**paths_data),
            model=ModelConfig(**model_data),
            generation=GenerationConfig(**generation_data),
            database=DatabaseConfig(**database_data),
            validation=ValidationConfig(**validation_data),
            debug=data.get('debug', False),
            log_level=data.get('log_level', "INFO")
        )

    def save(self, path: str = "config.yaml"):
        """Save to YAML."""
        data = self.to_dict()
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "paths": self._dataclass_to_dict(self.paths),
            "model": self._dataclass_to_dict(self.model),
            "generation": self._dataclass_to_dict(self.generation),
            "database": self._dataclass_to_dict(self.database),
            "validation": self._dataclass_to_dict(self.validation),
            "debug": self.debug,
            "log_level": self.log_level
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def _dataclass_to_dict(dc):
        """Convert dataclass to dict with Path conversion."""
        result = {}
        for key, value in asdict(dc).items():
            if isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        if not self.paths.output_dir:
            errors.append("output_dir not specified")
        if self.model.n_ctx < 1024:
            errors.append("n_ctx too small (minimum 1024)")
        if self.generation.min_word_count < 5000:
            errors.append("min_word_count too low")
        
        if errors:
            logger.error("Configuration validation errors:")
            for error in errors:
                logger.error(f" - {error}")
            return False
        return True

# Global configuration instance
config: Config = Config.load()

# Environment variable overrides (simplified for brevity in full compilation)
if os.getenv("OPUS_DEBUG"): config.debug = os.getenv("OPUS_DEBUG").lower() == "true"
if os.getenv("OPUS_LOG_LEVEL"): config.log_level = os.getenv("OPUS_LOG_LEVEL")
if os.getenv("OPUS_MODEL_PATH"): config.paths.models_dir = Path(os.getenv("OPUS_MODEL_PATH"))

if not config.validate():
    logger.warning("Configuration validation failed but continuing...")