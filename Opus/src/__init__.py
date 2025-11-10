"""
OPUS MAXIMUS - Theological Encyclopedia Generation System
===========================================================

A comprehensive system for generating high-quality Orthodox theological
encyclopedia entries with multi-tier validation and caching.
"""

__version__ = "2.0.0"
__author__ = "Opus Maximus Project"

from .opus_engine import OpusMaximusEngine, OpusConfig, GenerationResult
from .batch_processor import BatchProcessor, BatchStatistics
from .llm_interface import create_llm, LocalLLM, APILLM
from .validators import (
    TheologicalValidator,
    StyleValidator,
    PatristicCitationValidator,
    StructuralValidator,
    ValidationResult
)
from .checkpoint_manager import CheckpointManager
from .caching import MultiTierCache
from .prompts import PromptTemplates, SectionType
from .error_handling import (
    OpusError,
    GenerationError,
    ValidationError,
    LLMError,
    ConfigurationError
)

__all__ = [
    # Main classes
    'OpusMaximusEngine',
    'OpusConfig',
    'GenerationResult',
    'BatchProcessor',
    'BatchStatistics',

    # LLM
    'create_llm',
    'LocalLLM',
    'APILLM',

    # Validators
    'TheologicalValidator',
    'StyleValidator',
    'PatristicCitationValidator',
    'StructuralValidator',
    'ValidationResult',

    # Utilities
    'CheckpointManager',
    'MultiTierCache',
    'PromptTemplates',
    'SectionType',

    # Exceptions
    'OpusError',
    'GenerationError',
    'ValidationError',
    'LLMError',
    'ConfigurationError',
]
