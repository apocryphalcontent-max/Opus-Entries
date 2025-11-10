# Opus Maximus - Theological Encyclopedia Generator

**Version:** 2.0 (Development Build)
**Status:** ⚠️ ACTIVE DEVELOPMENT

A comprehensive AI-powered system for generating Orthodox theological encyclopedia entries with sophisticated validation, multi-tier caching, and resumable generation.

---

## ⚠️ PROJECT STATUS

This is an **active development build (v2.0)**. Core functionality has been implemented and is being tested.

### What Works ✅

- **LLM Integration**: Complete integration with llama-cpp-python (local models) and OpenAI-compatible APIs
- **Validation Framework**: Multi-dimensional validation (theological, stylistic, structural, citation)
- **Checkpoint System**: Full checkpoint/resume capability for fault-tolerant generation
- **Multi-Tier Caching**: L1/L2/L3 caching optimized for 32GB RAM systems
- **Batch Processing**: Unattended multi-entry generation with progress tracking
- **Error Recovery**: Automatic retry with exponential backoff
- **Configuration System**: Comprehensive YAML-based configuration

### In Progress 🚧

- **Template-Guided Generation**: Pattern extraction from golden entries
- **Quality Testing**: Comprehensive test suite
- **Performance Optimization**: Benchmarking and tuning
- **Documentation**: Complete usage guides

### Not Yet Implemented ❌

- **Web Dashboard**: Streamlit-based monitoring UI
- **Human Review Workflow**: Integration with review systems
- **Ecclesial Oversight**: Theological review process
- **Production Deployment**: Hardened for large-scale operation

---

## Prerequisites

### Hardware Requirements

**Recommended:**
- **GPU**: 16GB+ VRAM (NVIDIA RTX 4070 Ti or better)
- **RAM**: 32GB+ system RAM
- **Storage**: 50GB+ free space (for models and cache)
- **CPU**: 8+ cores (16+ recommended)

**Minimum:**
- **GPU**: 8GB VRAM (or use API mode)
- **RAM**: 16GB
- **Storage**: 20GB

### Software Requirements

- **Python**: 3.10 or higher
- **CUDA**: 11.8 or 12.1 (for GPU acceleration)
- **Git**: For cloning and version control

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Opus-Entries.git
cd Opus-Entries
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**For GPU acceleration (CUDA 11.8):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118
```

**For GPU acceleration (CUDA 12.1):**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**For CPU/Metal (macOS):**
```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### 4. Download Model

Download a GGUF model file and place in `models/` directory.

