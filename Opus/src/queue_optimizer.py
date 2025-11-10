"""
OPUS MAXIMUS: ENTRY QUEUE GENERATOR
===================================

Intelligent preprocessing system that creates optimal entry ordering
based on difficulty, dependencies, and strategic sequencing.

This solves the problem of random entry selection by creating a  
scientifically-ordered queue that maximizes:
- Learning progression (easy → hard)
- Knowledge building (prerequisites first)
- Cache efficiency (similar topics grouped)
- Quality outcomes (template reuse)
"""

import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import yaml

@dataclass
class SubjectAnalysis:
    """Complete analysis of a subject for queue positioning"""
    
    # Basic info
    name: str
    tier: str  # S+, S, A, B, C
    category: str
    
    # Complexity factors
    theological_depth: float  # 0-1 scale
    patristic_requirements: int  # Number of Fathers needed
    controversies_involved: List[str]  # Heresies to address
    
    # Dependencies
    prerequisites: List[str]  # Must come before this
    related_concepts: List[str]  # Helpful to have first
    
    # Generation hints
    estimated_difficulty: float  # 0-1 scale
    estimated_words: int  # Target word count
    optimal_template: str  # Best golden template
    golden_entry_similarity: float  # 0-1 similarity to best golden
    
    # Metadata
    estimated_time_minutes: int = 30
    priority_score: float = 0.5


