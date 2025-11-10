#!/usr/bin/env python3
"""
Quick test script for Opus Maximus v2
Demonstrates the complete generation pipeline
"""

import sys
sys.path.insert(0, '.')

from opus_maximus_v2 import OpusMaximusEngine, OpusConfig
import json

def main():
    print("="*80)
    print("OPUS MAXIMUS DREAM ENGINE v2.0 - TEST EXECUTION")
    print("="*80)
    print()
    
    # Create configuration
    print("Initializing configuration...")
    config = OpusConfig(
        model_path="models/nous-hermes-2-mixtral.gguf",
        n_ctx=16384,
        n_gpu_layers=-1,
        n_threads=16,
        min_total_words=10000,
        max_total_words=15000
    )
    
    print(f"✓ Context window: {config.n_ctx}")
    print(f"✓ GPU layers: {config.n_gpu_layers}")
    print(f"✓ CPU threads: {config.n_threads}")
    print(f"✓ Target word count: {config.min_total_words}-{config.max_total_words}")
    print()
    
    # Initialize engine
    print("Initializing Opus Maximus Engine...")
    engine = OpusMaximusEngine(config)
    print("✓ Engine initialized")
    print("✓ Multi-tier cache ready")
    print("✓ Validators loaded")
    print()
    
    # Test subjects
    test_subjects = [
        {
            "subject": "Theosis",
            "tier": "Tier 1",
            "category": "Soteriology"
        },
        {
            "subject": "The Divine Liturgy",
            "tier": "Tier 1",
            "category": "Liturgical Theology"
        },
        {
            "subject": "Saint Maximus the Confessor",
            "tier": "Tier 1",
            "category": "Hagiography"
        }
    ]
    
    print("Test subjects queued:")
    for i, subj in enumerate(test_subjects, 1):
        print(f"  {i}. {subj['subject']} ({subj['tier']}, {subj['category']})")
    print()
    
    # Generate first entry
    print("="*80)
    print("GENERATING ENTRY 1: Theosis")
    print("="*80)
    print()
    
    result = engine.generate_entry(**test_subjects[0])
    
    # Display results
    print()
    print("="*80)
    print("GENERATION RESULTS")
    print("="*80)
    print()
    
    print(f"Subject: {result['subject']}")
    print(f"Tier: {result['tier']}")
    print(f"Category: {result['category']}")
    print(f"Word Count: {result['word_count']:,}")
    print(f"Generation Time: {result['generation_time_seconds']:.2f}s")
    print(f"Timestamp: {result['timestamp']}")
    print()
    
    # Validation report
    validation = result['validation']
    print("VALIDATION REPORT:")
    print(f"  Status: {'PASSED ✓' if validation['valid'] else 'FAILED ✗'}")
    print()
    
    if validation['errors']:
        print(f"  Errors: {len(validation['errors'])}")
        for i, error in enumerate(validation['errors'][:5], 1):
            print(f"    {i}. {error}")
        if len(validation['errors']) > 5:
            print(f"    ... and {len(validation['errors']) - 5} more")
        print()
    
    if validation['warnings']:
        print(f"  Warnings: {len(validation['warnings'])}")
        for i, warning in enumerate(validation['warnings'][:3], 1):
            print(f"    {i}. {warning}")
        if len(validation['warnings']) > 3:
            print(f"    ... and {len(validation['warnings']) - 3} more")
        print()
    
    # Metrics
    if validation['metrics']:
        print("  Metrics:")
        for key, value in validation['metrics'].items():
            if isinstance(value, float):
                print(f"    {key}: {value:.2f}")
            else:
                print(f"    {key}: {value}")
        print()
    
    # Content preview
    print("CONTENT PREVIEW (first 500 characters):")
    print("-" * 80)
    preview = result['content'][:500].replace('\n', '\n')
    print(preview)
    print("...")
    print("-" * 80)
    print()
    
    # Save summary
    summary_file = config.output_dir / "generation_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_run': True,
            'timestamp': result['timestamp'],
            'results': {
                'subject': result['subject'],
                'word_count': result['word_count'],
                'generation_time': result['generation_time_seconds'],
                'validation_passed': validation['valid'],
                'error_count': len(validation['errors']),
                'warning_count': len(validation['warnings'])
            }
        }, f, indent=2)
    
    print(f"✓ Summary saved to: {summary_file}")
    print()
    
    # Cache statistics
    print("CACHE STATISTICS:")
    print(f"  L1 Cache: {len(engine.cache.l1_cache)} items")
    print(f"  L2 Cache: {len(engine.cache.l2_cache)} items")
    print(f"  Cache Hits: {engine.cache.hit_count}")
    print(f"  Cache Misses: {engine.cache.miss_count}")
    if engine.cache.hit_count + engine.cache.miss_count > 0:
        hit_rate = engine.cache.hit_count / (engine.cache.hit_count + engine.cache.miss_count)
        print(f"  Hit Rate: {hit_rate:.1%}")
    print()
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Check GENERATED_ENTRIES_MASTER/ for output files")
    print("  2. Review validation warnings/errors")
    print("  3. Integrate real LLM for production use")
    print("  4. Add your custom patristic corpus")
    print("  5. Enable advanced features (ensemble, human review, etc.)")
    print()

if __name__ == "__main__":
    main()
