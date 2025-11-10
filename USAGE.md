# Usage Guide

## Basic Usage

### Generating an Entry

To generate a comprehensive entry on a topic:

```bash
python -m opus_entries.cli generate --topic "The Nature of Infinity"
```

This will:
1. Generate content for all 6 sections
2. Validate the entry
3. Calculate quality scores
4. Assign a quality tier
5. Save the entry to `output/{topic}.md`

### Specifying a Model

Use a specific LLM model:

```bash
python -m opus_entries.cli generate --topic "Mathematics and Theology" --model "mistral"
```

### Custom Output Path

Specify where to save the entry:

```bash
python -m opus_entries.cli generate --topic "Divine Infinity" --output "/path/to/entry.md"
```

### Using Custom Configuration

Use a custom configuration file:

```bash
python -m opus_entries.cli generate --topic "Topic" --config "custom-config.json"
```

## Entry Structure

Each generated entry includes 6 sections:

1. **Introduction** (1,500-2,000 words)
   - Presents the topic and its significance
   - Outlines key themes
   - Sets the stage for exploration

2. **The Patristic Mind** (2,000-2,500 words)
   - Explores how the Church Fathers understood the topic
   - Draws on Patristic sources and traditions
   - Shows continuity of Orthodox thought

3. **Symphony of Clashes** (2,000-2,500 words)
   - Presents dialectical tensions and contradictions
   - Explores different perspectives
   - Examines creative tensions

4. **Orthodox Affirmation** (2,000-2,500 words)
   - Articulates the Orthodox Christian position
   - Grounds affirmations in Scripture and Tradition
   - Demonstrates theological coherence

5. **Synthesis** (1,500-2,000 words)
   - Integrates previous threads
   - Shows unified Orthodox understanding
   - Points to practical implications

6. **Conclusion** (1,500-2,000 words)
   - Summarizes key insights
   - Reinforces Orthodox perspective
   - Points to future exploration

## Quality Tiers

Entries are automatically assigned quality tiers based on validation scores:

- **CELESTIAL** (95-100): Exceptional theological depth and coherence
- **ADAMANTINE** (90-94): Outstanding quality and insight
- **PLATINUM** (85-89): Excellent comprehensive coverage
- **GOLD** (80-84): Very good quality
- **SILVER** (75-79): Good quality
- **BRONZE** (70-74): Acceptable quality
- **UNRANKED** (<70): Below standard

## Validation Criteria

Entries are scored on five criteria:

1. **Word Count** (20% weight): Adherence to 11,000-14,000 word target
2. **Theological Depth** (30% weight): Patristic references and Orthodox concepts
3. **Coherence** (25% weight): Completeness and flow of sections
4. **Section Balance** (15% weight): Appropriate length for each section
5. **Orthodox Perspective** (10% weight): Fidelity to Orthodox tradition

## Understanding Validation Results

After generation, you'll see validation results:

```
Validation Results:
  Overall Score: 92.50/100
  Quality Tier: ADAMANTINE

Component Scores:
  Word Count: 95.00/100
  Theological Depth: 88.00/100
  Coherence: 92.00/100
  Section Balance: 91.00/100
  Orthodox Perspective: 94.00/100

Feedback:
  - Excellent work! This entry meets all quality standards.
```

## Tips for Better Entries

1. **Choose Focused Topics**: More specific topics often produce better results
2. **Use Descriptive Titles**: Help the LLM understand the scope
3. **Check LLM Connection**: Ensure your local LLM service is running
4. **Review Output**: While automated, entries benefit from human review
5. **Iterate**: If quality is low, try regenerating or refining the topic

## Output Format

Entries are saved in Markdown format with:
- Topic as main heading
- Quality tier and validation score
- Total word count
- Each section with word count
- Easy to read and edit format

## Advanced Usage

### Programmatic Use

You can also use the system programmatically:

```python
from opus_entries import EntryGenerator, EntryValidator

# Generate an entry
generator = EntryGenerator()
entry = generator.generate("Your Topic")

# Validate it
validator = EntryValidator()
result = validator.validate(entry)

# Save as markdown
with open("output.md", "w") as f:
    f.write(entry.to_markdown())
```

### Custom Configuration

Create a custom `config.json` to adjust:
- Word count targets
- Section definitions
- Quality tier thresholds
- Validation weights
- LLM settings

See `config.json` for the default configuration structure.
