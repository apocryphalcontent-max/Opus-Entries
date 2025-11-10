"""
Command-line interface for Opus-Entries with CELESTIAL-tier mandate
"""
import argparse
import sys
from pathlib import Path

from .generator import EntryGenerator
from .validator import EntryValidator
from .refiner import EntryRefiner
from .citation_checker import CitationChecker
from .config import Config


def generate_command(args):
    """Handle the generate command with CELESTIAL mandate"""
    # Initialize components
    config = Config(args.config) if args.config else Config()
    generator = EntryGenerator(config=config)
    validator = EntryValidator(config=config)
    refiner = EntryRefiner(config=config)
    citation_checker = CitationChecker()
    
    print(f"Generating entry on: {args.topic}")
    print(f"Model: {args.model}")
    print(f"CELESTIAL mandate: {args.celestial_only}")
    print("=" * 80)
    
    # Phase 1: Generate
    print("\nPhase 1: Generating entry...")
    entry = generator.generate(args.topic, model=args.model)
    print(f"  Generated {entry.total_word_count} words across {len(entry.sections)} sections")
    
    # Phase 2: Validate
    print("\nPhase 2: Validating...")
    result = validator.validate(entry)
    print(f"  Score: {result.score:.2f}/100")
    print(f"  Tier: {result.quality_tier.value}")
    
    # Phase 3: Refinement if needed
    if args.celestial_only and result.score < 95:
        print(f"\nPhase 3: Iterative refinement to CELESTIAL tier...")
        entry = refiner.refine_to_celestial(entry, model=args.model, max_attempts=args.max_refinement_attempts)
        result = validator.validate(entry)
        print(f"  Final score: {result.score:.2f}/100 ({result.quality_tier.value})")
    
    # Save
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        safe_topic = args.topic.replace(' ', '_').replace('/', '_')
        output_path = output_dir / f"{safe_topic}.md"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(entry.to_markdown())
    
    print(f"\n✓ Entry saved to: {output_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Opus-Entries: Orthodox Christian Entry Generator")
    subparsers = parser.add_subparsers(dest='command')
    
    generate_parser = subparsers.add_parser('generate')
    generate_parser.add_argument('--topic', required=True)
    generate_parser.add_argument('--model', default='llama2')
    generate_parser.add_argument('--output', '-o')
    generate_parser.add_argument('--config')
    generate_parser.add_argument('--celestial-only', action='store_true', default=True)
    generate_parser.add_argument('--no-celestial-mandate', dest='celestial_only', action='store_false')
    generate_parser.add_argument('--max-refinement-attempts', type=int, default=3)
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generate_command(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
