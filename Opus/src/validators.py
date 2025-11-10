"""
OPUS MAXIMUS - Validation Framework
====================================
Multi-dimensional validation for theological content quality.

Validators:
- TheologicalValidator: Heresy detection, council compliance
- StyleValidator: ALPHA, BETA, GAMMA, DELTA rulesets
- PatristicCitationValidator: Citation verification
- StructuralValidator: Entry structure requirements
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter
from enum import Enum

from .error_handling import ValidationError

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ValidationResult:
    """Result of validation check"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0

    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)

    def add_metric(self, key: str, value: Any):
        """Add metric"""
        self.metrics[key] = value


class HeresyType(Enum):
    """Types of heresies to detect"""
    ARIANISM = "Arianism"
    NESTORIANISM = "Nestorianism"
    MONOPHYSITISM = "Monophysitism"
    PELAGIANISM = "Pelagianism"
    SEMI_PELAGIANISM = "Semi-Pelagianism"
    MODALISM = "Modalism"
    SUBORDINATIONISM = "Subordinationism"
    DOCETISM = "Docetism"
    GNOSTICISM = "Gnosticism"
    ICONOCLASM = "Iconoclasm"
    MONOTHELITISM = "Monothelitism"


# ============================================================================
# THEOLOGICAL VALIDATOR
# ============================================================================

