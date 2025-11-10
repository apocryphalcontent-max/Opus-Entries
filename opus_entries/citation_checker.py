"""
Citation checker for automated quality-based validation of Patristic citations
"""
from typing import Dict, List
from .models import Entry


class CitationChecker:
    """Automated citation quality checker with 4 scoring metrics"""
    
    # Database of verified Patristic works by Church Father
    PATRISTIC_WORKS_DATABASE = {
        "Gregory of Nyssa": [
            "On the Making of Man",
            "The Life of Moses",
            "Against Eunomius",
            "On the Soul and the Resurrection",
            "The Great Catechism"
        ],
        "Maximus the Confessor": [
            "The Ambigua",
            "Chapters on Knowledge",
            "On the Cosmic Mystery of Jesus Christ",
            "The Four Hundred Chapters on Love",
            "Questions to Thalassius"
        ],
        "Basil the Great": [
            "On the Holy Spirit",
            "Hexaemeron",
            "Against Eunomius",
            "Moralia",
            "The Long Rules"
        ],
        "Athanasius": [
            "On the Incarnation",
            "Against the Arians",
            "Life of Antony",
            "Letters to Serapion"
        ],
        "John Chrysostom": [
            "Homilies on Matthew",
            "Homilies on John",
            "On the Priesthood",
            "Homilies on Romans",
            "Divine Liturgy of St. John Chrysostom"
        ],
        "Gregory Palamas": [
            "The Triads",
            "One Hundred and Fifty Chapters",
            "Homilies"
        ],
        "John of Damascus": [
            "The Fount of Knowledge",
            "An Exact Exposition of the Orthodox Faith",
            "Three Treatises on the Divine Images"
        ],
        "Ignatius of Antioch": [
            "Letter to the Ephesians",
            "Letter to the Romans",
            "Letter to the Smyrnaeans"
        ],
        "Irenaeus": [
            "Against Heresies",
            "Demonstration of the Apostolic Preaching"
        ]
    }
    
    def __init__(self):
        """Initialize the citation checker"""
        self.all_fathers = list(self.PATRISTIC_WORKS_DATABASE.keys())
    
    def check_quality(self, entry: Entry) -> Dict[str, float]:
        """
        Run all 4 quality checks on entry citations
        
        Args:
            entry: Entry to check
        
        Returns:
            Dictionary with scores for each metric
        """
        total_content = " ".join(section.content for section in entry.sections)
        
        diversity_score = self.calculate_diversity_score(total_content)
        specificity_score = self.calculate_specificity_score(total_content)
        integration_score = self.calculate_integration_score(entry)
        distribution_score = self.calculate_distribution_score(entry)
        
        # Composite score (all metrics equal weight)
        composite_score = (diversity_score + specificity_score + integration_score + distribution_score) / 4
        
        return {
            "diversity": diversity_score,
            "specificity": specificity_score,
            "integration": integration_score,
            "distribution": distribution_score,
            "composite": composite_score
        }
    
    def calculate_diversity_score(self, content: str) -> float:
        """
        Calculate Diversity Score: Citation breadth across Patristic tradition
        
        Measures: How many different Church Fathers are cited?
        Target: 5+ different Fathers
        Threshold: 80/100
        
        Args:
            content: Full entry content
        
        Returns:
            Score from 0-100
        """
        fathers_cited = []
        
        for father in self.all_fathers:
            if father in content or father.split()[-1] in content:  # Check full name or last name
                fathers_cited.append(father)
        
        count = len(fathers_cited)
        
        # Scoring algorithm
        if count >= 5:
            return 100
        elif count == 4:
            return 85
        elif count == 3:
            return 70
        elif count == 2:
            return 50
        elif count == 1:
            return 30
        else:
            return 0
    
    def calculate_specificity_score(self, content: str) -> float:
        """
        Calculate Specificity Score: Citation depth and scholarly precision
        
        Measures: How many specific Patristic works are named?
        Target: 3+ specific works
        Threshold: 70/100
        
        Args:
            content: Full entry content
        
        Returns:
            Score from 0-100
        """
        works_cited = []
        
        for father, works in self.PATRISTIC_WORKS_DATABASE.items():
            for work in works:
                if work in content:
                    works_cited.append(work)
        
        count = len(works_cited)
        
        # Scoring algorithm
        if count >= 3:
            return 100
        elif count == 2:
            return 75
        elif count == 1:
            return 50
        else:
            # Check for generic works patterns (partial credit)
            generic_patterns = [
                "in his work",
                "in his treatise",
                "in his homily",
                "in his letter",
                "in his commentary"
            ]
            generic_count = sum(1 for pattern in generic_patterns if pattern.lower() in content.lower())
            return min(40, generic_count * 10)
    
    def calculate_integration_score(self, entry: Entry) -> float:
        """
        Calculate Integration Score: Natural flow of citations
        
        Measures: Whether citations are evenly distributed or clustered
        Target: Even distribution across sections
        Threshold: 70/100
        
        Args:
            entry: Entry object
        
        Returns:
            Score from 0-100
        """
        # Count Patristic references per section
        section_citation_counts = []
        
        for section in entry.sections:
            citation_count = 0
            for father in self.all_fathers:
                if father in section.content or father.split()[-1] in section.content:
                    citation_count += 1
            section_citation_counts.append(citation_count)
        
        if not section_citation_counts:
            return 0
        
        # Calculate variance (lower variance = better distribution)
        mean_citations = sum(section_citation_counts) / len(section_citation_counts)
        
        if mean_citations == 0:
            return 0
        
        variance = sum((x - mean_citations) ** 2 for x in section_citation_counts) / len(section_citation_counts)
        std_dev = variance ** 0.5
        
        # Coefficient of variation (lower is better)
        cv = (std_dev / mean_citations) if mean_citations > 0 else 0
        
        # Score based on evenness (cv closer to 0 is better)
        if cv <= 0.3:
            return 100
        elif cv <= 0.5:
            return 85
        elif cv <= 0.7:
            return 70
        elif cv <= 1.0:
            return 55
        else:
            return max(40, 100 - (cv * 50))
    
    def calculate_distribution_score(self, entry: Entry) -> float:
        """
        Calculate Distribution Score: Patristic content across sections
        
        Measures: Whether all sections have Patristic grounding
        Target: Patristic content in 4+ sections (not just "The Patristic Mind")
        Threshold: 85/100
        
        Args:
            entry: Entry object
        
        Returns:
            Score from 0-100
        """
        sections_with_patristic_content = 0
        
        patristic_indicators = [
            "Patristic", "patristic", "Fathers", "Father",
            "Tradition", "tradition"
        ] + self.all_fathers
        
        for section in entry.sections:
            has_patristic = any(indicator in section.content for indicator in patristic_indicators)
            if has_patristic:
                sections_with_patristic_content += 1
        
        total_sections = len(entry.sections)
        
        if total_sections == 0:
            return 0
        
        # Scoring algorithm
        ratio = sections_with_patristic_content / total_sections
        
        if ratio >= 0.67:  # 4/6 sections or better
            return 100
        elif ratio >= 0.5:  # 3/6 sections
            return 80
        elif ratio >= 0.33:  # 2/6 sections
            return 60
        else:
            return ratio * 100
    
    def generate_citation_report(self, entry: Entry) -> Dict:
        """
        Generate comprehensive citation quality report
        
        Args:
            entry: Entry to analyze
        
        Returns:
            Dictionary with scores and recommendations
        """
        scores = self.check_quality(entry)
        
        recommendations = []
        
        # Diversity recommendations
        if scores["diversity"] < 80:
            total_content = " ".join(section.content for section in entry.sections)
            fathers_cited = [f for f in self.all_fathers if f in total_content or f.split()[-1] in total_content]
            missing_fathers = [f for f in self.all_fathers if f not in fathers_cited]
            recommendations.append(f"Add citations from: {', '.join(missing_fathers[:3])}")
        
        # Specificity recommendations
        if scores["specificity"] < 70:
            recommendations.append("Name specific Patristic works (e.g., 'St. Basil in On the Holy Spirit argues...')")
        
        # Integration recommendations
        if scores["integration"] < 70:
            recommendations.append("Distribute citations more evenly across sections (avoid clustering)")
        
        # Distribution recommendations
        if scores["distribution"] < 85:
            recommendations.append("Add Patristic content to Introduction, Symphony, Orthodox Affirmation, Synthesis, and Conclusion (not just 'The Patristic Mind')")
        
        return {
            "scores": scores,
            "recommendations": recommendations,
            "passed": scores["composite"] >= 75,  # 75% composite threshold for acceptance
            "status": "PASS" if scores["composite"] >= 75 else "NEEDS REFINEMENT"
        }
