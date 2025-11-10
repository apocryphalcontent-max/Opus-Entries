# OPUS MAXIMUS - AFTER SETUP GUIDE

## ✅ Setup Complete - What's Next?

You've successfully run `SETUP_COMPLETE_SYSTEM.bat`. Here's what to do now.

---

## 📁 Files Created During Setup

```
✓ subjects_pool_ULTIMATE_12000.json  - 12,000+ subjects to generate
✓ entry_queue.json                   - Optimized generation order
✓ golden_patterns.json               - Quality templates
✓ config_v2.yaml                     - System configuration
✓ Directory structure                - All folders created
```

---

## 🚀 Starting Generation

### Method 1: Interactive Mode (Recommended for First Use)

```bash
python opus_maximus_v2.py --interactive
```

This will:
- Ask which entry to generate
- Show you the quality analysis in real-time
- Let you review before saving
- Good for learning the system

### Method 2: Queue Mode (For Batch Processing)

```bash
python opus_maximus_v2.py --queue
```

This will:
- Read from `entry_queue.json`
- Generate entries in optimal order
- Run 24/7 unattended
- Save checkpoints automatically
- Resume if interrupted

### Method 3: Single Entry Mode

```bash
python opus_maximus_v2.py --subject "Theosis"
```

Generate one specific entry immediately.

---

## 📊 Monitoring Progress

### View Generation Stats

```bash
python opus_maximus_v2.py --stats
```

Shows:
- Total entries generated
- Quality distribution (Celestial/Adamantine/Platinum)
- Cache hit rates
- Generation speed
- Estimated time remaining

### View Logs

```bash
# Real-time log monitoring
tail -f logs/opus_maximus.log

# Or on Windows:
Get-Content logs\opus_maximus.log -Wait -Tail 50
```

---

## ⚙️ Configuration (Optional)

Before starting, you may want to adjust `config_v2.yaml`:

### LLM Settings

```yaml
model:
  path: "models/nous-hermes-2-mixtral.gguf"  # Update this path
  n_ctx: 16384                               # Context window
  n_gpu_layers: -1                           # -1 = use all GPU
```

### Quality Thresholds

```yaml
validation:
  quality_threshold: 0.85      # Minimum overall quality
  min_patristic_citations: 40  # Citations required
  min_biblical_references: 60  # Bible refs required
```

### Performance

```yaml
performance:
  vram_reservation_mb: 512         # Reserve VRAM
  max_parallel_validations: 8     # Parallel validation
```

---

## 📖 Generation Workflow

### 1. Queue-Based Generation (24/7 Operation)

This is the PRIMARY workflow for generating all 12,000 entries:

```bash
# Start queue processing
python opus_maximus_v2.py --queue --continuous
```

**What happens:**
1. Reads next entry from `entry_queue.json`
2. Generates blueprint (2-3 minutes)
3. Generates 6 sections (30-40 minutes total)
4. Validates quality (ALPHA/BETA/GAMMA/DELTA)
5. If validation fails, attempts correction
6. Saves to `GENERATED_ENTRIES_MASTER/`
7. Updates checkpoint
8. Moves to next entry
9. Repeats until all 12,000 complete

**Estimated time:** ~12 months for 12,000 entries at Celestial Tier quality

### 2. Single Entry Generation (Testing)

Good for testing or generating specific entries:

```bash
# Generate one entry
python opus_maximus_v2.py --subject "Divine Energies"

# Generate with specific tier
python opus_maximus_v2.py --subject "Saint Maximus" --tier "S+"
```

### 3. Batch Generation (Custom List)

Generate a custom subset:

```bash
# Create custom list
echo '["Theosis", "Hesychasm", "Palamism"]' > my_batch.json

# Generate batch
python opus_maximus_v2.py --batch my_batch.json
```

---

## 🎯 Understanding Quality Tiers

Every generated entry receives a quality score and tier:

| Tier | Score | Quality Level |
|------|-------|---------------|
| **Celestial ✨** | 0.995+ | Approaching angelic perfection |
| **Adamantine 💎** | 0.985+ | Beyond human capability |
| **Platinum ⭐** | 0.97+ | 99th percentile excellence |
| **Gold 🥇** | 0.92+ | Exceptional quality |
| **Silver 🥈** | 0.85+ | Strong quality |
| **Bronze 🥉** | 0.70+ | Acceptable quality |

**Goal:** Achieve Celestial or Adamantine tier for all entries.

---

## 🔍 Validation System

Four rulesets evaluate every entry:

### ALPHA: Vocabulary Sophistication
- Average word length ≥5.5 characters
- Simple words ≤25%
- Sophisticated theological terms present

### BETA: Sentence Structure
- Average sentence length: 28-38 words
- Golden ratio pacing: 38% short, 55% medium, 7% long
- Variation coefficient: 0.3-0.6

### GAMMA: Theological Depth
- Patristic citations: 50+ (3 per 500 words)
- Biblical references: 70+ (4 per 500 words)
- No heresies detected
- Conciliar compliance verified

### DELTA: Scholarly Tone
- ZERO contractions
- ZERO informal language
- Third-person perspective
- Academic register maintained

---

## 📁 Output Structure

Generated entries are saved in organized folders:

