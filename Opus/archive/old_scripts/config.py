"""
OPUS MAXIMUS - CENTRALIZED CONFIGURATION
==========================================
Loads settings from config.yaml using Pydantic for type safety and validation.

Usage:
    from config import settings

    output_dir = settings.directories.output
    min_word_count = settings.generation.min_word_count

Author: Automated System for Orthodox Apologetics
Date: 2025-11-07
Version: GPU-NATIVE-V2
"""

from pathlib import Path
from typing import List, Dict, Tuple, Type
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
import yaml
import sys


# ============================================================================
# NESTED CONFIGURATION MODELS
# ============================================================================

class DirectoriesConfig(BaseModel):
    """Directory paths"""
    output: str
    golden: str
    patristics_library: str
    models: str


class DatabaseConfig(BaseModel):
    """Database file paths"""
    chroma_path: str
    faiss_index: str
    entry_names: str
    phrase_registry: str
    telemetry: str
    knowledge_graph: str


class GenerationConfig(BaseModel):
    """Generation parameters"""
    tier_priority: List[str]
    min_word_count: int
    section_word_targets: List[int]
    min_section_word_counts: List[int]
    max_section_attempts: int
    max_expansion_attempts: int
    max_fact_check_attempts: int
    base_temperatures: Dict[str, float]


class LLMConfig(BaseModel):
    """LLM inference parameters"""
    default_n_ctx: int
    min_n_ctx: int
    max_n_ctx: int
    default_n_gpu_layers: int
    default_max_tokens: int
    validation_max_tokens: int
    stop_tokens: List[str]
    use_tiered_models: bool
    validator_n_gpu_layers: int
    validator_n_ctx: int


class SemanticSearchConfig(BaseModel):
    """Semantic search parameters"""
    patristic_limit: int
    biblical_limit: int
    apocryphal_limit: int
    min_similarity: float
    cross_reference_limit: int


class UniquenessConfig(BaseModel):
    """Uniqueness checking thresholds"""
    similarity_threshold: float
    repeated_phrase_threshold: int
    fuzzy_match_threshold: int
    fuzzy_match_limit: int
    faiss_save_interval: int


class CheckpointingConfig(BaseModel):
    """Checkpointing settings"""
    enabled: bool
    save_after_each_section: bool
    checkpoint_dir: str


class ResourcesConfig(BaseModel):
    """Resource monitoring thresholds"""
    vram_critical_threshold: float
    vram_warning_threshold: float
    ram_critical_threshold: float
    ram_warning_threshold: float
    monitor_interval: int
    enable_degradation: bool


class TelemetryConfig(BaseModel):
    """Telemetry and logging settings"""
    enabled: bool
    log_level: str
    structured_logging: bool
    track_section_times: bool
    track_vram_usage: bool
    track_validation_failures: bool
    track_llm_calls: bool
    max_log_age_days: int


class QualityConfig(BaseModel):
    """Quality assurance settings"""
    verify_citations: bool
    citation_similarity_threshold: float
    check_consistency: bool
    consistency_check_limit: int
    run_benchmarks: bool
    benchmark_sample_size: int


class AdvancedConfig(BaseModel):
    """Advanced features"""
    blueprint_library_enabled: bool
    blueprint_library_path: str
    failure_detection_enabled: bool
    failure_history_limit: int
    knowledge_graph_enabled: bool
    multi_gpu_enabled: bool
    num_gpus: int


class LoggingConfig(BaseModel):
    """Logging configuration"""
    console_level: str
    file_level: str
    json_logging: bool
    log_file: str
    telemetry_file: str


# ============================================================================
# CUSTOM YAML SETTINGS SOURCE
# ============================================================================

class YamlSettingsSource(PydanticBaseSettingsSource):
    """
    Custom settings source that loads from YAML file
    """

    def __init__(self, settings_cls: Type[BaseSettings], yaml_file: str = 'config.yaml'):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def get_field_value(self, field_name: str) -> Tuple[any, str, bool]:
        # Not used for dict-based loading
        return None, field_name, False

    def __call__(self) -> Dict[str, any]:
        """
        Load and return YAML data as dict
        """
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data if data else {}
        except FileNotFoundError:
            return {}


# ============================================================================
# MAIN SETTINGS CLASS
# ============================================================================

