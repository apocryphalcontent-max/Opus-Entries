"""
Entry validator for assessing quality and assigning tiers
"""
from typing import List
from .models import Entry, ValidationResult, QualityTier
from .config import Config


class EntryValidator:
    """Validator for assessing entry quality and assigning tiers"""
    
    def __init__(self, config: Config = None):
        """
        Initialize the validator
        
        Args:
            config: Configuration object (creates default if not provided)
        """
        self.config = config or Config()
    
    def validate(self, entry: Entry) -> ValidationResult:
        """
        Validate an entry and calculate its quality score
        
        Args:
            entry: The entry to validate
        
        Returns:
            ValidationResult with scores and tier assignment
        """
        weights = self.config.get_validation_weights()
        
        # Calculate individual component scores
        word_count_score = self._calculate_word_count_score(entry)
        theological_depth_score = self._calculate_theological_depth_score(entry)
        coherence_score = self._calculate_coherence_score(entry)
        section_balance_score = self._calculate_section_balance_score(entry)
        orthodox_perspective_score = self._calculate_orthodox_perspective_score(entry)
        
        # Calculate weighted total score
        total_score = (
            word_count_score * weights.get("word_count", 0.2) +
            theological_depth_score * weights.get("theological_depth", 0.3) +
            coherence_score * weights.get("coherence", 0.25) +
            section_balance_score * weights.get("section_balance", 0.15) +
            orthodox_perspective_score * weights.get("orthodox_perspective", 0.1)
        )
        
        # Determine quality tier
        quality_tier = self._determine_quality_tier(total_score)
        
        # Generate feedback
        feedback = self._generate_feedback(
            entry, word_count_score, theological_depth_score, 
            coherence_score, section_balance_score, orthodox_perspective_score
        )
        
        # Update entry with validation results
        entry.validation_score = total_score
        entry.quality_tier = quality_tier
        
        return ValidationResult(
            score=total_score,
            quality_tier=quality_tier,
            word_count_score=word_count_score,
            theological_depth_score=theological_depth_score,
            coherence_score=coherence_score,
            section_balance_score=section_balance_score,
            orthodox_perspective_score=orthodox_perspective_score,
            feedback=feedback
        )
    
    def _calculate_word_count_score(self, entry: Entry) -> float:
        """Calculate score based on word count (minimum: 11,000 words, no maximum)"""
        min_words = self.config.get("entry.min_word_count", 11000)
        
        total_words = entry.total_word_count
        
        if total_words >= min_words:
            # Meets minimum - full score
            # No penalty for going over (complex topics require more words)
            return 100.0
        else:
            # Below minimum - proportional penalty
            ratio = total_words / min_words
            return max(0, ratio * 100)
    
    def _calculate_theological_depth_score(self, entry: Entry) -> float:
        """Calculate score based on theological depth"""
        # Look for key theological indicators
        depth_indicators = [
            "Patristic", "patristic", "Fathers", "Father",
            "Scripture", "Biblical", "Gospel",
            "theosis", "incarnation", "Trinity",
            "sacrament", "liturgy", "prayer",
            "tradition", "Tradition"
        ]
        
        total_content = " ".join(section.content for section in entry.sections)
        indicator_count = sum(1 for indicator in depth_indicators if indicator in total_content)
        
        # Check for specific theological sections
        patristic_section = entry.get_section("The Patristic Mind")
        orthodox_section = entry.get_section("Orthodox Affirmation")
        
        base_score = min(100, 60 + (indicator_count * 2))
        
        # Bonus for having substantial theological sections
        if patristic_section and patristic_section.word_count >= 1500:
            base_score += 10
        if orthodox_section and orthodox_section.word_count >= 1500:
            base_score += 10
        
        return min(100, base_score)
    
    def _calculate_coherence_score(self, entry: Entry) -> float:
        """Calculate score based on entry coherence"""
        # Check that all required sections are present
        required_sections = ["Introduction", "The Patristic Mind", "Symphony of Clashes", 
                           "Orthodox Affirmation", "Synthesis", "Conclusion"]
        
        present_sections = [section.name for section in entry.sections]
        sections_present = sum(1 for req in required_sections if req in present_sections)
        
        section_score = (sections_present / len(required_sections)) * 100
        
        # Check for reasonable content in each section
        content_score = 100
        for section in entry.sections:
            if section.word_count < 500:  # Too short
                content_score -= 10
        
        return max(0, min(100, (section_score + content_score) / 2))
    
    def _calculate_section_balance_score(self, entry: Entry) -> float:
        """Calculate score based on balance between sections (minimums only, no maximums)"""
        if not entry.sections:
            return 0
        
        section_configs = {sc["name"]: sc for sc in self.config.get_section_configs()}
        
        balance_scores = []
        for section in entry.sections:
            if section.name in section_configs:
                config = section_configs[section.name]
                min_words = config.get("min_words", 1000)
                optimal_zone_max = config.get("optimal_zone_max", 3000)
                
                if section.word_count >= min_words:
                    # Meets minimum - calculate bonus for being in optimal zone
                    if section.word_count <= optimal_zone_max:
                        balance_scores.append(100)  # In optimal zone
                    else:
                        # Above optimal zone but NOT penalized (complex topics need space)
                        balance_scores.append(95)  # Slight preference for optimal zone
                else:
                    # Below minimum - proportional penalty
                    ratio = section.word_count / min_words
                    balance_scores.append(ratio * 100)
        
        return sum(balance_scores) / len(balance_scores) if balance_scores else 70
    
    def _calculate_orthodox_perspective_score(self, entry: Entry) -> float:
        """Calculate score based on Orthodox perspective"""
        # Look for Orthodox-specific terminology and concepts
        orthodox_indicators = [
            "Orthodox", "orthodox",
            "Eastern", "eastern",
            "Patristic", "patristic",
            "tradition", "Tradition",
            "theosis", "divine energies",
            "synergy", "mystery"
        ]
        
        total_content = " ".join(section.content for section in entry.sections)
        indicator_count = sum(1 for indicator in orthodox_indicators if indicator in total_content)
        
        return min(100, 70 + (indicator_count * 3))
    
    def _determine_quality_tier(self, score: float) -> QualityTier:
        """Determine quality tier based on score"""
        tiers = self.config.get_quality_tiers()
        
        for tier_name in ["CELESTIAL", "ADAMANTINE", "PLATINUM", "GOLD", "SILVER", "BRONZE"]:
            tier_config = tiers.get(tier_name, {})
            min_score = tier_config.get("min_score", 0)
            max_score = tier_config.get("max_score", 100)
            
            if min_score <= score <= max_score:
                return QualityTier[tier_name]
        
        return QualityTier.UNRANKED
    
    def _generate_feedback(
        self,
        entry: Entry,
        word_count_score: float,
        theological_depth_score: float,
        coherence_score: float,
        section_balance_score: float,
        orthodox_perspective_score: float
    ) -> List[str]:
        """Generate feedback messages based on scores"""
        feedback = []
        
        min_words = self.config.get("entry.min_word_count", 11000)
        total_score = (
            word_count_score * 0.2 +
            theological_depth_score * 0.3 +
            coherence_score * 0.25 +
            section_balance_score * 0.15 +
            orthodox_perspective_score * 0.1
        )
        
        # CELESTIAL mandate check
        if total_score < 95:
            feedback.append(f"Entry scored {total_score:.1f}/100. CELESTIAL tier (95+) required. Iterative refinement needed.")
        
        # Word count feedback
        if word_count_score < 100:
            if entry.total_word_count < min_words:
                feedback.append(f"Entry too short ({entry.total_word_count} words). Minimum: {min_words} words. Expand sections as needed.")
        
        # Theological depth feedback
        if theological_depth_score < 90:
            feedback.append("Deepen theological content: add Patristic citations (20+ minimum), Scripture references (15+ minimum), and Orthodox theological vocabulary.")
        
        # Coherence feedback
        if coherence_score < 90:
            feedback.append("Improve coherence: ensure all sections are well-developed, flow naturally, and connect thematically.")
        
        # Section balance feedback
        if section_balance_score < 90:
            feedback.append("Section imbalance detected. Review each section against minimum word counts. Expand under-developed sections.")
        
        # Orthodox perspective feedback
        if orthodox_perspective_score < 90:
            feedback.append("Strengthen Orthodox Christian perspective: increase Orthodox-specific terminology, liturgical grounding, and contrasts with Western theology.")
        
        if total_score >= 95:
            feedback.append(f"CELESTIAL tier achieved ({total_score:.1f}/100)! Entry meets all quality standards.")
        
        return feedback
