"""
Opus-Entries: Comprehensive Entry Generator
A system for generating detailed Orthodox Christian perspective entries.
"""

__version__ = "0.1.0"

from .generator import EntryGenerator
from .validator import EntryValidator
from .models import Entry, QualityTier

__all__ = ["EntryGenerator", "EntryValidator", "Entry", "QualityTier"]
