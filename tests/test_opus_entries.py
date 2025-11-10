"""
Tests for the Opus-Entries system
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opus_entries.models import Entry, Section, QualityTier
from opus_entries.generator import EntryGenerator
from opus_entries.validator import EntryValidator
from opus_entries.config import Config


def test_section_model():
    """Test Section model"""
    section = Section(name="Introduction", content="This is a test introduction with several words.")
    assert section.name == "Introduction"
    assert section.word_count == 8
    print("✓ Section model test passed")


def test_entry_model():
    """Test Entry model"""
    sections = [
        Section(name="Introduction", content="Test introduction content here."),
        Section(name="Conclusion", content="Test conclusion content here.")
    ]
    entry = Entry(topic="Test Topic", sections=sections)
    
    assert entry.topic == "Test Topic"
    assert len(entry.sections) == 2
    assert entry.total_word_count == 8
    assert entry.quality_tier == QualityTier.UNRANKED
    print("✓ Entry model test passed")


def test_config():
    """Test Config loading"""
    config = Config("config.json")
    
    assert config.get("llm.default_model") == "llama2"
    assert config.get("entry.min_word_count") == 11000
    assert config.get("entry.max_word_count") == 14000
    
    sections = config.get_section_configs()
    assert len(sections) == 6
    assert sections[0]["name"] == "Introduction"
    assert sections[1]["name"] == "The Patristic Mind"
    
    print("✓ Config test passed")


def test_validator():
    """Test EntryValidator"""
    validator = EntryValidator()
    
    # Create a test entry with proper sections
    sections = [
        Section(name="Introduction", content=" ".join(["word"] * 1800)),
        Section(name="The Patristic Mind", content=" ".join(["Patristic"] * 2200)),
        Section(name="Symphony of Clashes", content=" ".join(["dialectic"] * 2100)),
        Section(name="Orthodox Affirmation", content=" ".join(["Orthodox"] * 2200)),
        Section(name="Synthesis", content=" ".join(["synthesis"] * 1700)),
        Section(name="Conclusion", content=" ".join(["conclusion"] * 1600))
    ]
    
    entry = Entry(topic="Test Topic", sections=sections)
    
    result = validator.validate(entry)
    
    assert result.score > 0
    assert result.quality_tier in QualityTier
    assert 0 <= result.word_count_score <= 100
    assert 0 <= result.theological_depth_score <= 100
    assert 0 <= result.coherence_score <= 100
    assert 0 <= result.section_balance_score <= 100
    assert 0 <= result.orthodox_perspective_score <= 100
    
    print(f"✓ Validator test passed (Score: {result.score:.2f}, Tier: {result.quality_tier.value})")


def test_generator():
    """Test EntryGenerator"""
    generator = EntryGenerator()
    
    # Generate a short entry (will use fallback since LLM likely not available)
    entry = generator.generate("Test Topic")
    
    assert entry.topic == "Test Topic"
    assert len(entry.sections) == 6
    assert all(section.content for section in entry.sections)
    
    print(f"✓ Generator test passed (Generated {entry.total_word_count} words)")


def test_markdown_output():
    """Test markdown output generation"""
    sections = [
        Section(name="Introduction", content="Test introduction."),
        Section(name="Conclusion", content="Test conclusion.")
    ]
    entry = Entry(topic="Test Topic", sections=sections)
    entry.quality_tier = QualityTier.GOLD
    entry.validation_score = 82.5
    
    markdown = entry.to_markdown()
    
    assert "# Test Topic" in markdown
    assert "**Quality Tier**: GOLD" in markdown
    assert "**Validation Score**: 82.50" in markdown
    assert "## Introduction" in markdown
    assert "## Conclusion" in markdown
    
    print("✓ Markdown output test passed")


def run_all_tests():
    """Run all tests"""
    print("Running Opus-Entries Tests\n" + "="*50)
    
    test_section_model()
    test_entry_model()
    test_config()
    test_validator()
    test_generator()
    test_markdown_output()
    
    print("="*50)
    print("All tests passed! ✓")


if __name__ == "__main__":
    run_all_tests()
