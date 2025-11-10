"""
Command-line interface for Opus-Entries
"""
import argparse
import os
import sys
from pathlib import Path

from .generator import EntryGenerator
from .validator import EntryValidator
from .config import Config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Opus-Entries: Generate comprehensive Orthodox Christian perspective entries"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a new entry")
    generate_parser.add_argument("--topic", required=True, help="Topic for the entry")
    generate_parser.add_argument("--model", help="LLM model to use (default: from config)")
    generate_parser.add_argument("--output", help="Output file path (default: output/{topic}.md)")
    generate_parser.add_argument("--config", help="Path to config file (default: config.json)")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an existing entry")
    validate_parser.add_argument("--input", required=True, help="Path to entry file")
    validate_parser.add_argument("--config", help="Path to config file (default: config.json)")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        generate_entry(args)
    elif args.command == "validate":
        validate_entry(args)
    else:
        parser.print_help()
        sys.exit(1)


def generate_entry(args):
    """Generate a new entry"""
    # Load configuration
    config_path = args.config or "config.json"
    config = Config(config_path)
    
    # Initialize generator and validator
    generator = EntryGenerator(config)
    validator = EntryValidator(config)
    
    print(f"Generating entry on topic: {args.topic}")
    print("This may take several minutes depending on the LLM model...")
    
    # Check LLM connection
    if not generator.llm_client.check_connection():
        print("\nWarning: LLM service not available. Using fallback mode.")
        print("For full functionality, ensure Ollama or compatible service is running.")
        print()
    
    # Generate entry
    entry = generator.generate(args.topic, args.model)
    
    print(f"\nEntry generated with {entry.total_word_count} words")
    
    # Validate entry
    print("Validating entry...")
    validation_result = validator.validate(entry)
    
    print(f"\nValidation Results:")
    print(f"  Overall Score: {validation_result.score:.2f}/100")
    print(f"  Quality Tier: {validation_result.quality_tier.value}")
    print(f"\nComponent Scores:")
    print(f"  Word Count: {validation_result.word_count_score:.2f}/100")
    print(f"  Theological Depth: {validation_result.theological_depth_score:.2f}/100")
    print(f"  Coherence: {validation_result.coherence_score:.2f}/100")
    print(f"  Section Balance: {validation_result.section_balance_score:.2f}/100")
    print(f"  Orthodox Perspective: {validation_result.orthodox_perspective_score:.2f}/100")
    
    if validation_result.feedback:
        print(f"\nFeedback:")
        for feedback_item in validation_result.feedback:
            print(f"  - {feedback_item}")
    
    # Save entry
    if args.output:
        output_path = args.output
    else:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Sanitize topic for filename
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in args.topic)
        safe_topic = safe_topic.replace(' ', '_')
        output_path = output_dir / f"{safe_topic}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(entry.to_markdown())
    
    print(f"\nEntry saved to: {output_path}")


def validate_entry(args):
    """Validate an existing entry"""
    print(f"Validating entry from: {args.input}")
    print("Note: This is a placeholder. Full validation requires parsing the entry file.")
    # This would require implementing entry parsing from markdown
    # For now, it's a placeholder for the interface


if __name__ == "__main__":
    main()