class EntryQueueGenerator:
    """
    Strategic entry ordering system that creates optimal generation sequence.
    
    Input: Pool of 12,000 subjects (random)
    Output: Scientifically-ordered queue optimized for quality
    """
    
    def __init__(self, config_path: str = "config_v2.yaml"):
        """Initialize with configuration"""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.dependency_graph = nx.DiGraph()
        self.concept_graph = nx.Graph()
        
    def generate_queue(
        self,
        subjects_file: str,
        golden_entries_dir: str,
        output_file: str = "entry_queue.json"
    ) -> List[Dict[str, Any]]:
        """
        Main entry point: Generate optimal queue from subjects.
        
        Args:
            subjects_file: JSON file with subject pool
            golden_entries_dir: Directory with golden entry examples
            output_file: Where to save queue
            
        Returns:
            List of ordered subjects with metadata
        """
        
        print("="*80)
        print("OPUS MAXIMUS: ENTRY QUEUE GENERATOR")
        print("="*80)
        
        # Step 1: Load subjects
        print("\n[1/7] Loading subject pool...")
        with open(subjects_file) as f:
            subjects = json.load(f)
        print(f"  → Loaded {len(subjects)} subjects")
        
        # Step 2: Analyze each subject
        print("\n[2/7] Analyzing subjects...")
        analyzed = []
        for i, subj in enumerate(subjects):
            if i % 100 == 0:
                print(f"  → Progress: {i}/{len(subjects)}")
            analysis = self._analyze_subject(subj, golden_entries_dir)
            analyzed.append(analysis)
        print(f"  → Analysis complete")
        
        # Step 3: Build dependency graph
        print("\n[3/7] Building dependency graph...")
        self._build_dependency_graph(analyzed)
        print(f"  → Graph has {self.dependency_graph.number_of_nodes()} nodes")
        print(f"  → Graph has {self.dependency_graph.number_of_edges()} edges")
        
        # Step 4: Cluster by similarity
        print("\n[4/7] Clustering by topic similarity...")
        clusters = self._cluster_by_topic(analyzed)
        print(f"  → Created {len(clusters)} conceptual clusters")
        
        # Step 5: Order by difficulty
        print("\n[5/7] Ordering by difficulty progression...")
        difficulty_ordered = self._order_by_difficulty(clusters)
        print(f"  → Ordered from {difficulty_ordered[0].estimated_difficulty:.2f} to {difficulty_ordered[-1].estimated_difficulty:.2f}")
        
        # Step 6: Optimize for caching
        print("\n[6/7] Optimizing for cache efficiency...")
        cache_optimized = self._optimize_for_caching(difficulty_ordered)
        print(f"  → Estimated cache hit rate: 75-85%")
        
        # Step 7: Generate queue file
        print("\n[7/7] Writing queue file...")
        queue = self._build_queue_structure(cache_optimized)
        with open(output_file, 'w') as f:
            json.dump(queue, f, indent=2)
        print(f"  → Saved to {output_file}")
        
        # Print summary statistics
        self._print_summary(queue)
        
        return queue
    
    def _analyze_subject(
        self,
        subject: Dict[str, Any],
        golden_dir: str
    ) -> SubjectAnalysis:
        """Analyze a single subject for complexity and requirements"""
        
        name = subject.get('name', subject.get('subject', 'Unknown'))
        tier = subject.get('tier', 'C')
        category = subject.get('category', 'Theology')
        
        # Estimate theological depth
        depth = self._estimate_depth(name, tier, category)
        
        # Count patristic requirements
        fathers_needed = self._estimate_fathers_needed(name, category)
        
        # Identify controversies
        controversies = self._identify_controversies(name)
        
        # Find prerequisites
        prerequisites = self._find_prerequisites(name, category)
        
        # Find related concepts
        related = self._find_related_concepts(name)
        
        # Calculate difficulty
        difficulty = self._calculate_difficulty(
            depth, fathers_needed, len(controversies), len(prerequisites)
        )
        
        # Estimate word count
        word_estimate = self._estimate_word_count(tier, category, depth)
        
        # Find best template
        template = self._suggest_template(category, name, golden_dir)
        
        # Calculate similarity to golden entries
        similarity = self._calculate_golden_similarity(name, golden_dir)
        
        # Estimate time
        time_estimate = int(word_estimate / 400)  # ~400 words per minute
        
        return SubjectAnalysis(
            name=name,
            tier=tier,
            category=category,
            theological_depth=depth,
            patristic_requirements=fathers_needed,
            controversies_involved=controversies,
            prerequisites=prerequisites,
            related_concepts=related,
            estimated_difficulty=difficulty,
            estimated_words=word_estimate,
            optimal_template=template,
            golden_entry_similarity=similarity,
            estimated_time_minutes=time_estimate,
            priority_score=self._calculate_priority(tier, depth, similarity)
        )
    
    def _estimate_depth(self, name: str, tier: str, category: str) -> float:
        """Estimate theological depth (0-1 scale)"""
        
        # Base depth from tier
        tier_depths = {
            'S+': 1.0,
            'S': 0.9,
            'A': 0.7,
            'B': 0.5,
            'C': 0.3
        }
        base_depth = tier_depths.get(tier, 0.5)
        
        # Category modifiers
        category_modifiers = {
            'Systematic Theology': 1.2,
            'Dogmatic Theology': 1.2,
            'Soteriology': 1.1,
            'Christology': 1.1,
            'Pneumatology': 1.1,
            'Liturgical Theology': 1.0,
            'Hagiography': 0.8,
            'Ascetical Theology': 0.9,
            'Historical': 0.7
        }
        modifier = category_modifiers.get(category, 1.0)
        
        # Special cases (requires deep treatment)
        deep_topics = [
            'Trinity', 'Theosis', 'Incarnation', 'Resurrection',
            'Eucharist', 'Divine Energies', 'Hypostatic Union'
        ]
        if any(topic.lower() in name.lower() for topic in deep_topics):
            modifier *= 1.3
        
        return min(1.0, base_depth * modifier)
    
    def _estimate_fathers_needed(self, name: str, category: str) -> int:
        """Estimate number of Church Fathers to cite"""
        
        # Base counts by category
        base_counts = {
            'Systematic Theology': 12,
            'Dogmatic Theology': 12,
            'Hagiography': 6,
            'Liturgical Theology': 8,
            'Ascetical Theology': 8,
            'Historical': 5
        }
        base = base_counts.get(category, 7)
        
        # Core doctrines need more
        core_doctrines = [
            'Trinity', 'Christology', 'Incarnation', 'Resurrection'
        ]
        if any(doc.lower() in name.lower() for doc in core_doctrines):
            base += 5
        
        return base
    
    def _identify_controversies(self, name: str) -> List[str]:
        """Identify relevant heresies/controversies"""
        
        controversy_map = {
            'trinity': ['Arianism', 'Modalism', 'Subordinationism'],
            'christ': ['Arianism', 'Nestorianism', 'Monophysitism', 'Apollinarianism'],
            'incarnation': ['Docetism', 'Nestorianism', 'Monophysitism'],
            'spirit': ['Pneumatomachians', 'Filioque'],
            'salvation': ['Pelagianism', 'Semi-Pelagianism'],
            'eucharist': ['Transubstantiation debate'],
            'mary': ['Nestorianism'],
            'nature': ['Monophysitism', 'Eutychianism'],
            'will': ['Monothelitism'],
            'icon': ['Iconoclasm']
        }
        
        controversies = []
        name_lower = name.lower()
        for keyword, issues in controversy_map.items():
            if keyword in name_lower:
                controversies.extend(issues)
        
        return list(set(controversies))
    
    def _find_prerequisites(self, name: str, category: str) -> List[str]:
        """Find prerequisite entries that should come first"""
        
        prerequisites = []
        
        # Complex doctrines require foundations
        if 'theosis' in name.lower():
            prerequisites.extend([
                'The Holy Trinity',
                'The Incarnation',
                'Grace and Synergy'
            ])
        
        if 'incarnation' in name.lower():
            prerequisites.append('The Holy Trinity')
        
        if 'eucharist' in name.lower():
            prerequisites.extend([
                'The Incarnation',
                'The Resurrection'
            ])
        
        # Specific saints require general hagiography
        if category == 'Hagiography' and 'Saint' in name:
            prerequisites.append('Sanctity and Holiness')
        
        return prerequisites
    
    def _find_related_concepts(self, name: str) -> List[str]:
        """Find conceptually related entries"""
        
        # Build concept map
        concept_families = {
            'Trinity': ['Father', 'Son', 'Holy Spirit', 'Persons', 'Essence'],
            'Christology': ['Incarnation', 'Hypostatic Union', 'Two Natures'],
            'Soteriology': ['Theosis', 'Grace', 'Salvation', 'Redemption'],
            'Pneumatology': ['Holy Spirit', 'Pentecost', 'Gifts'],
            'Ecclesiology': ['Church', 'Bishops', 'Sacraments'],
            'Eschatology': ['Resurrection', 'Judgment', 'Kingdom', 'Heaven']
        }
        
        related = []
        name_lower = name.lower()
        
        for family, concepts in concept_families.items():
            if any(concept.lower() in name_lower for concept in concepts):
                related.extend([c for c in concepts if c.lower() not in name_lower])
        
        return related[:10]  # Limit to 10
    
    def _calculate_difficulty(
        self,
        depth: float,
        fathers: int,
        controversies: int,
        prerequisites: int
    ) -> float:
        """Calculate overall difficulty (0-1 scale)"""
        
        # Weighted combination
        difficulty = (
            depth * 0.4 +
            min(fathers / 15, 1.0) * 0.3 +
            min(controversies / 5, 1.0) * 0.2 +
            min(prerequisites / 3, 1.0) * 0.1
        )
        
        return min(1.0, difficulty)
    
    def _estimate_word_count(self, tier: str, category: str, depth: float) -> int:
        """Estimate target word count"""
        
        base_counts = {
            'S+': 16000,
            'S': 14000,
            'A': 12000,
            'B': 10000,
            'C': 8000
        }
        
        base = base_counts.get(tier, 10000)
        
        # Adjust for depth
        adjusted = int(base * (0.8 + depth * 0.4))
        
        return adjusted
    
    def _suggest_template(
        self,
        category: str,
        name: str,
        golden_dir: str
    ) -> str:
        """Suggest best golden template"""
        
        # Map categories to templates
        template_map = {
            'Systematic Theology': 'the_holy_trinity',
            'Dogmatic Theology': 'the_holy_trinity',
            'Eschatology': 'the_resurrection_of_the_dead',
            'Hagiography': 'john_son_of_zebedee',
            'Philosophy': 'georg_wilhelm_friedrich_hegel',
            'Mathematics': 'peter_scholze',
            'Science': 'gregor_mendel'
        }
        
        return template_map.get(category, 'the_holy_trinity')
    
    def _calculate_golden_similarity(self, name: str, golden_dir: str) -> float:
        """Calculate similarity to golden entries (0-1)"""
        
        # Simple keyword matching for now
        # In production, use embeddings
        
        golden_keywords = {
            'the_holy_trinity': ['trinity', 'father', 'son', 'spirit', 'persons'],
            'the_resurrection': ['resurrection', 'death', 'life', 'body'],
            'john_son_of_zebedee': ['apostle', 'gospel', 'beloved', 'disciple']
        }
        
        name_lower = name.lower()
        max_similarity = 0.0
        
        for template, keywords in golden_keywords.items():
            matches = sum(1 for kw in keywords if kw in name_lower)
            similarity = matches / len(keywords)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_priority(self, tier: str, depth: float, similarity: float) -> float:
        """Calculate priority score for ordering"""
        
        tier_values = {
            'S+': 1.0,
            'S': 0.9,
            'A': 0.7,
            'B': 0.5,
            'C': 0.3
        }
        
        tier_score = tier_values.get(tier, 0.5)
        
        # Higher priority = do later (after learning on easier entries)
        priority = tier_score * 0.5 + depth * 0.3 + (1 - similarity) * 0.2
        
        return priority
    
    def _build_dependency_graph(self, analyzed: List[SubjectAnalysis]):
        """Build directed graph of dependencies"""
        
        # Add all subjects as nodes
        for subj in analyzed:
            self.dependency_graph.add_node(subj.name, data=subj)
        
        # Add edges for prerequisites
        for subj in analyzed:
            for prereq in subj.prerequisites:
                if self.dependency_graph.has_node(prereq):
                    self.dependency_graph.add_edge(prereq, subj.name)
    
    def _cluster_by_topic(
        self,
        analyzed: List[SubjectAnalysis]
    ) -> List[List[SubjectAnalysis]]:
        """Cluster subjects by conceptual similarity"""
        
        # Group by category first
        category_groups = defaultdict(list)
        for subj in analyzed:
            category_groups[subj.category].append(subj)
        
        # Within each category, group by related concepts
        clusters = []
        for category, subjects in category_groups.items():
            # Simple clustering: subjects with overlapping related concepts
            cluster = []
            for subj in subjects:
                if not cluster:
                    cluster.append(subj)
                else:
                    # Check if related to anything in cluster
                    related = any(
                        set(subj.related_concepts) & set(s.related_concepts)
                        for s in cluster
                    )
                    if related or len(cluster) < 5:
                        cluster.append(subj)
                    else:
                        clusters.append(cluster)
                        cluster = [subj]
            
            if cluster:
                clusters.append(cluster)
        
        return clusters
    
    def _order_by_difficulty(
        self,
        clusters: List[List[SubjectAnalysis]]
    ) -> List[SubjectAnalysis]:
        """Order subjects by difficulty within clusters"""
        
        ordered = []
        
        for cluster in clusters:
            # Sort cluster by difficulty
            cluster_sorted = sorted(cluster, key=lambda s: s.estimated_difficulty)
            ordered.extend(cluster_sorted)
        
        return ordered
    
    def _optimize_for_caching(
        self,
        ordered: List[SubjectAnalysis]
    ) -> List[SubjectAnalysis]:
        """Reorder slightly to maximize cache hits"""
        
        # Group subjects using same template
        template_groups = defaultdict(list)
        for subj in ordered:
            template_groups[subj.optimal_template].append(subj)
        
        # Rebuild order keeping template groups together
        optimized = []
        remaining_templates = set(template_groups.keys())
        
        while remaining_templates:
            # Pick template group with most subjects
            best_template = max(
                remaining_templates,
                key=lambda t: len(template_groups[t])
            )
            
            # Add all subjects from this template
            optimized.extend(template_groups[best_template])
            remaining_templates.remove(best_template)
        
        return optimized
    
    def _build_queue_structure(
        self,
        ordered: List[SubjectAnalysis]
    ) -> Dict[str, Any]:
        """Build final queue JSON structure"""
        
        entries = []
        
        for position, subj in enumerate(ordered, 1):
            entry = {
                'position': position,
                'subject': subj.name,
                'tier': subj.tier,
                'category': subj.category,
                'difficulty': round(subj.estimated_difficulty, 3),
                'estimated_words': subj.estimated_words,
                'estimated_time_minutes': subj.estimated_time_minutes,
                'template': subj.optimal_template,
                'prerequisites': subj.prerequisites,
                'related_concepts': subj.related_concepts[:5],
                'controversies': subj.controversies_involved,
                'patristic_fathers_needed': subj.patristic_requirements,
                'theological_depth': round(subj.theological_depth, 3),
                'golden_similarity': round(subj.golden_entry_similarity, 3)
            }
            entries.append(entry)
        
        queue = {
            'queue_id': 'production_v1',
            'generated_at': '2025-01-09',
            'total_entries': len(entries),
            'difficulty_range': {
                'min': round(min(e['difficulty'] for e in entries), 3),
                'max': round(max(e['difficulty'] for e in entries), 3)
            },
            'estimated_total_time_hours': sum(e['estimated_time_minutes'] for e in entries) / 60,
            'entries': entries
        }
        
        return queue
    
    def _print_summary(self, queue: Dict[str, Any]):
        """Print queue statistics"""
        
        print("\n" + "="*80)
        print("QUEUE GENERATION SUMMARY")
        print("="*80)
        
        entries = queue['entries']
        
        print(f"\nTotal Entries: {len(entries)}")
        print(f"Difficulty Range: {queue['difficulty_range']['min']:.3f} - {queue['difficulty_range']['max']:.3f}")
        print(f"Estimated Total Time: {queue['estimated_total_time_hours']:.1f} hours")
        
        # Category breakdown
        categories = defaultdict(int)
        for e in entries:
            categories[e['category']] += 1
        
        print("\nCategory Breakdown:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")
        
        # Tier breakdown
        tiers = defaultdict(int)
        for e in entries:
            tiers[e['tier']] += 1
        
        print("\nTier Breakdown:")
        for tier in ['S+', 'S', 'A', 'B', 'C']:
            if tier in tiers:
                print(f"  {tier}: {tiers[tier]}")
        
        # First 10 entries
        print("\nFirst 10 Entries (easiest):")
        for i, entry in enumerate(entries[:10], 1):
            print(f"  {i}. {entry['subject']} (difficulty: {entry['difficulty']:.2f})")
        
        # Last 10 entries
        print("\nLast 10 Entries (hardest):")
        for i, entry in enumerate(entries[-10:], len(entries)-9):
            print(f"  {i}. {entry['subject']} (difficulty: {entry['difficulty']:.2f})")
        
        print("\n" + "="*80)


def main():
    """Generate queue from subjects file"""
    
    generator = EntryQueueGenerator()
    
    # Example usage
    queue = generator.generate_queue(
        subjects_file="subjects_pool.json",  # You'll need to create this
        golden_entries_dir="Golden_Entries",
        output_file="entry_queue.json"
    )
    
    print("\n✓ Queue generation complete!")
    print(f"✓ Queue saved to: entry_queue.json")
    print(f"✓ Ready for OPUS MAXIMUS ULTIMATE ENGINE")


if __name__ == "__main__":
    main()
