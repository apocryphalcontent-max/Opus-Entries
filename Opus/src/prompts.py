"""
OPUS MAXIMUS - Prompt Template System
======================================
Sophisticated prompts for each generation phase.
"""

from typing import Dict, Any, Optional
from enum import Enum


# ============================================================================
# SECTION TYPES
# ============================================================================

class SectionType(Enum):
    """Six required entry sections"""
    STRATEGIC_ROLE = "strategic_role"
    CLASSIFICATION = "classification"
    PRIMARY_WORKS = "primary_works"
    PATRISTIC_MIND = "patristic_mind"
    SYMPHONY_CLASHES = "symphony_clashes"
    ORTHODOX_AFFIRMATION = "orthodox_affirmation"


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

class PromptTemplates:
    """Comprehensive prompt templates for all generation phases"""

    @staticmethod
    def blueprint_prompt(
        subject: str,
        tier: str,
        category: str
    ) -> str:
        """
        Generate blueprint/outline prompt.

        Args:
            subject: Entry subject
            tier: Priority tier
            category: Subject category

        Returns:
            Blueprint generation prompt
        """
        return f"""You are a world-class Orthodox theologian tasked with creating a comprehensive theological encyclopedia entry on "{subject}".

SUBJECT: {subject}
TIER: {tier}
CATEGORY: {category}

Your task is to create a detailed BLUEPRINT/OUTLINE for this entry. This blueprint will guide the full entry generation.

The entry must follow this MANDATORY six-section structure:

I. STRATEGIC ROLE (1200-1800 words)
   - Define the concept's place in Orthodox systematic theology
   - Explain its unique contribution to the theological ecosystem
   - Connect to broader soteriological and ecclesiological themes

II. CLASSIFICATION (1200-1800 words)
   - Formal theological categorization
   - Historical development through patristic, byzantine, and modern periods
   - Relationship to other theological concepts

III. PRIMARY WORKS (1500-2500 words)
   - Magisterial patristic treatments (Saint Athanasius, Basil, Gregory, Maximus, etc.)
   - Key biblical foundations (minimum 20 scriptural references)
   - Liturgical expressions and hymnographic witness

IV. THE PATRISTIC MIND (1800-2500 words)
   - Deep dive into patristic anthropology and soteriology
   - Synthesis of Eastern fathers' perspectives
   - Contrast with Western theological developments
   - Heavy citation density (aim for 15+ patristic citations)

V. SYMPHONY OF CLASHES (2000-3000 words)
   - Historical heresies addressed (Arianism, Nestorianism, Pelagianism, etc.)
   - Conciliar responses (Nicaea, Constantinople, Chalcedon, etc.)
   - Contemporary challenges and apologetic applications
   - Detailed theological argumentation

VI. ORTHODOX AFFIRMATION (2000-2500 words)
   - Synthesis of orthodox teaching
   - Liturgical grounding ("AND NOW, in the Divine Liturgy...")
   - Practical spiritual applications
   - Doxological conclusion ("To the Father, Son, and Holy Spirit...")

For each section, provide:
1. CORE THESIS: What is the main argument?
2. UNIQUE ANGLE: What makes this treatment distinctive?
3. KEY PATRISTIC VOICES: Which fathers to emphasize?
4. HERETICAL CONTRASTS: What errors to refute?
5. RHETORICAL STRATEGY: How to structure the argument?

Create a comprehensive blueprint now. Be specific about theological arguments, patristic citations to include, and rhetorical flow."""

    @staticmethod
    def section_prompt(
        subject: str,
        section_type: SectionType,
        blueprint: str,
        min_words: int,
        max_words: int,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate section-specific prompt.

        Args:
            subject: Entry subject
            section_type: Which section to generate
            blueprint: Overall entry blueprint
            min_words: Minimum word count
            max_words: Maximum word count
            context: Additional context (previous sections, etc.)

        Returns:
            Section generation prompt
        """
        section_name = section_type.value.replace('_', ' ').title()

        # Section-specific instructions
        section_instructions = {
            SectionType.STRATEGIC_ROLE: """
This section establishes the theological landscape and stakes. You must:
- Define the concept with precision worthy of a doctoral dissertation
- Situate it within Orthodox systematic theology's architecture
- Use sophisticated vocabulary (average word length ≥5.2 characters)
- Employ complex sentence structures (average 25-35 words/sentence)
- Include 3-5 patristic citations
- Use rhetorical devices: NOT...BUT contrasts, anaphora, triadic structures
- Avoid simple words and contractions
- Capitalize all sacred terms (God, Christ, Church, Scripture, Trinity)
""",
            SectionType.CLASSIFICATION: """
This section provides rigorous categorization and historical development:
- Formal theological taxonomy
- Historical trajectory (patristic → byzantine → modern)
- Relationship to cognate concepts
- 4-6 patristic citations establishing historical witness
- Technical Greek/Latin terminology with English equivalents
- Sophisticated sentence architecture with subordinate clauses
- Reference at least one ecumenical council
""",
            SectionType.PRIMARY_WORKS: """
This section dives into the textual foundations:
- Comprehensive survey of patristic treatments
- 6-8 major patristic citations with specific work titles
- 20+ biblical references (book, chapter, verse)
- Analysis of key liturgical texts
- Avoid pedestrian language; use erudite vocabulary
- Long, flowing sentences that build theological arguments
- Connect Scripture → Fathers → Liturgy in seamless synthesis
""",
            SectionType.PATRISTIC_MIND: """
This is the theological heart of the entry:
- Profound synthesis of Eastern patristic thought
- 12-15 patristic citations from diverse fathers
- Contrast with Western theological trajectories
- Deep exploration of anthropological and soteriological implications
- Use apophatic-cataphatic balance (40% apophatic, 60% cataphatic)
- Include at least 2 "NOT...BUT" rhetorical structures
- Minimum 8 Greek theological terms (with translations)
- Several epic sentences (100+ words) with layered argumentation
""",
            SectionType.SYMPHONY_CLASHES: """
This section showcases theological precision through contrast:
- Detailed refutation of at least 3 major heresies
- Reference specific ecumenical councils and their canons
- 8-10 patristic citations showing orthodox alternative
- Robust apologetic argumentation
- Use polysyndeton (repeated "and") for building momentum
- Complex rhetorical architecture
- Show how heresies fail soteriologically and christologically
- Contemporary applications and warnings
""",
            SectionType.ORTHODOX_AFFIRMATION: """
This is the doxological summit:
- Synthesize all previous themes into unified orthodox teaching
- Begin with liturgical grounding: "AND NOW, in the Divine Liturgy..."
- Describe how concept manifests in worship
- Provide practical spiritual counsel for believers
- 6-8 final patristic citations as capstone
- End with majestic doxology (150+ words, rising to praise)
- Final sentence MUST be doxological formula ending in "Amen"
- Capitalize all divine titles (Father, Son, Holy Spirit, Trinity, etc.)
"""
        }

        base_prompt = f"""You are writing Section {section_type.value.split('_')[0]} of a theological encyclopedia entry on "{subject}".

SECTION: {section_name}
TARGET LENGTH: {min_words}-{max_words} words

=== BLUEPRINT CONTEXT ===
{blueprint}

=== SECTION-SPECIFIC REQUIREMENTS ===
{section_instructions.get(section_type, "")}

=== MANDATORY STYLE REQUIREMENTS (ALPHA, BETA, GAMMA, DELTA) ===

ALPHA (Vocabulary):
- Average word length: ≥5.2 characters
- Simple word ratio: ≤35%
- Use theological terminology: essence, hypostasis, theosis, economia, kenosis
- Prefer: "ascetical" over "spiritual", "soteriological" over "salvific"

BETA (Sentence Structure):
- Average sentence length: 25-35 words
- Include at least 2 epic sentences (100+ words each)
- Use subordinate clauses, participial phrases, appositive structures
- Vary sentence length: mix short (10-15), medium (20-40), long (50+)

GAMMA (Theological Depth):
- Citation density: 2 patristic citations per 500 words
- Biblical references: 3 per 500 words
- Greek/Latin terms: 3 per 500 words (with English)
- Technical precision: always use conciliar terminology

DELTA (Formal Tone):
- NO contractions (it's → it is; don't → do not)
- NO informal words (stuff, things, lots, guys, okay)
- Capitalize: God, Christ, Trinity, Holy Spirit, Church, Scripture, Liturgy
- Capitalize specific saints: Saint Athanasius, Saint Basil
- Use formal connectives: moreover, furthermore, nevertheless, notwithstanding

=== EXAMPLES OF TARGET QUALITY ===

GOOD SENTENCE EXAMPLE:
"Saint Maximus the Confessor, in his Ambigua, elucidates this mystery with characteristic precision, demonstrating how the divine energies (ἐνέργειαι) penetrate creation without compromising the absolute transcendence of the divine essence (οὐσία), thereby preserving the apophatic foundation even as cataphatic theology proclaims God's knowability through His uncreated operations in the world."

NOT THIS:
"Maximus the Confessor talks about how God's energies work in creation but His essence stays unknown."

RHETORICAL DEVICES TO EMPLOY:
- NOT...BUT: "This is NOT merely intellectual assent, BUT existential transformation..."
- Anaphora: "The Fathers teach... The Fathers demonstrate... The Fathers proclaim..."
- Triadic: "...through repentance, through ascesis, through unceasing prayer..."
- Polysyndeton: "...and the prophets proclaimed it, and the apostles witnessed it, and the martyrs sealed it with their blood..."

=== PREVIOUS CONTEXT ===
{context.get('previous_sections', 'This is the first section.')}

Now generate Section {section_name} following ALL requirements above. The output must be {min_words}-{max_words} words of sophisticated theological prose."""

        return base_prompt

    @staticmethod
    def correction_prompt(
        original_prompt: str,
        generated_text: str,
        errors: list[str]
    ) -> str:
        """
        Generate correction prompt for failed validation.

        Args:
            original_prompt: Original generation prompt
            generated_text: Text that failed validation
            errors: List of validation errors

        Returns:
            Correction prompt
        """
        return f"""The following text failed validation. Please regenerate with corrections.

=== ORIGINAL PROMPT ===
{original_prompt}

=== GENERATED TEXT (with errors) ===
{generated_text}

=== VALIDATION ERRORS ===
{chr(10).join('- ' + error for error in errors)}

=== CORRECTION INSTRUCTIONS ===
Fix ALL validation errors listed above while maintaining the theological content and argument structure.

Specifically:
1. If word count is too short/long, adjust accordingly
2. If patristic citations are insufficient, add more
3. If sentence structure is too simple, make more complex
4. If vocabulary is too simple, use more sophisticated terms
5. If contractions found, expand them
6. If informal words found, replace with formal equivalents
7. If capitalization errors, fix them

Generate the CORRECTED version now. It must pass all validation requirements."""

    @staticmethod
    def enhancement_prompt(
        current_text: str,
        target_improvements: Dict[str, Any]
    ) -> str:
        """
        Generate enhancement prompt for progressive improvement.

        Args:
            current_text: Current text to enhance
            target_improvements: Specific areas to improve

        Returns:
            Enhancement prompt
        """
        improvements_text = "\n".join(
            f"- {key}: {value}" for key, value in target_improvements.items()
        )

        return f"""Enhance the following theological text to achieve higher quality.

=== CURRENT TEXT ===
{current_text}

=== TARGET IMPROVEMENTS ===
{improvements_text}

=== ENHANCEMENT GUIDELINES ===
1. Preserve all theological content and arguments
2. Maintain structural flow
3. Elevate vocabulary sophistication
4. Add rhetorical devices (NOT...BUT, anaphora, etc.)
5. Deepen patristic engagement
6. Increase sentence complexity
7. Ensure formal tone throughout

Generate the ENHANCED version now."""

    @staticmethod
    def assembly_prompt(
        subject: str,
        sections: Dict[str, str]
    ) -> str:
        """
        Generate prompt for final assembly/polish.

        Args:
            subject: Entry subject
            sections: Dictionary of section content

        Returns:
            Assembly prompt
        """
        sections_text = "\n\n".join(
            f"=== {name.upper()} ===\n{content}"
            for name, content in sections.items()
        )

        return f"""You have generated six sections for the encyclopedia entry on "{subject}".
Now perform final assembly and polish.

=== ALL SECTIONS ===
{sections_text}

=== ASSEMBLY TASKS ===
1. Ensure smooth transitions between sections
2. Verify no contradictions or redundancy
3. Confirm doxological ending is majestic
4. Check all citations are properly formatted
5. Verify consistent terminology throughout
6. Ensure total word count is 10,000-15,000
7. Confirm all six sections are present and properly labeled

Generate the final polished entry now, with all sections integrated seamlessly."""


# ============================================================================
# PROMPT UTILITIES
# ============================================================================

def truncate_for_context(text: str, max_chars: int = 2000) -> str:
    """
    Truncate text to fit in context window.

    Args:
        text: Text to truncate
        max_chars: Maximum characters

    Returns:
        Truncated text with ellipsis
    """
    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[... truncated ...]"


def count_prompt_tokens(prompt: str) -> int:
    """
    Estimate token count for prompt.

    Args:
        prompt: Prompt text

    Returns:
        Estimated token count (~4 chars per token)
    """
    return len(prompt) // 4
