"""
Data models for Opus-Entries system
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class QualityTier(str, Enum):
    """Quality tiers for entries based on validation scores"""
    CELESTIAL = "CELESTIAL"
    ADAMANTINE = "ADAMANTINE"
    PLATINUM = "PLATINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"
    UNRANKED = "UNRANKED"


class Section(BaseModel):
    """A section within an entry"""
    name: str
    content: str
    word_count: int = 0

    def model_post_init(self, __context) -> None:
        """Calculate word count after initialization"""
        if not self.word_count:
            self.word_count = len(self.content.split())


class Entry(BaseModel):
    """Complete entry with all sections"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    topic: str
    sections: List[Section] = Field(default_factory=list)
    total_word_count: int = 0
    quality_tier: QualityTier = QualityTier.UNRANKED
    validation_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context) -> None:
        """Calculate total word count after initialization"""
        if not self.total_word_count:
            self.total_word_count = sum(section.word_count for section in self.sections)

    def get_section(self, name: str) -> Optional[Section]:
        """Get a section by name"""
        for section in self.sections:
            if section.name == name:
                return section
        return None

    def to_markdown(self) -> str:
        """Convert entry to markdown format"""
        lines = [
            f"# {self.topic}",
            "",
            f"**Quality Tier**: {self.quality_tier.value}",
            f"**Validation Score**: {self.validation_score:.2f}",
            f"**Total Words**: {self.total_word_count}",
            "",
            "---",
            ""
        ]
        
        for section in self.sections:
            lines.extend([
                f"## {section.name}",
                "",
                section.content,
                "",
                f"*({section.word_count} words)*",
                "",
                "---",
                ""
            ])
        
        return "\n".join(lines)


class ValidationResult(BaseModel):
    """Result of entry validation"""
    score: float
    quality_tier: QualityTier
    word_count_score: float
    theological_depth_score: float
    coherence_score: float
    section_balance_score: float
    orthodox_perspective_score: float
    feedback: List[str] = Field(default_factory=list)