class TheologicalValidator:
    """
    Validate theological orthodoxy.

    Checks:
    - Heresy detection (11 major heresies)
    - Nicene Creed compliance
    - Apophatic-cataphatic balance
    - Council affirmations
    """

    # Heresy detection patterns
    HERESY_PATTERNS = {
        HeresyType.ARIANISM: [
            r'\bJesus\s+(?:is\s+)?(?:a\s+)?creature\b',
            r'\bSon\s+(?:is\s+)?created\b',
            r'\bChrist\s+(?:is\s+)?not\s+(?:fully\s+)?divine\b',
            r'\bthere\s+was\s+(?:a\s+)?time\s+when\s+(?:the\s+)?Son\s+was\s+not\b',
        ],
        HeresyType.NESTORIANISM: [
            r'\bMary\s+(?:is\s+)?not\s+(?:the\s+)?(?:Mother\s+of\s+God|Theotokos)\b',
            r'\btwo\s+(?:separate\s+)?persons\s+in\s+Christ\b',
            r'\bChristotokos\s+(?:not|rather\s+than)\s+Theotokos\b',
        ],
        HeresyType.MONOPHYSITISM: [
            r'\bone\s+nature\s+(?:only\s+)?(?:in|of)\s+Christ\b',
            r'\bdivine\s+nature\s+(?:absorbed|overwhelmed)\s+(?:the\s+)?human\b',
            r'\bChrist\s+(?:is\s+)?not\s+(?:fully\s+)?human\b',
        ],
        HeresyType.PELAGIANISM: [
            r'\bno\s+(?:original\s+)?sin\b',
            r'\bgrace\s+(?:is\s+)?not\s+(?:necessary|needed|required)\b',
            r'\bsave(?:d)?\s+(?:ourselves|himself|themselves)\s+by\s+works\b',
            r'\b(?:can\s+)?achieve\s+perfection\s+(?:by\s+)?(?:ourselves|alone)\b',
        ],
        HeresyType.MODALISM: [
            r'\bsame\s+person\s+(?:in\s+)?different\s+modes\b',
            r'\bFather\s+suffered\s+on\s+(?:the\s+)?cross\b',
            r'\bno\s+(?:real\s+)?distinction\s+(?:in|of|between)\s+(?:the\s+)?(?:Trinity|persons)\b',
        ],
        HeresyType.DOCETISM: [
            r'\bonly\s+appeared\s+(?:to\s+be\s+)?human\b',
            r'\bphantom\s+body\b',
            r'\billusion\s+of\s+(?:the\s+)?flesh\b',
        ],
        HeresyType.GNOSTICISM: [
            r'\bmatter\s+(?:is\s+)?evil\b',
            r'\bsecret\s+knowledge\s+(?:for\s+)?(?:the\s+)?elect\b',
            r'\bbody\s+(?:is\s+)?(?:a\s+)?prison\b',
        ],
        HeresyType.ICONOCLASM: [
            r'\bvenerat(?:e|ion)\s+(?:of\s+)?icons\s+(?:is\s+)?(?:idol(?:atry|atrous)|forbidden)\b',
            r'\bimages\s+(?:of\s+)?(?:Christ|saints)\s+(?:are\s+)?prohibited\b',
        ],
    }

    # Required orthodox affirmations
    REQUIRED_AFFIRMATIONS = {
        'trinity': [r'\bTrinity\b', r'\btriune\b', r'\bThree\s+Persons\b'],
        'theosis': [r'\btheosis\b', r'\bdeification\b', r'\bdivini[sz]ation\b'],
        'incarnation': [r'\bIncarnation\b', r'\bWord\s+became\s+flesh\b'],
        'nicene': [r'\b(?:consubstantial|homoousios)\b'],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize theological validator"""
        self.config = config or {}
        logger.debug("Theological validator initialized")

    def validate(self, text: str) -> ValidationResult:
        """
        Validate theological content.

        Args:
            text: Text to validate

        Returns:
            ValidationResult with errors, warnings, and metrics
        """
        result = ValidationResult(valid=True)

        # Check for heresies
        detected_heresies = self._detect_heresies(text)
        for heresy in detected_heresies:
            result.add_error(f"Possible {heresy.value} detected")

        # Check Nicene compliance
        if not self._check_nicene_compliance(text):
            result.add_warning("Missing Nicene terminology (homoousios/consubstantial)")

        # Check apophatic-cataphatic balance
        balance = self._check_apophatic_balance(text)
        result.add_metric('apophatic_ratio', balance)
        if balance < 0.2 or balance > 0.8:
            result.add_warning(
                f"Apophatic-cataphatic imbalance (ratio: {balance:.2f}, target: 0.3-0.7)"
            )

        # Check council affirmations
        council_check = self._check_council_affirmations(text)
        result.add_metric('council_references', council_check)

        # Calculate score
        result.score = self._calculate_theological_score(result)

        logger.debug(
            f"Theological validation: valid={result.valid}, "
            f"errors={len(result.errors)}, warnings={len(result.warnings)}"
        )

        return result

    def _detect_heresies(self, text: str) -> List[HeresyType]:
        """Detect potential heresies"""
        detected = []

        for heresy_type, patterns in self.HERESY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(heresy_type)
                    logger.warning(f"Detected possible {heresy_type.value}: {pattern}")
                    break

        return detected

    def _check_nicene_compliance(self, text: str) -> bool:
        """Check for Nicene Creed terminology"""
        nicene_terms = self.REQUIRED_AFFIRMATIONS['nicene']
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in nicene_terms)

    def _check_apophatic_balance(self, text: str) -> float:
        """
        Calculate apophatic vs cataphatic ratio.

        Returns:
            Ratio of apophatic language (0.0-1.0)
        """
        # Apophatic keywords
        apophatic = [
            r'\bunknowable\b', r'\bineffable\b', r'\bmystery\b',
            r'\bbeyond\s+(?:all\s+)?(?:comprehension|understanding)\b',
            r'\btranscendent\b', r'\binconceivable\b',
            r'\bunspeakable\b', r'\bhidden\b'
        ]

        # Cataphatic keywords
        cataphatic = [
            r'\bGod\s+is\s+\w+\b',  # God is love, etc.
            r'\bdivine\s+\w+\b',    # divine mercy, etc.
            r'\battributes?\b', r'\bproperties\b',
            r'\bcharacteristics\b'
        ]

        apophatic_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in apophatic
        )

        cataphatic_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in cataphatic
        )

        total = apophatic_count + cataphatic_count
        return apophatic_count / total if total > 0 else 0.5

    def _check_council_affirmations(self, text: str) -> int:
        """Count references to ecumenical councils"""
        councils = [
            r'\bNicaea\b', r'\bConstantinople\b', r'\bEphesus\b',
            r'\bChalcedon\b', r'\becumenical\s+council\b'
        ]

        return sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in councils
        )

    def _calculate_theological_score(self, result: ValidationResult) -> float:
        """Calculate overall theological quality score"""
        # Start with perfect score
        score = 1.0

        # Penalize errors heavily
        score -= len(result.errors) * 0.3

        # Penalize warnings moderately
        score -= len(result.warnings) * 0.05

        return max(0.0, min(1.0, score))


# ============================================================================
# STYLE VALIDATOR (ALPHA, BETA, GAMMA, DELTA)
# ============================================================================

class StyleValidator:
    """
    Validate stylistic quality using four rulesets.

    ALPHA: Vocabulary (word length, sophistication)
    BETA: Sentence structure (length, variation)
    GAMMA: Theological depth (citations, terminology)
    DELTA: Formal tone (capitalization, contractions)
    """

    # Simple words to avoid (ALPHA)
    SIMPLE_WORDS = {
        'get', 'got', 'make', 'made', 'do', 'did', 'go', 'went',
        'put', 'see', 'saw', 'say', 'said', 'think', 'know',
        'want', 'use', 'find', 'give', 'tell', 'work', 'call',
        'try', 'ask', 'need', 'feel', 'become', 'leave', 'put'
    }

    # Informal words to avoid (DELTA)
    INFORMAL_WORDS = {
        'lots', 'stuff', 'things', 'guy', 'guys', 'okay', 'ok',
        'yeah', 'yep', 'nope', 'gonna', 'wanna', 'kinda', 'sorta'
    }

    def __init__(self, config: Dict[str, Any]):
        """Initialize style validator"""
        self.config = config
        self.thresholds = config.get('validation', {})

    def validate(self, text: str) -> ValidationResult:
        """
        Validate style across all four rulesets.

        Args:
            text: Text to validate

        Returns:
            ValidationResult with detailed metrics
        """
        result = ValidationResult(valid=True)

        # ALPHA: Vocabulary
        alpha_result = self._validate_alpha(text)
        result.errors.extend(alpha_result.errors)
        result.warnings.extend(alpha_result.warnings)
        result.metrics.update(alpha_result.metrics)

        # BETA: Sentence structure
        beta_result = self._validate_beta(text)
        result.errors.extend(beta_result.errors)
        result.warnings.extend(beta_result.warnings)
        result.metrics.update(beta_result.metrics)

        # GAMMA: Theological depth
        gamma_result = self._validate_gamma(text)
        result.errors.extend(gamma_result.errors)
        result.warnings.extend(gamma_result.warnings)
        result.metrics.update(gamma_result.metrics)

        # DELTA: Formal tone
        delta_result = self._validate_delta(text)
        result.errors.extend(delta_result.errors)
        result.warnings.extend(delta_result.warnings)
        result.metrics.update(delta_result.metrics)

        # Calculate overall score
        result.score = self._calculate_style_score(result)
        result.valid = len(result.errors) == 0

        return result

    def _validate_alpha(self, text: str) -> ValidationResult:
        """ALPHA: Vocabulary sophistication"""
        result = ValidationResult(valid=True)

        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            result.add_error("No words found")
            return result

        # Average word length
        avg_word_length = sum(len(w) for w in words) / len(words)
        result.add_metric('avg_word_length', avg_word_length)

        min_avg = self.thresholds.get('min_avg_word_length', 5.2)
        if avg_word_length < min_avg:
            result.add_error(
                f"Average word length too short: {avg_word_length:.2f} "
                f"(minimum: {min_avg})"
            )

        # Simple word ratio
        simple_count = sum(1 for w in words if w in self.SIMPLE_WORDS)
        simple_ratio = simple_count / len(words)
        result.add_metric('simple_word_ratio', simple_ratio)

        max_simple = self.thresholds.get('max_simple_word_ratio', 0.35)
        if simple_ratio > max_simple:
            result.add_error(
                f"Too many simple words: {simple_ratio:.1%} "
                f"(maximum: {max_simple:.1%})"
            )

        return result

    def _validate_beta(self, text: str) -> ValidationResult:
        """BETA: Sentence structure"""
        result = ValidationResult(valid=True)

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            result.add_error("No sentences found")
            return result

        # Average sentence length
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        result.add_metric('avg_sentence_length', avg_length)

        min_avg = self.thresholds.get('min_avg_sentence_length', 20)
        max_avg = self.thresholds.get('max_avg_sentence_length', 40)

        if avg_length < min_avg:
            result.add_error(
                f"Sentences too short: {avg_length:.1f} words "
                f"(minimum: {min_avg})"
            )
        elif avg_length > max_avg:
            result.add_warning(
                f"Sentences very long: {avg_length:.1f} words "
                f"(maximum recommended: {max_avg})"
            )

        # Sentence length variation
        if len(sentence_lengths) > 3:
            length_variance = sum((l - avg_length)**2 for l in sentence_lengths) / len(sentence_lengths)
            result.add_metric('sentence_length_variance', length_variance)

            if length_variance < 10:
                result.add_warning("Low sentence length variation (monotonous)")

        return result

    def _validate_gamma(self, text: str) -> ValidationResult:
        """GAMMA: Theological depth"""
        result = ValidationResult(valid=True)

        word_count = len(text.split())

        # Patristic citations
        patristic_patterns = [
            r'\bSaint\s+\w+',
            r'\b(?:St\.|Saint)\s+(?:Athanasius|Basil|Gregory|Maximus|John\s+Chrysostom|Cyril)\b',
        ]
        patristic_count = sum(
            len(re.findall(p, text, re.IGNORECASE))
            for p in patristic_patterns
        )
        result.add_metric('patristic_citations', patristic_count)

        # Expected citations per 500 words
        expected_per_500 = self.thresholds.get('min_patristic_per_500_words', 2)
        expected_total = int(word_count / 500 * expected_per_500)

        if patristic_count < expected_total:
            result.add_error(
                f"Insufficient patristic citations: {patristic_count} "
                f"(expected: {expected_total})"
            )

        # Biblical references
        biblical_patterns = [
            r'\b(?:Genesis|Exodus|Matthew|John|Romans|Corinthians|Hebrews)\s+\d+:\d+',
            r'\b(?:Psalm|Isaiah|Gospel)\b',
        ]
        biblical_count = sum(
            len(re.findall(p, text, re.IGNORECASE))
            for p in biblical_patterns
        )
        result.add_metric('biblical_references', biblical_count)

        expected_biblical = int(word_count / 500 * self.thresholds.get('min_biblical_per_500_words', 3))
        if biblical_count < expected_biblical:
            result.add_warning(
                f"Low biblical references: {biblical_count} "
                f"(expected: {expected_biblical})"
            )

        return result

    def _validate_delta(self, text: str) -> ValidationResult:
        """DELTA: Formal tone"""
        result = ValidationResult(valid=True)

        # Check for contractions
        contractions = re.findall(r"\b\w+'\w+\b", text)
        if contractions:
            result.add_error(
                f"Contractions found: {', '.join(contractions[:5])} "
                f"(total: {len(contractions)})"
            )

        # Check for informal words
        words = set(re.findall(r'\b\w+\b', text.lower()))
        informal_found = words & self.INFORMAL_WORDS
        if informal_found:
            result.add_error(
                f"Informal words found: {', '.join(list(informal_found)[:5])}"
            )

        # Check capitalization of sacred terms
        sacred_terms = ['god', 'christ', 'trinity', 'holy spirit', 'church', 'scripture']
        for term in sacred_terms:
            # Find lowercase instances when not appropriate
            pattern = r'\b' + term.lower() + r'\b'
            if re.search(pattern, text):
                # Check if it's properly capitalized in context
                capitalized_pattern = r'\b' + term.capitalize() + r'\b'
                if not re.search(capitalized_pattern, text):
                    result.add_warning(f"Sacred term '{term}' may need capitalization")

        return result

    def _calculate_style_score(self, result: ValidationResult) -> float:
        """Calculate overall style quality score"""
        score = 1.0

        # Penalize errors
        score -= len(result.errors) * 0.15

        # Penalize warnings
        score -= len(result.warnings) * 0.05

        return max(0.0, min(1.0, score))


# ============================================================================
# PATRISTIC CITATION VALIDATOR
# ============================================================================

class PatristicCitationValidator:
    """
    Validate patristic citations for accuracy.

    Checks:
    - Recognized Father
    - Known work
    - Citation format
    """

    # Canonical Church Fathers
    CANONICAL_FATHERS = {
        'Saint Athanasius', 'Saint Basil the Great', 'Saint Gregory of Nazianzus',
        'Saint Gregory of Nyssa', 'Saint John Chrysostom', 'Saint Maximus the Confessor',
        'Saint John of Damascus', 'Saint Cyril of Alexandria', 'Saint Irenaeus',
        'Saint Gregory Palamas', 'Saint Isaac the Syrian', 'Saint Symeon the New Theologian'
    }

    # Known major works
    KNOWN_WORKS = {
        'Saint Athanasius': ['On the Incarnation', 'Against the Arians', 'Life of Antony'],
        'Saint Basil the Great': ['On the Holy Spirit', 'Hexaemeron', 'Ascetical Works'],
        'Saint Gregory of Nazianzus': ['Five Theological Orations', 'On God and Christ'],
        'Saint Maximus the Confessor': ['Ambigua', 'Four Hundred Chapters on Love', 'Mystagogy'],
        'Saint John Chrysostom': ['Homilies on Matthew', 'Homilies on John', 'On the Priesthood'],
    }

    def validate_citation(self, citation: str) -> Tuple[bool, List[str]]:
        """
        Validate a single citation.

        Args:
            citation: Citation text

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Check for recognized Father
        father_found = any(father in citation for father in self.CANONICAL_FATHERS)
        if not father_found:
            issues.append(f"Unrecognized Father in citation: {citation}")

        # Check for work title (if Father recognized)
        if father_found:
            for father, works in self.KNOWN_WORKS.items():
                if father in citation:
                    work_found = any(work in citation for work in works)
                    if not work_found and 'in his' in citation.lower():
                        issues.append(f"Unknown work cited for {father}")

        return len(issues) == 0, issues

    def count_citations(self, text: str) -> int:
        """Count number of patristic citations in text"""
        count = 0
        for father in self.CANONICAL_FATHERS:
            count += text.count(father)
        return count


# ============================================================================
# STRUCTURAL VALIDATOR
# ============================================================================

class StructuralValidator:
    """
    Validate entry structure.

    Checks:
    - Six required sections present
    - Proper section headings
    - Doxological ending
    - Appropriate word counts
    """

    REQUIRED_SECTIONS = [
        "I. Strategic Role",
        "II. Classification",
        "III. Primary Works",
        "IV. The Patristic Mind",
        "V. Symphony of Clashes",
        "VI. Orthodox Affirmation"
    ]

    def validate(self, text: str) -> ValidationResult:
        """Validate entry structure"""
        result = ValidationResult(valid=True)

        # Check for required sections
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            if section not in text:
                missing_sections.append(section)

        if missing_sections:
            result.add_error(f"Missing sections: {', '.join(missing_sections)}")

        # Check for doxological ending
        ending_patterns = [
            r'\bages\s+of\s+ages\b',
            r'\bAmen\b',
            r'\bglory\s+be\s+to\b'
        ]

        has_doxology = any(re.search(p, text, re.IGNORECASE) for p in ending_patterns)
        if not has_doxology:
            result.add_warning("Missing doxological ending")

        # Check word count
        word_count = len(text.split())
        result.add_metric('word_count', word_count)

        if word_count < 10000:
            result.add_error(f"Entry too short: {word_count} words (minimum: 10,000)")
        elif word_count > 15000:
            result.add_warning(f"Entry very long: {word_count} words (maximum: 15,000)")

        result.score = 1.0 if len(result.errors) == 0 else 0.5

        return result