```
GENERATED_ENTRIES_MASTER/
├── Theology/
│   ├── Systematic/
│   │   ├── Theosis.md
│   │   ├── Theosis.json (metadata)
│   │   └── ...
│   ├── Patristic/
│   ├── Biblical/
│   └── Liturgical/
├── Mathematics/
│   ├── Perfectoid_Spaces.md
│   └── ...
├── Natural_Sciences/
│   ├── Physics/
│   ├── Biology/
│   └── ...
└── Philosophy/
    └── ...
```

Each entry includes:
- **Markdown file** (.md) - Human-readable
- **JSON metadata** (.json) - Quality metrics, citations, etc.

---

## 🛠️ Troubleshooting

### "Model not found" error

```bash
# Download a model first
# Recommended: Nous Hermes 2 Mixtral (70B)
# Place in models/ folder
# Update config_v2.yaml with correct path
```

### "CUDA out of memory" error

```yaml
# Reduce context window in config_v2.yaml
model:
  n_ctx: 8192  # Instead of 16384
  n_batch: 512 # Instead of 1024
```

### "Validation failed repeatedly" error

```yaml
# Lower quality threshold temporarily
validation:
  quality_threshold: 0.75  # Instead of 0.85
```

### Generation is slow

```yaml
# Enable more parallelization
performance:
  enable_async_sections: true
  max_parallel_validations: 16  # Instead of 8
```

---

## 📊 Monitoring Dashboard

View real-time generation stats:

```bash
python opus_maximus_v2.py --dashboard
```

Shows:
- Current entry being generated
- Overall progress (X / 12,000)
- Quality distribution chart
- Cache hit rates
- Generation speed (entries/day)
- ETA to completion

---

## 🎓 Entry Structure

Each entry contains 6 sections:

### I. Strategic Role (1200-1800 words)
Theological foundation and systematic positioning

### II. Classification (1200-1800 words)
Doctrinal taxonomy and heresy distinctions

### III. Primary Works (1500-2500 words)
Patristic, biblical, liturgical sources

### IV. The Patristic Mind (1800-2500 words)
Engagement with 10+ Church Fathers

### V. Symphony of Clashes (2000-3000 words)
Dialectical engagement with objections

### VI. Orthodox Affirmation (2000-2500 words)
**Five-part epic culmination:**
1. Patristic Symphonia (900-1200w)
2. Liturgical Immersion (700-900w)
3. Ascetical Path (400-600w)
4. Eschatological Consummation (500-700w)
5. Doxological Apotheosis (600-900w)

**Total:** 11,000-14,000 words per entry

---

## 🚦 Quick Start Commands

```bash
# 1. Generate first test entry
python opus_maximus_v2.py --subject "Theosis"

# 2. Review the output
cat GENERATED_ENTRIES_MASTER/Theology/Systematic/Theosis.md

# 3. Check quality scores
python opus_maximus_v2.py --stats

# 4. If satisfied, start queue processing
python opus_maximus_v2.py --queue --continuous

# 5. Monitor progress
python opus_maximus_v2.py --dashboard
```

---

## 📝 Important Notes

### Checkpoints

The system automatically saves checkpoints every 10 entries. If generation is interrupted:

```bash
# Resume from last checkpoint
python opus_maximus_v2.py --queue --resume
```

### Cache Benefits

After generating 10+ entries, cache hit rates will be 70-80%, speeding up generation by 2-3x.

### Quality vs. Speed

- **Celestial Tier:** 45-60 minutes per entry
- **Platinum Tier:** 30-40 minutes per entry
- **Gold Tier:** 20-30 minutes per entry

The system targets Celestial Tier by default.

---

## 🎯 Recommended Workflow

### Week 1: Testing Phase
1. Generate 10 test entries from different categories
2. Review quality scores
3. Adjust thresholds if needed
4. Ensure validation is working correctly

### Week 2-4: Optimization Phase
1. Start queue processing
2. Monitor cache hit rates
3. Fine-tune performance settings
4. Verify output quality

### Month 2-12: Production Phase
1. Run 24/7 unattended
2. Generate ~900 entries/month
3. Periodic quality audits
4. Backup regularly

---

## ✅ Success Criteria

Your system is working correctly if:

- ✓ Entries are 11,000-14,000 words
- ✓ Quality scores are 0.97+ (Platinum or higher)
- ✓ No heresies detected
- ✓ 50+ patristic citations per entry
- ✓ 70+ biblical references per entry
- ✓ Section VI has all five parts
- ✓ Generation speed is 30-60 min/entry
- ✓ Cache hit rate reaches 70-80%

---

## 📞 Getting Help

If you encounter issues:

1. Check logs: `logs/opus_maximus.log`
2. Review configuration: `config_v2.yaml`
3. Run system test: `python test_ultimate_system.py`
4. Check documentation:
   - `ULTIMATE_ENGINE_ARCHITECTURE.md`
   - `OPUS_MAXIMUS_HYPERQUALITY_INTEGRATION.md`

---

## 🙏 Doxology

**Glory to the Father and to the Son and to the Holy Spirit,**
**now and ever and unto ages of ages. Amen. ✝**

---

**Generated:** 2025-11-09
**System Version:** 3.0 (Hyperquality Edition)
**Status:** Ready for production deployment
