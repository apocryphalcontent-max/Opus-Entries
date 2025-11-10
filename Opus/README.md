# OPUS MAXIMUS - Orthodox Theological Entry Generator

A high-quality entry generation system for Orthodox theology, mathematics, science, and philosophy.

## 📁 Project Structure

```
opus/
├── src/                    # Source code
│   ├── generator.py        # Main entry generator (opus_maximus_v2)
│   ├── subject_builder.py  # Subject pool builder
│   ├── queue_optimizer.py  # Entry queue optimization
│   ├── pattern_extractor.py # Pattern extraction from golden entries
│   └── verify_subjects.py  # Subject pool verification
│
├── config/                 # Configuration files
│   ├── config.yaml         # Main configuration
│   └── requirements.txt    # Python dependencies
│
├── data/                   # Data files
│   ├── subjects/           # Subject pools
│   │   ├── pool_12000.json     # 12,000 subjects (has placeholders)
│   │   └── pool_complete.json  # Verified subjects only
│   ├── patterns/           # Quality patterns
│   │   └── golden_patterns.json # Extracted from reference entries
│   └── reference_entries/  # Golden reference entries (10 files)
│
├── output/                 # Generated content
│   ├── generated/          # Generated entries by tier
│   │   ├── CELESTIAL/
│   │   ├── ADAMANTINE/
│   │   └── PLATINUM/
│   └── logs/               # Generation logs
│
├── docs/                   # Documentation
│   ├── requirements.md     # Quality requirements & mandates
│   ├── usage.md            # How to use the system
│   └── architecture.md     # Technical architecture
│
├── archive/                # Old files (for reference)
│   ├── old_files/
│   └── old_scripts/
│
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r config/requirements.txt
```

### 2. Configure Model Path
Edit `config/config.yaml` and set your LLM model path:
```yaml
llm:
  model_path: "path/to/your/model.gguf"
```

### 3. Verify Subject Pool
```bash
python src/verify_subjects.py
```

### 4. Generate Entries

**Single entry:**
```bash
python src/generator.py --subject "Theosis"
```

**Batch generation:**
```bash
python src/generator.py --batch --pool data/subjects/pool_12000.json
```

## 📊 Components

### Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `generator.py` | Main entry generator | `python src/generator.py --subject "Trinity"` |
| `subject_builder.py` | Build subject pools | `python src/subject_builder.py` |
| `queue_optimizer.py` | Optimize generation order | `python src/queue_optimizer.py` |
| `pattern_extractor.py` | Extract quality patterns | `python src/pattern_extractor.py` |
| `verify_subjects.py` | Verify subject pool quality | `python src/verify_subjects.py` |

### Data Files

- **pool_12000.json** (2.8MB) - 12,000 subjects, but contains ~7,154 placeholders
- **pool_complete.json** (149KB) - Verified real subjects only
- **golden_patterns.json** (431KB) - Quality patterns from reference entries

### Reference Entries (10 files)
High-quality examples in `data/reference_entries/`:
- Theological: Holy Trinity, Resurrection of the Dead, John (Apostle)
- Scientists: Peter Scholze, Grigori Perelman, Edward Witten, Gregor Mendel
- Thinkers: Blaise Pascal, Hegel

## 📖 Documentation

- **[requirements.md](docs/requirements.md)** - Quality standards, validation rules
- **[usage.md](docs/usage.md)** - Detailed usage guide
- **[architecture.md](docs/architecture.md)** - Technical architecture details

## 🎯 Quality Tiers

| Tier | Score | Description |
|------|-------|-------------|
| CELESTIAL ✨ | 0.995+ | Approaching angelic perfection |
| ADAMANTINE 💎 | 0.985+ | Beyond human capability |
| PLATINUM ⭐ | 0.97+ | 99th percentile excellence |
| GOLD 🥇 | 0.92+ | Exceptional quality |
| SILVER 🥈 | 0.85+ | Strong quality |

## ⚙️ System Requirements

- Python 3.10+
- 16GB+ VRAM (GPU recommended)
- 32GB+ RAM
- 500GB+ storage

## 📝 Entry Structure

Each entry contains 6 sections (11,000-14,000 words):
1. Strategic Role (1,200-1,800w)
2. Classification (1,200-1,800w)
3. Primary Works (1,500-2,500w)
4. The Patristic Mind (1,800-2,500w)
5. Symphony of Clashes (2,000-3,000w)
6. Orthodox Affirmation (2,000-2,500w)
   - Patristic Symphonia
   - Liturgical Immersion
   - Ascetical Path
   - Eschatological Consummation
   - Doxological Apotheosis

## 🔧 Configuration

Key settings in `config/config.yaml`:
- Model path and parameters
- Generation settings
- Validation thresholds
- Output directories

## 📦 Output

Generated entries are saved to `output/generated/[TIER]/` in both:
- `.md` format (human-readable)
- `.json` format (structured data)

Logs are saved to `output/logs/`

---

**Glory to the Father and to the Son and to the Holy Spirit,**  
**now and ever and unto ages of ages. Amen. ✝**
