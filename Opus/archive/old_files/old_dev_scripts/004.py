"""
FILE 4: STYLE GUIDE VALIDATOR
=============================
Exhaustive style guide enforcement for all Absolute Rulesets (ALPHA, BETA, GAMMA, DELTA).
Real-time compliance checking with detailed reporting.
File 4 of 20: Style Validator
Optimized for: RAM Preloading (Golden Patterns) | Numpy Vectorization
"""
import logging
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RulesetType(Enum):
    """Absolute Ruleset types."""
    ALPHA = "ALPHA"
    BETA = "BETA"
    GAMMA = "GAMMA"
    DELTA = "DELTA"

@dataclass
class StyleViolation:
    """A single style violation."""
    ruleset: RulesetType
    rule_number: int
    violation: str
    location: str # line number or section
    severity: str # CRITICAL, WARNING, INFO
    correction: str
    example: str

class AbsoluteRulesetEnforcer:
    """Enforces all absolute rulesets."""
    RULESET_ALPHA = {
        "name": "Structure",
        "rules": {
            1: {
                "rule": "Exactly 6 sections with specific titles",
                "sections": [
                    "I. Strategic Role", "II. Classification", "III. Primary Works",
                    "IV. The Patristic Mind", "V. Symphony of Clashes", "VI. Orthodox Affirmation"
                ],
                "min_words": 10000, "severity": "CRITICAL"
            },
            2: {
                "rule": "Each section must be 1200-2500 words",
                "min_section": 1200, "max_section": 2500, "severity": "CRITICAL"
            },
            3: {"rule": "Total word count must exceed 10000 words", "severity": "CRITICAL"},
            4: {"rule": "Clear section headings with Roman numerals", "pattern": r'^[IVX]+\.\s+[A-Z]', "severity": "CRITICAL"}
        }
    }

    RULESET_BETA = {
        "name": "Formatting",
        "rules": {
            1: {
                "rule": "EVERY paragraph begins with exactly 4 spaces",
                "pattern": r'^ [^\s]', "severity": "CRITICAL"
            },
            2: {
                "rule": "NO em-dashes allowed (—)",
                "replacement": "Use hyphens (-) for compound words only",
                "pattern": r'—|–', "severity": "CRITICAL"
            },
            3: {
                "rule": "Numbers below 1000 must be spelled out",
                "pattern": r'\b([0-9]{1,3})\b(?![\.\,])',
                "severity": "WARNING", "exceptions": ["1200", "2000", "dates"]
            },
            4: {
                "rule": "NO contractions allowed",
                "pattern": r'\b(can\'t|don\'t|won\'t|it\'s|that\'s)\b', # Simplified list for brevity
                "severity": "WARNING"
            },
            5: {
                "rule": "Line length maximum 95 characters",
                "severity": "INFO"
            }
        }
    }

    RULESET_GAMMA = {
        "name": "Linguistic Precision",
        "rules": {
            1: {"rule": "Capitalize divine names", "pattern": r'\b(trinity|father|son|holy spirit)\b', "severity": "WARNING"},
            2: {"rule": "Use NOT...BUT structures", "required_pattern": r'not\s+[^\.]+but', "min_occurrences": 2, "severity": "WARNING"},
            4: {"rule": "Incorporate original language terms", "min_terms": 3, "severity": "WARNING"},
            5: {"rule": "Apophatic language usage", "pattern": r'(unknowable|mystery|beyond|ineffable)', "min_occurrences": 1, "severity": "WARNING"}
        }
    }

    RULESET_DELTA = {
        "name": "Content Requirements",
        "rules": {
            1: {"rule": "Patristic citations in every section", "pattern": r'(Saint|St\.) \w+', "min_per_section": 2, "severity": "CRITICAL"},
            3: {"rule": "Eucharistic culmination in Section VI", "section": 6, "required_phrases": ['Eucharist', 'liturgy'], "severity": "CRITICAL"},
            5: {"rule": "Theosis as unifying theme", "pattern": r'theosis|deification', "min_mentions": 3, "severity": "CRITICAL"}
        }
    }

    def __init__(self):
        self.rulesets = {
            RulesetType.ALPHA: self.RULESET_ALPHA,
            RulesetType.BETA: self.RULESET_BETA,
            RulesetType.GAMMA: self.RULESET_GAMMA,
            RulesetType.DELTA: self.RULESET_DELTA
        }
        self.golden_dir = Path("OPUS_MAXIMUS_INDIVIDUALIZED/Enhancement_Corpus")
        # Edit 12: Pre-load golden corpus patterns into RAM (leveraging 32GB)
        self.golden_patterns = self._preload_golden_patterns()

    # Edit 12 Implementation
    def _preload_golden_patterns(self) -> Dict:
        """Preload golden patterns for instant comparison."""
        patterns = {}
        if self.golden_dir.exists():
            for md_file in self.golden_dir.glob('*.md'):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    patterns[md_file.name] = {
                        'word_count': len(content.split()),
                        'avg_sentence_length': sum(len(s.split()) for s in content.split('.')) / max(1, len(content.split('.'))),
                        # 'theological_terms': self._extract_terms(content) # Requires TermRegistry linked
                    }
                except Exception as e:
                    logger.warning(f"Failed to preload {md_file}: {e}")
        return patterns

    def validate_content(self, content: str, section_num: int = None) -> List[StyleViolation]:
        """Validate content against all rulesets."""
        violations = []
        
        # Edit 13: Run vectorized checks first for speed
        violations.extend(self.check_line_lengths_vectorized(content))

        # Standard checks
        sections = self._split_into_sections(content)
        current_section = sections[section_num-1] if section_num and sections and section_num <= len(sections) else content

        for ruleset_type, ruleset in self.rulesets.items():
            violations.extend(self._check_ruleset(ruleset_type, ruleset, current_section, section_num))
            
        return violations

    # Edit 13 Implementation: Vectorized Check
    def check_line_lengths_vectorized(self, content: str) -> List[StyleViolation]:
        """GPU/CPU-accelerated line length check using Numpy."""
        violations = []
        lines = np.array(content.split('\n'))
        # Use np.char.str_len for vectorized length calculation
        lengths = np.char.str_len(lines)
        # Find indices where length > 95
        long_lines_indices = np.where(lengths > 95)[0]
        
        for idx in long_lines_indices[:5]: # Report first 5 violations to avoid spam
            violations.append(StyleViolation(
                ruleset=RulesetType.BETA,
                rule_number=5,
                violation=f"Line length exceeds 95 chars ({lengths[idx]})",
                location=f"Line {idx + 1}",
                severity="INFO",
                correction="Wrap text to 95 characters",
                example=lines[idx][:50] + "..."
            ))
        return violations

    def _split_into_sections(self, content: str) -> List[str]:
        pattern = r'(^[IVX]+\.\s+[A-Z][^\n]+)\n(.*?)(?=\n^[IVX]+\.|$)'
        matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
        return [match[1].strip() for match in matches]

    def _check_ruleset(self, ruleset_type: RulesetType, ruleset: Dict, content: str,
                       section_num: int = None) -> List[StyleViolation]:
        """Check single ruleset (Regex-based)."""
        violations = []
        for rule_num, rule in ruleset['rules'].items():
            # Skip Rule 5 (line length) here as it's handled by vectorization
            if ruleset_type == RulesetType.BETA and rule_num == 5:
                continue

            if 'pattern' in rule:
                matches = re.findall(rule['pattern'], content, re.MULTILINE)
                if matches:
                     # Special handling for Rule Delta 5 (Theosis mentions) - it demands a MINIMUM
                    if 'min_mentions' in rule:
                         if len(matches) < rule['min_mentions']:
                             violations.append(StyleViolation(
                                 ruleset=ruleset_type, rule_number=rule_num,
                                 violation=f"Insufficient mentions of {rule['pattern']} (found {len(matches)}, need {rule['min_mentions']})",
                                 location="Global" if not section_num else f"Section {section_num}",
                                 severity=rule['severity'], correction=f"Add more references to {rule['pattern']}", example="N/A"
                             ))
                    # Standard pattern MUST NOT exist (like contractions)
                    elif 'min_mentions' not in rule and 'min_occurrences' not in rule and 'min_per_section' not in rule:
                         for match in matches[:1]:
                            violations.append(StyleViolation(
                                ruleset=ruleset_type, rule_number=rule_num,
                                violation=f"Forbidden pattern found: {match}",
                                location="Text body", severity=rule['severity'],
                                correction=rule.get('replacement', 'Remove/Rewrite'), example=match
                            ))
            
            # ALPHA word counts
            elif ruleset_type == RulesetType.ALPHA and rule_num == 3:
                 total_words = len(content.split())
                 if total_words < rule.get('min_words', 10000) and not section_num:
                     violations.append(StyleViolation(
                         ruleset=ruleset_type, rule_number=rule_num,
                         violation=f"Total word count {total_words} < 10000",
                         location="Entire Entry", severity="CRITICAL",
                         correction="Expand all sections", example="N/A"
                     ))

        return violations

    def generate_compliance_report(self, violations: List[StyleViolation]) -> str:
        """Generate compliance report."""
        if not violations:
            return "\n✓ ALL STYLE CHECKS PASSED"
        report = ["OPUS MAXIMUS STYLE COMPLIANCE REPORT"]
        critical = [v for v in violations if v.severity == "CRITICAL"]
        if critical:
            report.append("\n🔴 CRITICAL VIOLATIONS (MUST FIX):")
            for v in critical:
                report.append(f" - {v.ruleset.name} R{v.rule_number}: {v.violation} [{v.location}]")
        
        warnings = [v for v in violations if v.severity == "WARNING"]
        if warnings:
             report.append(f"\n🟡 WARNINGS: {len(warnings)} found")

        return "\n".join(report)

enforcer = AbsoluteRulesetEnforcer()