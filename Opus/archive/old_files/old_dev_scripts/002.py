# File 2: PROMPT TEMPLATES & ASSEMBLY
"""
OPUS MAXIMUS - COMPREHENSIVE PROMPT TEMPLATES
==============================================
Complete prompt template library for all generation contexts.
Includes section-specific guidance, quality gates, and linguistic mandates.
File 2 of 20: Prompt Templates
Optimized for: RAM caching of compiled regex patterns
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re

class SectionType(Enum):
    """Section types in entry structure."""
    STRATEGIC_ROLE = "I. Strategic Role"
    CLASSIFICATION = "II. Classification"
    PRIMARY_WORKS = "III. Primary Works"
    PATRISTIC_MIND = "IV. The Patristic Mind"
    SYMPHONY_CLASHES = "V. Symphony of Clashes"
    ORTHODOX_AFFIRMATION = "VI. Orthodox Affirmation"

@dataclass
class SectionTemplate:
    """Template for a section."""
    section_type: SectionType
    min_words: int
    max_words: int
    key_requirements: List[str]
    forbidden_phrases: List[str]
    required_elements: List[str]
    style_notes: str

class PromptTemplates:
    """Complete prompt template system."""
    def __init__(self):
        self.templates = self._load_templates()
        self.absolute_mandates = self._load_mandates()
        # Edit 9: Pre-compile regex patterns for validation (RAM speed optimization)
        # Utilizing 32GB RAM to keep these ready for instant validation checks
        self.compiled_patterns = {
            'not_but': re.compile(r'NOT\s+.*?\s+BUT\s+', re.IGNORECASE),
            # Made slightly more robust than original suggestion to catch 'St.' as well
            'patristic_citation': re.compile(r'(?:Saint|St\.)\s+\w+.*?(?:Homily|On|Against|Commentary)', re.IGNORECASE),
        }

    def _load_templates(self) -> Dict:
        """Load all prompt templates."""
        return {
            'blueprint_generation': self._blueprint_template(),
            'section_generation': self._section_generation_template(),
            'correction_prompt': self._correction_template(),
            'expansion_prompt': self._expansion_template(),
            'validation_prompt': self._validation_template(),
        }

    def _load_mandates(self) -> Dict:
        """Load absolute generation mandates."""
        return {
            'RULESET_ALPHA': {
                'description': 'Six-section structure with 10,000+ word minimum',
                'requirements': [
                    'Exactly 6 sections',
                    'Minimum 10,000 words total',
                    'Each section 1200-2500 words',
                    'Clear section headings with Roman numerals'
                ]
            },
            'RULESET_BETA': {
                'description': 'Formatting compliance',
                'requirements': [
                    'ALL paragraphs start with exactly 4 spaces (NO tabs)',
                    'NO em-dashes (—), use hyphens only for compounds',
                    'Numbers spelled out (one, two, three, etc.)',
                    'NO contractions (cannot, not can\'t)',
                    'Line length max 95 characters for readability'
                ]
            },
            'RULESET_GAMMA': {
                'description': 'Linguistic and Orthodox precision',
                'requirements': [
                    'Capitalize: Trinity, Father, Son, Holy Spirit, Eucharist, Liturgy',
                    'Use NOT...BUT structures for theological contrasts',
                    'Average sentence length: 25-35 words',
                    'Incorporate Greek/Syriac/Hebrew terms with transliteration',
                    'Apophatic language for divine essence'
                ]
            },
            'RULESET_DELTA': {
                'description': 'Content and doctrinal requirements',
                'requirements': [
                    'Patristic citations in every section',
                    'Theological density: minimum 3 key terms per 500 words',
                    'Eucharistic/eschatological culmination in Section VI',
                    'Dialectical tension in Section V',
                    'Theosis as unifying theme'
                ]
            }
        }

    def _blueprint_template(self) -> str:
        return """Generate a detailed blueprint for an Orthodox theological entry on {subject}.