**Recommended models:**
- [Nous-Hermes-2-SOLAR-10.7B-GGUF](https://huggingface.co/TheBloke/Nous-Hermes-2-SOLAR-10.7B-GGUF) (Q5_K_M, 6.7GB)
- [Mixtral-8x7B-Instruct-GGUF](https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF) (Q4_K_M, 26GB)

```bash
mkdir -p models
cd models
# Download your chosen model
wget https://huggingface.co/TheBloke/Nous-Hermes-2-SOLAR-10.7B-GGUF/resolve/main/nous-hermes-2-solar-10.7b.Q5_K_M.gguf
cd ..
```

### 5. Configure

Edit `Opus/config/config.yaml` to point to your model:

```yaml
model:
  path: "models/nous-hermes-2-solar-10.7b.Q5_K_M.gguf"
  n_ctx: 16384
  n_gpu_layers: -1  # -1 = all layers on GPU
  # ... other settings
```

---

## Quick Start

### Generate Single Entry

```bash
python opus_cli.py generate --subject "Theosis" --tier "Tier 1" --category "Soteriology"
```

**Expected:** 30-90 minutes for first generation (cold cache)

### Process Batch

```bash
python opus_cli.py batch --pool Opus/data/subjects/pool_12000.json --max 10
```

### Validate Entry

```bash
python opus_cli.py validate --file GENERATED_ENTRIES_MASTER/Tier_1/Theosis.md
```

### Show Cache Statistics

```bash
python opus_cli.py cache-stats
```

---

## Usage

### Python API

```python
from Opus.src import OpusMaximusEngine, OpusConfig

# Load configuration
config = OpusConfig.from_yaml('Opus/config/config.yaml')

# Create engine
engine = OpusMaximusEngine(config)

# Generate entry
result = engine.generate_entry(
    subject="Theosis",
    tier="Tier 1",
    category="Soteriology",
    resume=True  # Enable checkpoint/resume
)

print(f"Generated {result.word_count} words")
print(f"Quality score: {result.validation['score']:.3f}")
```

### Batch Processing

```python
from Opus.src import BatchProcessor, create_engine_from_config
from pathlib import Path

# Create engine
engine = create_engine_from_config(Path('Opus/config/config.yaml'))

# Create batch processor
processor = BatchProcessor(engine)

# Process pool
stats = processor.process_pool(
    pool_file=Path('Opus/data/subjects/pool_12000.json'),
    start_index=0,
    max_entries=100,
    skip_existing=True
)

print(f"Completed: {stats.completed}")
print(f"Average quality: {stats.average_quality_score:.3f}")
```

---

## Architecture

### Core Components

1. **LLM Interface** (`llm_interface.py`)
   - Unified interface for local (llama.cpp) and API-based backends
   - Automatic retry with exponential backoff
   - Token counting and cost estimation

2. **Validators** (`validators.py`)
   - **Theological**: Heresy detection, council compliance
   - **Style**: ALPHA, BETA, GAMMA, DELTA rulesets
   - **Patristic**: Citation verification
   - **Structural**: Entry structure requirements

3. **Checkpoint Manager** (`checkpoint_manager.py`)
   - Save/resume generation state
   - Corruption detection
   - Automatic cleanup

4. **Multi-Tier Cache** (`caching.py`)
   - L1: Hot RAM cache (5,000 entries)
   - L2: Warm RAM cache (50,000 entries)
   - L3: Compressed disk cache (unlimited)

5. **Opus Engine** (`opus_engine.py`)
   - Main generation orchestrator
   - Integrates all components
   - Error recovery and retry logic

6. **Batch Processor** (`batch_processor.py`)
   - Unattended multi-entry generation
   - Progress tracking with tqdm
   - Error logging and statistics

---

## Performance

### Expected Generation Times

| Metric | Cold Cache | Hot Cache |
|--------|-----------|-----------|
| Single Entry (10k words) | 45-90 min | 30-45 min |
| Blueprint Only | 3-5 min | 1-2 min |
| Single Section (2k words) | 8-12 min | 5-8 min |

*Based on 16GB VRAM GPU with Q5_K_M quantization*

### Realistic Timelines

- **10 entries**: 1-2 days (24/7 operation)
- **100 entries**: 2-4 weeks
- **1,000 entries**: 6-12 months
- **12,000 entries**: 3-5 years

### Cost Estimates

**Self-Hosted:**
- Hardware: $3,000-$5,000 (GPU + system)
- Electricity: ~$500-$1,000/year (24/7 operation)

**API-Based (OpenAI/Anthropic):**
- 12,000 entries: ~$10,000-$30,000
- 100 entries: ~$100-$300

---

## Limitations

### Technical Limitations

1. **No Semantic Validation**: Cannot detect logical contradictions
2. **Regex-Based Heresy Detection**: May miss subtle theological errors
3. **Citation Accuracy Not Verified**: Counts citations but doesn't verify quotes
4. **Single-Threaded Generation**: Cannot parallelize entry generation

### Theological Limitations

1. **No Church Oversight**: Not reviewed by Orthodox theologians
2. **AI-Generated Content**: Lacks spiritual discernment
3. **Possible Errors**: May contain subtle theological mistakes
4. **No Ecclesial Authority**: Cannot teach authoritatively

⚠️ **All generated content should be reviewed by qualified Orthodox theologians before publication.**

---

## Troubleshooting

### "Model file not found"

Check `model.path` in `config.yaml` points to actual GGUF file.

### "Out of memory" (CUDA)

- Reduce `n_ctx` to 8192 or 4096
- Use smaller quantization (Q4 instead of Q5)
- Reduce `n_gpu_layers`

### Generation Very Slow

- Check GPU utilization: `nvidia-smi`
- Ensure `n_gpu_layers: -1` (all layers on GPU)
- Use faster quantization (Q5_K_M or Q6_K)

---

## Development

### Running Tests

```bash
pytest Opus/tests/ -v
```

### Code Quality

```bash
# Format code
black Opus/src/

# Type checking
mypy Opus/src/

# Linting
flake8 Opus/src/
```

---

## Disclaimer

This system generates AI-powered theological content. While sophisticated validation is employed, **all output requires review by qualified Orthodox theologians** before use in teaching, publication, or spiritual guidance.

The system is provided "as-is" without warranty. The authors are not responsible for theological errors, misuse, or reliance on generated content without proper review.

---

**Status:** Active Development
**Last Updated:** November 10, 2025
**Version:** 2.0.0
