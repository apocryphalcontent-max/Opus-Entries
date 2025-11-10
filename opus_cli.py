#!/usr/bin/env python3
"""
OPUS MAXIMUS - Command Line Interface
======================================
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "Opus" / "src"))

from opus_engine import create_engine_from_config
from batch_processor import run_batch_from_cli


def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('opus_maximus.log')
        ]
    )


def cmd_generate(args):
    """Generate single entry"""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Generating entry: {args.subject}")

    # Load engine
    config_path = Path(args.config)
    engine = create_engine_from_config(config_path)

    # Generate
    result = engine.generate_entry(
        subject=args.subject,
        tier=args.tier,
        category=args.category,
        resume=not args.no_resume
    )

    # Print results
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"Subject: {result.subject}")
    print(f"Word count: {result.word_count}")
    print(f"Generation time: {result.generation_time_seconds:.1f}s")
    print(f"Quality score: {result.validation['score']:.3f}")
    print(f"Errors: {len(result.validation['errors'])}")
    print(f"Warnings: {len(result.validation['warnings'])}")
    print("="*70 + "\n")

    if result.validation['errors']:
        print("ERRORS:")
        for error in result.validation['errors'][:5]:
            print(f"  - {error}")
        if len(result.validation['errors']) > 5:
            print(f"  ... and {len(result.validation['errors']) - 5} more")
        print()

    print(f"✓ Entry saved to: {engine.config.output_dir}")


def cmd_batch(args):
    """Process batch of entries"""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting batch processing: {args.pool}")

    run_batch_from_cli(
        config_path=Path(args.config),
        pool_file=Path(args.pool),
        start=args.start,
        max_entries=args.max,
        skip_existing=not args.no_skip
    )


def cmd_validate(args):
    """Validate existing entry"""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"Validating entry: {args.file}")

    # Load entry
    entry_file = Path(args.file)
    if not entry_file.exists():
        print(f"Error: File not found: {entry_file}")
        sys.exit(1)

    with open(entry_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Load engine (for validators)
    config_path = Path(args.config)
    engine = create_engine_from_config(config_path)

    # Validate
    result = engine._validate_entry(content)

    # Print results
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    print(f"Score: {result.score:.3f}")
    print(f"Valid: {'✓ YES' if result.valid else '✗ NO'}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print()

    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  - {error}")
        print()

    if result.warnings and args.verbose:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  - {warning}")
        print()

    print("METRICS:")
    for key, value in result.metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("="*70 + "\n")


def cmd_cache_stats(args):
    """Show cache statistics"""
    setup_logging(args.verbose)

    # Load engine
    config_path = Path(args.config)
    engine = create_engine_from_config(config_path)

    if engine.cache:
        engine.cache.print_stats()
    else:
        print("Caching is disabled")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Opus Maximus - Theological Encyclopedia Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single entry
  opus_cli.py generate --subject "Theosis" --tier "Tier 1"

  # Process batch
  opus_cli.py batch --pool Opus/data/subjects/pool_12000.json --max 10

  # Validate entry
  opus_cli.py validate --file GENERATED_ENTRIES_MASTER/Tier_1/Theosis.md

  # Show cache stats
  opus_cli.py cache-stats
        """
    )

    parser.add_argument(
        '--config',
        default='Opus/config/config.yaml',
        help='Path to configuration file (default: Opus/config/config.yaml)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate single entry')
    gen_parser.add_argument('--subject', required=True, help='Subject to generate')
    gen_parser.add_argument('--tier', default='Tier 1', help='Entry tier')
    gen_parser.add_argument('--category', default='Theology', help='Entry category')
    gen_parser.add_argument('--no-resume', action='store_true', help='Disable resume from checkpoint')
    gen_parser.set_defaults(func=cmd_generate)

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Process batch of entries')
    batch_parser.add_argument('--pool', required=True, help='Subject pool JSON file')
    batch_parser.add_argument('--start', type=int, default=0, help='Start index')
    batch_parser.add_argument('--max', type=int, help='Maximum entries to process')
    batch_parser.add_argument('--no-skip', action='store_true', help='Do not skip existing entries')
    batch_parser.set_defaults(func=cmd_batch)

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate existing entry')
    val_parser.add_argument('--file', required=True, help='Entry file to validate')
    val_parser.set_defaults(func=cmd_validate)

    # Cache stats command
    cache_parser = subparsers.add_parser('cache-stats', help='Show cache statistics')
    cache_parser.set_defaults(func=cmd_cache_stats)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