Core Thesis: [Generate a profound, patristically-rooted thesis]
Include: patristic interlocutors, dialectical clashes, eucharistic seeds.
Ensure alignment with {tier} quality standards."""

    def _section_generation_template(self) -> str:
        return """Generate Section {section}: {description}.
Word count: {min_words}-{max_words}.
Incorporate: {requirements}.
Avoid: {forbidden}.
Use: {theological_terms}."""

    def _correction_template(self) -> str:
        return """Correct this content for theological accuracy and style compliance.
Issues: {violations}.
Revised version:"""

    def _expansion_template(self) -> str:
        return """Expand this section to meet word count and depth requirements.
Current: {current_words}. Target: {target_words}.
Add patristic depth and liturgical connections."""

    def _validation_template(self) -> str:
        return """Validate this content against Orthodox doctrine and style rules.
Flag: heresies, formatting errors, missing elements.
Report:"""

    def get_section_guidance(self, section_type: SectionType) -> str:
        """Get guidance for specific section."""
        guidance_map = {
            SectionType.ORTHODOX_AFFIRMATION: '''VI. ORTHODOX AFFIRMATION (2000-2500 words)
MANDATORY STRUCTURE:
1. PATRISTIC SYNTHESIS (800-1000 words):
   - Synthesize ALL previous sections
   - Show how {subject} integrates into Orthodox whole
   - Reference at least 5 key Fathers across entry
   - Demonstrate theandric unity
2. EUCHARISTIC CULMINATION (600-800 words):
   - THE PHRASE "AND NOW, in this Liturgy, at this Altar..." MUST appear somewhere
   - Show how {subject} finds its fulfillment in the Eucharist
   - Reference the Body and Blood of Christ
   - Connect to Church as theandric organism
   - Show liturgical actualization
   - Include at least one reference to the Liturgy or Sacramental theology
3. ESCHATOLOGICAL CONSUMMATION (400-500 words):
   - How does {subject} culminate in the Age to Come?
   - What does {subject} reveal about God's final purpose?
   - Connection to deification and theosis
   - Hope and fulfillment in Christ
4. DOXOLOGICAL CASCADE (400-600 words):
   - ONE OVERWHELMINGLY LONG SENTENCE (100+ words)
   - Use doxological language: "From...to...", "In Him...through Him...for Him..."
   - Build toward climactic affirmation of divine glory
   - End with "Glory to God for all things" or similar
   - This sentence should be a poetic-theological summit

EXAMPLE DOXOLOGICAL ENDING:
"From the first silence before creation, through the Logos-word spoken in every age...
AND NOW in this present moment at this altar where heaven and earth are joined,
YET beyond all earthly liturgies in the glory that awaits,
TO the Father and Son and Holy Spirit, the three-fold radiance of uncreated light
FROM generation to generation and forever and ever, Amen."

REQUIREMENTS:
- MUST include prayer
- MUST include exact phrase about altar/liturgy
- MUST include 100+ word doxological sentence
- Use grammatically complex periodic sentences
- Invoke entire Trinity
- Connect to personhood and deification
- Sense of cosmic culmination
- Eschatological hope
- This is the liturgical-theological climax of the entire entry'''
        }
        return guidance_map.get(section_type, "")

    def get_theological_terms_string(self) -> str:
        """Get formatted list of theological terms."""
        terms = [
            'theosis', 'logos', 'nous', 'kardia', 'pneuma', 'ousia', 'hypostasis',
            'energeia', 'theandric', 'perichoresis', 'theophania', 'apophatic', 'cataphatic',
            'metanoia', 'synergy', 'divinization', 'incarnation', 'theotokos', 'atonement'
        ]
        return ', '.join(terms)

    def get_absolute_mandates_string(self) -> str:
        """Get formatted absolute mandates."""
        output = []
        for ruleset, data in self.absolute_mandates.items():
            output.append(f"{ruleset}: {data['description']}")
            for req in data['requirements']:
                output.append(f" • {req}")
        return "\n".join(output)

# Global instance
TEMPLATES = PromptTemplates()