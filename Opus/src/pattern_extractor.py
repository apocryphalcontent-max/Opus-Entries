"""
OPUS MAXIMUS: GOLDEN ENTRY PATTERN EXTRACTOR
============================================

Analyzes golden entries to extract their quality DNA:
- Vocabulary patterns
- Sentence structures  
- Rhetorical devices
- Theological patterns
- Citation styles

These patterns become templates for new generation.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
import statistics


@dataclass
class VocabularyPattern:
    """Vocabulary characteristics of golden entry"""
    avg_word_length: float
    simple_word_ratio: float
    sophisticated_terms: List[str]
    greek_latin_terms: List[str]
    theological_density: float
    word_length_distribution: Dict[str, int]


@dataclass
class SentencePattern:
    """Sentence structure patterns"""
    avg_sentence_length: float
    sentence_length_distribution: Dict[str, float]  # short/medium/long
    epic_sentences: List[str]  # Sentences 100+ words
    sentence_variation_coefficient: float
    subordination_depth: float  # Average clause depth


@dataclass
class RhetoricalPattern:
    """Rhetorical device patterns"""
    not_but_structures: List[str]
    anaphora_patterns: List[str]
    polysyndeton_examples: List[str]
    chiasmus_examples: List[str]
    tricolon_examples: List[str]
    rhetorical_questions: List[str]


@dataclass
class TheologicalPattern:
    """Theological precision patterns"""
    patristic_citations: List[Dict[str, str]]  # {father, work, quote}
    biblical_references: List[str]
    heresies_addressed: List[str]
    councils_referenced: List[str]
    apophatic_cataphatic_ratio: float


@dataclass
class SectionPattern:
    """Patterns for specific section types"""
    section_number: str
    section_name: str
    word_count: int
    opening_sentence: str
    closing_sentence: str
    main_fathers_cited: List[str]
    key_arguments: List[str]
    rhetorical_strategy: str


@dataclass
class GoldenPattern:
    """Complete quality DNA from a golden entry"""
    entry_name: str
    vocabulary: VocabularyPattern
    sentences: SentencePattern
    rhetoric: RhetoricalPattern
    theology: TheologicalPattern
    sections: List[SectionPattern]
    overall_score: float
    special_features: List[str]


class GoldenEntryAnalyzer:
    """Extract patterns from golden entries"""
    
    # Simple words list (for calculating ratio)
    SIMPLE_WORDS = set([
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do',
        'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we',
        'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all',
        'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if'
    ])
    
    def __init__(self):
        """Initialize analyzer"""
        self.patterns = []
    
    def analyze_golden_entry(self, entry_path: Path) -> GoldenPattern:
        """Complete analysis of a golden entry"""
        
        print(f"\n{'='*70}")
        print(f"Analyzing: {entry_path.name}")
        print(f"{'='*70}")
        
        content = entry_path.read_text(encoding='utf-8')
        
        # Extract patterns
        vocabulary = self._analyze_vocabulary(content)
        print(f"✓ Vocabulary analyzed: {vocabulary.avg_word_length:.2f} avg chars")
        
        sentences = self._analyze_sentences(content)
        print(f"✓ Sentences analyzed: {sentences.avg_sentence_length:.1f} avg words")
        
        rhetoric = self._analyze_rhetoric(content)
        print(f"✓ Rhetoric analyzed: {len(rhetoric.not_but_structures)} NOT...BUT structures")
        
        theology = self._analyze_theology(content)
        print(f"✓ Theology analyzed: {len(theology.patristic_citations)} patristic citations")
        
        sections = self._analyze_sections(content)
        print(f"✓ Sections analyzed: {len(sections)} sections found")
        
        # Calculate overall score
        overall = self._calculate_overall_score(vocabulary, sentences, rhetoric, theology)
        print(f"✓ Overall quality score: {overall:.4f}")
        
        # Identify special features
        special = self._identify_special_features(content, sentences, rhetoric)
        print(f"✓ Special features: {', '.join(special[:3])}")
        
        pattern = GoldenPattern(
            entry_name=entry_path.stem,
            vocabulary=vocabulary,
            sentences=sentences,
            rhetoric=rhetoric,
            theology=theology,
            sections=sections,
            overall_score=overall,
            special_features=special
        )
        
        self.patterns.append(pattern)
        return pattern
    
    def _analyze_vocabulary(self, content: str) -> VocabularyPattern:
        """Extract vocabulary patterns"""
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
        
        # Average word length
        avg_length = sum(len(w) for w in words) / len(words) if words else 0
        
        # Simple word ratio
        simple_count = sum(1 for w in words if w in self.SIMPLE_WORDS)
        simple_ratio = simple_count / len(words) if words else 0
        
        # Find sophisticated theological terms
        sophisticated = self._extract_sophisticated_terms(content)
        
        # Find Greek/Latin terms
        greek_latin = self._extract_classical_terms(content)
        
        # Theological density (theological terms per 1000 words)
        theological_density = len(sophisticated) / len(words) * 1000 if words else 0
        
        # Word length distribution
        length_dist = Counter(len(w) for w in words)
        
        return VocabularyPattern(
            avg_word_length=avg_length,
            simple_word_ratio=simple_ratio,
            sophisticated_terms=sophisticated,
            greek_latin_terms=greek_latin,
            theological_density=theological_density,
            word_length_distribution=dict(length_dist)
        )
    
    def _analyze_sentences(self, content: str) -> SentencePattern:
        """Extract sentence structure patterns"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 3]
        
        # Sentence lengths in words
        lengths = [len(s.split()) for s in sentences]
        
        # Average
        avg_length = statistics.mean(lengths) if lengths else 0
        
        # Distribution
        short = sum(1 for l in lengths if 5 <= l <= 15)
        medium = sum(1 for l in lengths if 16 <= l <= 40)
        long = sum(1 for l in lengths if 41 <= l <= 100)
        epic = sum(1 for l in lengths if l > 100)
        total = len(lengths)
        
        distribution = {
            'short_ratio': short / total if total else 0,
            'medium_ratio': medium / total if total else 0,
            'long_ratio': long / total if total else 0,
            'epic_ratio': epic / total if total else 0
        }
        
        # Epic sentences (100+ words)
        epic_sentences = [s for s in sentences if len(s.split()) >= 100]
        
        # Variation coefficient
        variation = statistics.stdev(lengths) / avg_length if avg_length > 0 and len(lengths) > 1 else 0
        
        # Estimate subordination depth (count commas as proxy)
        avg_commas = statistics.mean([s.count(',') for s in sentences]) if sentences else 0
        subordination = avg_commas / 3  # Rough estimate
        
        return SentencePattern(
            avg_sentence_length=avg_length,
            sentence_length_distribution=distribution,
            epic_sentences=epic_sentences[:5],  # Keep top 5
            sentence_variation_coefficient=variation,
            subordination_depth=subordination
        )
    
    def _analyze_rhetoric(self, content: str) -> RhetoricalPattern:
        """Extract rhetorical device patterns"""
        
        # NOT...BUT structures
        not_but_pattern = r'(?:NOT|not)\s+[^,\.]+(?:,\s+)?(?:BUT|but)\s+[^,\.]+'
        not_but = re.findall(not_but_pattern, content)
        
        # Anaphora (repeated sentence starts)
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        anaphora = []
        for i in range(len(sentences) - 2):
            start1 = ' '.join(sentences[i].split()[:3])
            start2 = ' '.join(sentences[i+1].split()[:3])
            if start1 and start1 == start2 and len(start1.split()) == 3:
                anaphora.append(start1)
        
        # Polysyndeton (repeated "and" or "or")
        polysyndeton_pattern = r'(?:and|or)\s+\w+(?:\s+(?:and|or)\s+\w+){2,}'
        polysyndeton = re.findall(polysyndeton_pattern, content, re.IGNORECASE)
        
        # Chiasmus (harder to detect automatically, look for A-B-B-A patterns)
        chiasmus = []  # TODO: implement detection
        
        # Tricolon (lists of three)
        tricolon_pattern = r'\w+,\s+\w+,\s+(?:and|or)\s+\w+'
        tricolon = re.findall(tricolon_pattern, content)
        
        # Rhetorical questions
        rhetorical_pattern = r'[A-Z][^?]*\?'
        rhetorical = re.findall(rhetorical_pattern, content)
        
        return RhetoricalPattern(
            not_but_structures=not_but[:20],
            anaphora_patterns=list(set(anaphora))[:10],
            polysyndeton_examples=polysyndeton[:10],
            chiasmus_examples=chiasmus[:5],
            tricolon_examples=tricolon[:15],
            rhetorical_questions=rhetorical[:10]
        )
    
    def _analyze_theology(self, content: str) -> TheologicalPattern:
        """Extract theological precision patterns"""
        
        # Patristic citations
        patristic_pattern = r'(?:Saint|St\.)\s+([A-Za-z\s]+?)(?:,\s+in\s+his\s+|,\s+in\s+her\s+|\s+(?:writes|teaches|says|argues|affirms))'
        patristic_matches = re.findall(patristic_pattern, content)
        
        patristic_citations = []
        for father in patristic_matches:
            # Try to find the work
            work_pattern = rf'{re.escape(father)}[^.]+?(?:in|on)\s+([A-Z][^,\.]+)'
            work_match = re.search(work_pattern, content)
            work = work_match.group(1) if work_match else "Unknown work"
            
            patristic_citations.append({
                'father': father.strip(),
                'work': work,
                'quote': ''  # Would need more sophisticated extraction
            })
        
        # Biblical references
        biblical_pattern = r'\b(?:Genesis|Exodus|Matthew|Mark|Luke|John|Romans|Corinthians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Hebrews|James|Peter|Revelation)\s+\d+(?::\d+)?'
        biblical = re.findall(biblical_pattern, content)
        
        # Heresies mentioned
        heresies = [
            'Arianism', 'Nestorianism', 'Monophysitism', 'Pelagianism',
            'Semi-Pelagianism', 'Modalism', 'Gnosticism', 'Docetism',
            'Iconoclasm', 'Monothelitism', 'Apollinarianism'
        ]
        heresies_found = [h for h in heresies if h in content]
        
        # Councils referenced
        councils = [
            'Nicaea', 'Constantinople', 'Ephesus', 'Chalcedon'
        ]
        councils_found = [c for c in councils if c in content]
        
        # Apophatic vs cataphatic language
        cataphatic_pattern = r'God\s+is\s+\w+'
        apophatic_pattern = r'\b(?:unknowable|ineffable|beyond|transcendent|mystery|incomprehensible)\b'
        
        cataphatic_count = len(re.findall(cataphatic_pattern, content, re.IGNORECASE))
        apophatic_count = len(re.findall(apophatic_pattern, content, re.IGNORECASE))
        
        total = cataphatic_count + apophatic_count
        apophatic_ratio = apophatic_count / total if total > 0 else 0
        
        return TheologicalPattern(
            patristic_citations=patristic_citations,
            biblical_references=biblical,
            heresies_addressed=heresies_found,
            councils_referenced=councils_found,
            apophatic_cataphatic_ratio=apophatic_ratio
        )
    
    def _analyze_sections(self, content: str) -> List[SectionPattern]:
        """Extract patterns from each section"""
        
        # Split by section headers
        section_pattern = r'##\s+(I+|IV|V|VI)\.\s+([^\n]+)'
        sections = re.split(section_pattern, content)
        
        section_patterns = []
        
        # Process sections (they come in groups of 3: number, name, content)
        for i in range(1, len(sections), 3):
            if i+2 >= len(sections):
                break
            
            section_num = sections[i]
            section_name = sections[i+1]
            section_content = sections[i+2]
            
            # Skip if too short
            if len(section_content.strip()) < 100:
                continue
            
            # Get word count
            word_count = len(section_content.split())
            
            # Get opening sentence
            sentences = re.split(r'[.!?]+', section_content)
            opening = sentences[0].strip() if sentences else ""
            
            # Get closing sentence
            closing = sentences[-1].strip() if sentences else ""
            
            # Extract fathers cited in this section
            fathers = re.findall(
                r'(?:Saint|St\.)\s+([A-Za-z\s]+?)(?:\s+(?:writes|teaches|says))',
                section_content
            )
            fathers = list(set(fathers))[:10]
            
            # Try to extract key arguments (sentences with "therefore", "thus", "hence")
            argument_pattern = r'[A-Z][^.]*(?:therefore|thus|hence|consequently)[^.]*\.'
            arguments = re.findall(argument_pattern, section_content)
            
            # Identify rhetorical strategy
            if 'NOT' in section_content and 'BUT' in section_content:
                strategy = "Dialectical contrast"
            elif len(fathers) > 5:
                strategy = "Patristic synthesis"
            elif section_content.count('and') > 50:
                strategy = "Polysyndeton accumulation"
            else:
                strategy = "Expository"
            
            section_patterns.append(SectionPattern(
                section_number=section_num,
                section_name=section_name.strip(),
                word_count=word_count,
                opening_sentence=opening[:200],
                closing_sentence=closing[:200],
                main_fathers_cited=fathers,
                key_arguments=arguments[:5],
                rhetorical_strategy=strategy
            ))
        
        return section_patterns
    
    def _extract_sophisticated_terms(self, content: str) -> List[str]:
        """Find sophisticated theological vocabulary"""
        
        sophisticated_terms = {
            'soteriological', 'christological', 'pneumatological', 'ecclesiological',
            'eschatological', 'patristic', 'sacramental', 'liturgical', 'theosis',
            'perichoresis', 'homoousios', 'hypostatic', 'consubstantial', 'theandric',
            'apophatic', 'cataphatic', 'economia', 'theologia', 'synergistic',
            'transfiguration', 'kenosis', 'pleroma', 'parousia', 'epiklesis',
            'anaphora', 'eucharistic', 'doxological', 'trinitarian', 'incarnate'
        }
        
        found = []
        content_lower = content.lower()
        
        for term in sophisticated_terms:
            if term in content_lower:
                # Get actual usage (preserve capitalization)
                pattern = rf'\b{term}\b'
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found.append(matches[0])
        
        return list(set(found))
    
    def _extract_classical_terms(self, content: str) -> List[str]:
        """Find Greek/Latin terms"""
        
        # Look for Greek terms (often in transliteration or parentheses)
        greek_pattern = r'\(([αβγδεζηθικλμνξοπρστυφχψω\s]+)\)'
        greek = re.findall(greek_pattern, content)
        
        # Look for Latin phrases
        latin_phrases = [
            'ex nihilo', 'imago Dei', 'persona', 'substantia', 'hypostasis',
            'ousia', 'theotokos', 'theosis', 'logos', 'sophia'
        ]
        
        latin_found = []
        content_lower = content.lower()
        for phrase in latin_phrases:
            if phrase.lower() in content_lower:
                # Find actual usage
                pattern = rf'\b{re.escape(phrase)}\b'
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    latin_found.extend(matches)
        
        return list(set(greek + latin_found))
    
    def _calculate_overall_score(
        self,
        vocab: VocabularyPattern,
        sent: SentencePattern,
        rhet: RhetoricalPattern,
        theo: TheologicalPattern
    ) -> float:
        """Calculate overall quality score"""
        
        # Vocabulary score
        vocab_score = min(1.0, vocab.avg_word_length / 6.0) * 0.5
        vocab_score += (1.0 - min(1.0, vocab.simple_word_ratio / 0.2)) * 0.5
        vocab_score = vocab_score * 0.25
        
        # Sentence score
        sent_score = 1.0 - min(1.0, abs(sent.avg_sentence_length - 30) / 20)
        sent_score = sent_score * 0.20
        
        # Rhetorical score
        rhet_score = min(1.0, len(rhet.not_but_structures) / 15) * 0.4
        rhet_score += min(1.0, len(rhet.anaphora_patterns) / 5) * 0.3
        rhet_score += min(1.0, len(rhet.polysyndeton_examples) / 5) * 0.3
        rhet_score = rhet_score * 0.25
        
        # Theological score
        theo_score = min(1.0, len(theo.patristic_citations) / 50) * 0.5
        theo_score += min(1.0, len(theo.biblical_references) / 70) * 0.5
        theo_score = theo_score * 0.30
        
        overall = vocab_score + sent_score + rhet_score + theo_score
        
        return overall
    
    def _identify_special_features(
        self,
        content: str,
        sent: SentencePattern,
        rhet: RhetoricalPattern
    ) -> List[str]:
        """Identify unique features of this entry"""
        
        features = []
        
        # Epic sentences
        if len(sent.epic_sentences) > 5:
            features.append(f"Epic sentence mastery ({len(sent.epic_sentences)} sentences 100+ words)")
        
        # Polysyndeton
        if len(rhet.polysyndeton_examples) > 8:
            features.append(f"Extensive polysyndeton ({len(rhet.polysyndeton_examples)} chains)")
        
        # NOT...BUT
        if len(rhet.not_but_structures) > 15:
            features.append(f"Heavy dialectical contrast ({len(rhet.not_but_structures)} NOT...BUT)")
        
        # Section VI detection
        if 'AND NOW, in this Liturgy, at this Altar' in content:
            features.append("Section VI liturgical phrase present")
        
        # Doxological ending
        if re.search(r'ages of ages[,\.]?\s+Amen', content, re.IGNORECASE):
            features.append("Proper doxological ending")
        
        # Length
        word_count = len(content.split())
        if word_count > 15000:
            features.append(f"Exceptional length ({word_count:,} words)")
        
        return features
    
    def analyze_all_golden_entries(
        self,
        golden_dir: str,
        output_file: str = "golden_patterns.json"
    ) -> List[GoldenPattern]:
        """Analyze all golden entries in directory"""
        
        golden_path = Path(golden_dir)
        md_files = list(golden_path.glob("*.md"))
        
        print(f"\n{'='*80}")
        print(f"GOLDEN ENTRY PATTERN EXTRACTION")
        print(f"{'='*80}")
        print(f"\nFound {len(md_files)} golden entries to analyze\n")
        
        patterns = []
        for md_file in md_files:
            try:
                pattern = self.analyze_golden_entry(md_file)
                patterns.append(pattern)
            except Exception as e:
                print(f"✗ Error analyzing {md_file.name}: {e}")
        
        # Save patterns
        print(f"\n{'='*80}")
        print(f"Saving patterns to {output_file}...")
        
        # Convert to JSON-serializable format
        patterns_dict = {
            'patterns': [
                {
                    'entry_name': p.entry_name,
                    'overall_score': p.overall_score,
                    'vocabulary': asdict(p.vocabulary),
                    'sentences': {
                        **asdict(p.sentences),
                        'epic_sentences': [s[:200] + '...' for s in p.sentences.epic_sentences]
                    },
                    'rhetoric': asdict(p.rhetoric),
                    'theology': asdict(p.theology),
                    'sections': [asdict(s) for s in p.sections],
                    'special_features': p.special_features
                }
                for p in patterns
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(patterns_dict, f, indent=2)
        
        print(f"✓ Saved {len(patterns)} pattern analyses")
        
        # Print summary
        self._print_summary(patterns)
        
        return patterns
    
    def _print_summary(self, patterns: List[GoldenPattern]):
        """Print analysis summary"""
        
        print(f"\n{'='*80}")
        print(f"ANALYSIS SUMMARY")
        print(f"{'='*80}")
        
        if not patterns:
            print("No patterns analyzed")
            return
        
        # Average scores
        avg_overall = statistics.mean([p.overall_score for p in patterns])
        avg_vocab = statistics.mean([p.vocabulary.avg_word_length for p in patterns])
        avg_simple = statistics.mean([p.vocabulary.simple_word_ratio for p in patterns])
        avg_sent = statistics.mean([p.sentences.avg_sentence_length for p in patterns])
        avg_patristic = statistics.mean([len(p.theology.patristic_citations) for p in patterns])
        avg_biblical = statistics.mean([len(p.theology.biblical_references) for p in patterns])
        
        print(f"\nAverage Metrics Across All Golden Entries:")
        print(f"  Overall Quality Score: {avg_overall:.4f}")
        print(f"  Average Word Length: {avg_vocab:.2f} characters")
        print(f"  Simple Word Ratio: {avg_simple:.1%}")
        print(f"  Average Sentence Length: {avg_sent:.1f} words")
        print(f"  Patristic Citations: {avg_patristic:.0f}")
        print(f"  Biblical References: {avg_biblical:.0f}")
        
        # Top quality entries
        print(f"\nTop 5 Quality Entries:")
        sorted_patterns = sorted(patterns, key=lambda p: p.overall_score, reverse=True)
        for i, p in enumerate(sorted_patterns[:5], 1):
            print(f"  {i}. {p.entry_name}: {p.overall_score:.4f}")
        
        print(f"\n{'='*80}\n")


def main():
    """Run golden entry analysis"""
    
    analyzer = GoldenEntryAnalyzer()
    
    patterns = analyzer.analyze_all_golden_entries(
        golden_dir="Golden_Entries",
        output_file="golden_patterns.json"
    )
    
    print("✓ Golden entry analysis complete!")
    print("✓ Patterns saved to: golden_patterns.json")
    print("✓ Ready for template-guided generation")


if __name__ == "__main__":
    main()