class Settings(BaseSettings):
    """
    Main configuration class that loads from config.yaml

    All settings are validated using Pydantic models for type safety.
    """

    model_config = SettingsConfigDict(
        extra='allow'  # Allow extra fields for future expansion
    )

    # Configuration sections
    directories: DirectoriesConfig
    database: DatabaseConfig
    generation: GenerationConfig
    llm: LLMConfig
    semantic_search: SemanticSearchConfig
    uniqueness: UniquenessConfig
    checkpointing: CheckpointingConfig
    resources: ResourcesConfig
    telemetry: TelemetryConfig
    quality: QualityConfig
    advanced: AdvancedConfig
    category_dirs: Dict[str, str]
    logging: LoggingConfig

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize settings sources to include YAML file
        """
        return (
            init_settings,
            YamlSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @classmethod
    def load_from_yaml(cls, yaml_path: str = 'config.yaml') -> 'Settings':
        """
        Load settings from YAML file manually (fallback method)

        Args:
            yaml_path: Path to YAML config file

        Returns:
            Settings instance
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        return cls(**config_dict)

    def get_output_path(self, category: str) -> Path:
        """
        Get full output path for a given category

        Args:
            category: Entry category (e.g., 'Biblical', 'Theology')

        Returns:
            Full Path object
        """
        base_dir = Path(self.directories.output)
        subdir = self.category_dirs.get(category, 'Miscellaneous')
        return base_dir / subdir

    def get_checkpoint_path(self, subject: str, category: str) -> Path:
        """
        Get checkpoint file path for a subject

        Args:
            subject: Entry subject
            category: Entry category

        Returns:
            Path to checkpoint file
        """
        subject_filename = subject.lower().replace(' ', '_').replace(':', '')
        output_path = self.get_output_path(category)
        checkpoint_dir = output_path / self.checkpointing.checkpoint_dir
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return checkpoint_dir / f"{subject_filename}.state.json"

    def get_database_path(self, db_name: str) -> Path:
        """
        Get full path to a database file

        Args:
            db_name: Database name from config (e.g., 'chroma_path')

        Returns:
            Full Path object
        """
        db_path = getattr(self.database, db_name)
        return Path(db_path)

    def validate_paths(self) -> List[str]:
        """
        Validate that all critical paths exist

        Returns:
            List of missing paths
        """
        missing = []

        # Check golden directory
        if not Path(self.directories.golden).exists():
            missing.append(f"Golden directory: {self.directories.golden}")

        # Check ChromaDB
        if not Path(self.database.chroma_path).exists():
            missing.append(f"ChromaDB: {self.database.chroma_path}")

        # Check patristics library
        if not Path(self.directories.patristics_library).exists():
            missing.append(f"Patristics library: {self.directories.patristics_library}")

        return missing


# ============================================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================================

def load_settings() -> Settings:
    """
    Load settings from config.yaml with error handling

    Returns:
        Settings instance
    """
    try:
        # Use pydantic-settings with custom YAML source
        return Settings()
    except Exception as e:
        print(f"Warning: Could not load config.yaml using pydantic-settings: {e}")
        print("Attempting manual YAML load...")
        try:
            return Settings.load_from_yaml('config.yaml')
        except Exception as e2:
            print(f"FATAL: Could not load config.yaml: {e2}")
            raise


# Load settings at module import
settings = load_settings()


# ============================================================================
# VALIDATION ON IMPORT
# ============================================================================

if __name__ != "__main__":
    # Validate critical paths on import
    missing_paths = settings.validate_paths()
    if missing_paths:
        import warnings
        warnings.warn(
            f"Missing critical paths:\n" + "\n".join(f"  - {p}" for p in missing_paths)
        )


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    """Test configuration loading"""
    import json

    print("=" * 80)
    print("OPUS MAXIMUS - CONFIGURATION TEST")
    print("=" * 80)

    print("\n[OK] Configuration loaded successfully\n")

    print("Output Directory:", settings.directories.output)
    print("Golden Directory:", settings.directories.golden)
    print("Min Word Count:", settings.generation.min_word_count)
    print("Tier Priority:", settings.generation.tier_priority)
    print("Default Context Window:", settings.llm.default_n_ctx)
    print("Checkpointing Enabled:", settings.checkpointing.enabled)
    print("Telemetry Enabled:", settings.telemetry.enabled)

    print("\n" + "=" * 80)
    print("PATH VALIDATION")
    print("=" * 80)

    missing = settings.validate_paths()
    if missing:
        print("\n[WARNING] Missing paths:")
        for path in missing:
            print(f"  - {path}")
    else:
        print("\n[OK] All critical paths exist")

    print("\n" + "=" * 80)
    print("EXAMPLE USAGE")
    print("=" * 80)

    print("\nFrom code:")
    print("  from config import settings")
    print("  output_dir = settings.directories.output")
    print("  min_words = settings.generation.min_word_count")

    print("\n" + "=" * 80)
