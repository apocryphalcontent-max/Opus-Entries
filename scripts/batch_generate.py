#!/usr/bin/env python3
"""
Batch entry generator - Sequential generation with thermal management
Implements CELESTIAL-tier mandate with iterative refinement
"""
import sys
import os
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from opus_entries import EntryGenerator, EntryValidator, EntryRefiner, CitationChecker


def batch_generate(topics, output_dir="output", model="mixtral:8x7b", celestial_only=True, max_refinement_attempts=3):
    """
    Generate multiple entries in batch with CELESTIAL-tier guarantee
    
    Args:
        topics: List of topics to generate
        output_dir: Directory to save generated entries
        model: LLM model to use
        celestial_only: If True, refine until CELESTIAL tier achieved
        max_refinement_attempts: Maximum refinement attempts per entry
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    generator = EntryGenerator()
    validator = EntryValidator()
    refiner = EntryRefiner()
    citation_checker = CitationChecker()
    
    # Statistics
    total_entries = len(topics)
    celestial_first_pass = 0
    celestial_after_refinement = 0
    failed_celestial = 0
    
    print(f"Starting batch generation of {total_entries} entries")
    print(f"Model: {model}")
    print(f"CELESTIAL mandate: {celestial_only}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{total_entries}] Generating: {topic}")
        start_time = time.time()
        
        # Phase 1: Initial generation
        print("  Phase 1: Initial generation...")
        entry = generator.generate(topic, model=model)
        
        # Phase 2: Initial validation
        print("  Phase 2: Validation...")
        result = validator.validate(entry)
        print(f"    Initial score: {result.score:.2f}/100 ({result.quality_tier.value})")
        
        # Phase 3: Citation quality check
        print("  Phase 3: Citation quality check...")
        citation_report = citation_checker.generate_citation_report(entry)
        print(f"    Citation composite score: {citation_report['scores']['composite']:.2f}/100")
        print(f"    Citation status: {citation_report['status']}")
        
        # Phase 4: Iterative refinement (if needed)
        if celestial_only and result.score < 95:
            print("  Phase 4: Iterative refinement to CELESTIAL tier...")
            entry = refiner.refine_to_celestial(entry, model=model, max_attempts=max_refinement_attempts)
            
            # Re-validate
            result = validator.validate(entry)
            print(f"    Final score: {result.score:.2f}/100 ({result.quality_tier.value})")
            
            if result.score >= 95:
                celestial_after_refinement += 1
            else:
                failed_celestial += 1
                print(f"    WARNING: Failed to achieve CELESTIAL after {max_refinement_attempts} attempts")
        elif result.score >= 95:
            celestial_first_pass += 1
        
        # Phase 5: Save entry
        filename = f"{topic.replace(' ', '_').replace('/', '_')}.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(entry.to_markdown())
        
        elapsed = time.time() - start_time
        print(f"  ✓ Completed in {elapsed/60:.1f} minutes")
        print(f"  Saved to: {filepath}")
        
        # Thermal management: Cool-down period between entries
        if i < total_entries:
            cooldown = 30  # seconds
            print(f"  Cooling down for {cooldown} seconds...")
            time.sleep(cooldown)
    
    # Final statistics
    print("\n" + "=" * 80)
    print("BATCH GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total entries: {total_entries}")
    print(f"CELESTIAL first-pass: {celestial_first_pass} ({celestial_first_pass/total_entries*100:.1f}%)")
    print(f"CELESTIAL after refinement: {celestial_after_refinement} ({celestial_after_refinement/total_entries*100:.1f}%)")
    print(f"Failed CELESTIAL: {failed_celestial} ({failed_celestial/total_entries*100:.1f}%)")
    print(f"Total CELESTIAL: {celestial_first_pass + celestial_after_refinement} ({(celestial_first_pass + celestial_after_refinement)/total_entries*100:.1f}%)")


if __name__ == "__main__":
    # Example: Generate 5 entries
    example_topics = [
        "The Nature of Infinity",
        "Divine Energies and Essence",
        "Theosis in Mathematics",
        "The Trinity and Quantum Mechanics",
        "Liturgical Time and Relativity"
    ]
    
    batch_generate(
        topics=example_topics,
        output_dir="output/batch_example",
        model="mixtral:8x7b",  # Change to your preferred model
        celestial_only=True,
        max_refinement_attempts=3
    )
