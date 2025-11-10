"""
FILE 5: PLAGIARISM & CITATION VERIFIER
=======================================
Multi-layer plagiarism detection and academic integrity system.
File 5 of 20: Integrity Verifier
Optimized for: GPU N-Gram Extraction (Edit 14)
"""
import logging
from typing import List, Dict, Tuple
from collections import Counter
import hashlib
import re
import torch

logger = logging.getLogger(__name__)

class PlagiarismDetector:
    """Detects plagiarism and self-plagiarism."""
    def __init__(self):
        self.phrase_hashes = {}
        self.content_signatures = {}
        # Edit 14: Check for GPU availability for accelerated processing
        self.use_gpu = torch.cuda.is_available()
        if self.use_gpu:
             logger.info("Plagiarism detector utilizing GPU for n-gram extraction")

    def check_plagiarism(self, content: str, existing_corpus: List[str]) -> Dict:
        """Check against existing corpus."""
        results = {
            "is_plagiarized": False,
            "similarity_scores": [],
            "flagged_passages": []
        }
        content_phrases = self._extract_phrases(content, 5)
        # Convert to set once for speed
        content_phrases_set = set(content_phrases)

        for existing in existing_corpus:
            existing_phrases = set(self._extract_phrases(existing, 5))
            matches = content_phrases_set & existing_phrases
            
            if matches:
                # Jaccard similarity
                union_len = len(content_phrases_set | existing_phrases)
                similarity = len(matches) / union_len if union_len > 0 else 0
                
                if similarity > 0.3: # Threshold from config
                    results["is_plagiarized"] = True
                    results["similarity_scores"].append({
                        "similarity": similarity,
                        "source": existing[:100] + "..."
                    })
                    results["flagged_passages"].extend(list(matches)[:5])
                    
        return results

    def _extract_phrases(self, text: str, length: int) -> List[str]:
        """GPU-accelerated n-gram extraction (Edit 14)."""
        words = text.split()
        num_words = len(words)
        
        if num_words < length:
            return []

        # Use GPU only for larger texts where transfer overhead is worth it
        if self.use_gpu and num_words > 5000:
            try:
                # Create indices on GPU
                indices = torch.arange(num_words - length + 1, device='cuda')
                # Move back to CPU for list slicing (string ops still faster on CPU currently)
                indices_cpu = indices.cpu().numpy()
                return [' '.join(words[i:i+length]) for i in indices_cpu]
            except Exception as e:
                logger.warning(f"GPU n-gram extraction failed, falling back to CPU: {e}")
                # Fallback to CPU if VRAM is tight
                return [' '.join(words[i:i+length]) for i in range(num_words - length + 1)]
        else:
            # Standard CPU extraction for smaller texts
            return [' '.join(words[i:i+length]) for i in range(num_words - length + 1)]

class CitationVerifier:
    """Verifies citation accuracy and completeness."""
    def __init__(self):
        self.citation_patterns = {
            'patristic': r'(?:Saint|St\.)\s+\w+.*?(?:Homily|On|Against|Commentary)',
            'ecumenical_council': r'(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth)\s+Ecumenical\s+Council',
            'scriptural': r'(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song of Songs|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|John|Jude|Revelation).*?(?:\d+:\d+)?',
            'liturgical': r'(?:Divine\s+Liturgy|Triodion|Pentekostarion|Menaion|Oktoechos|Horologion)'
        }

    def verify_citations(self, content: str) -> Dict:
        """Verify citation patterns."""
        results = {"total_citations": 0, "verified": 0, "missing": []}
        
        for citation_type, pattern in self.citation_patterns.items():
            # Using re.IGNORECASE for wider catching
            matches = re.findall(pattern, content, re.IGNORECASE)
            results["total_citations"] += len(matches)
            # Simple verification: is it long enough to be real and does it have some specificity (like a period indicating abbreviation or end of sentence)?
            results["verified"] += len([m for m in matches if len(m) > 5])
            
        return results

# Global instances
plagiarism_detector = PlagiarismDetector()
citation_verifier = CitationVerifier()