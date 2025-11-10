# Opus-Entries

A comprehensive entry generator system that produces detailed theological, mathematical, scientific, and philosophical entries from an Orthodox Christian perspective.

## Features

- **Comprehensive Entries**: Generates entries of 11,000-14,000 words covering Orthodox theology, mathematics, science, and philosophy
- **Six-Section Structure**: Each entry includes:
  1. Introduction
  2. The Patristic Mind
  3. Symphony of Clashes
  4. Orthodox Affirmation
  5. Synthesis
  6. Conclusion
- **Local LLM Integration**: Uses local language models for content generation
- **Quality-Tiered System**: Validation-based quality tiers (CELESTIAL, ADAMANTINE, PLATINUM, GOLD, SILVER, BRONZE)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Generate an entry:
```bash
python -m opus_entries.cli generate --topic "The Nature of Infinity"
```

Generate an entry with specific model:
```bash
python -m opus_entries.cli generate --topic "Mathematics and Theology" --model "llama2"
```

## Configuration

Configuration is managed through `config.json` or environment variables. Key settings:
- LLM model selection
- Target word count range
- Quality tier thresholds
- Section parameters

## Quality Tiers

Entries are assigned quality tiers based on validation scores:
- **CELESTIAL** (95-100): Exceptional theological depth and coherence
- **ADAMANTINE** (90-94): Outstanding quality and insight
- **PLATINUM** (85-89): Excellent comprehensive coverage
- **GOLD** (80-84): Very good quality
- **SILVER** (75-79): Good quality
- **BRONZE** (70-74): Acceptable quality

## License

MIT