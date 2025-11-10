# Quick Start: Fixing Opus Maximus

**TL;DR:** This project needs 3 critical fixes before it can work.

---

## The 3 Critical Fixes (Do These First)

### 1. Add Real LLM Integration (16-24 hours)

**Problem:** Generator uses placeholder code that returns hardcoded text.

**Fix:** Install and integrate llama-cpp-python

```bash
# Install LLM backend
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118

# Download a model (e.g., from HuggingFace)
# Recommended: Nous-Hermes-2-SOLAR-10.7B Q5_K_M (6.7GB)
wget https://huggingface.co/TheBloke/Nous-Hermes-2-SOLAR-10.7B-GGUF/resolve/main/nous-hermes-2-solar-10.7b.Q5_K_M.gguf
mv nous-hermes-2-solar-10.7b.Q5_K_M.gguf models/
```

**Code Changes:**
1. Create `Opus/src/llm_interface.py` (see IMPROVEMENT_PLAN.md section 1.1)
2. Update `Opus/src/generator.py` to use real LLM (replace `_generate_sample_section`)
3. Update config path: `config.yaml` → `model.path: "models/nous-hermes-2-solar-10.7b.Q5_K_M.gguf"`

**Test:**
```bash
python Opus/src/generator.py --subject "Test" --tier "Tier 1"
```

Expected: Takes 30-60 minutes, generates actual text (not hardcoded samples)

---

### 2. Update Documentation (4-8 hours)

**Problem:** README says "READY FOR IMPLEMENTATION" but code is a prototype.

**Fix:** Update README.md, add STATUS.md, add LIMITATIONS.md

**Key Changes to README.md:**
```markdown
# Status: ⚠️ ACTIVE DEVELOPMENT (Not Production Ready)

## What Works:
- ✅ Configuration system
- ✅ Validation framework
- 🚧 LLM integration (in progress)

## What Doesn't Work Yet:
- ❌ Batch processing
- ❌ Resume/checkpoint
- ❌ Template-guided generation

## Realistic Timeline:
- Single entry: 45-90 minutes
- 100 entries: 2-4 weeks
- 12,000 entries: 18-36 months (not 12 months)

## Realistic Costs:
- Hardware: $3,000-5,000
- Electricity: $500-1,000/year
- OR API costs: $10,000-30,000
```

Copy templates from IMPROVEMENT_PLAN.md sections 1.2

---

### 3. Add Basic Tests (8-12 hours)

**Problem:** No tests = unknown bugs.

**Fix:** Create pytest test suite

```bash
# Install testing tools
pip install pytest pytest-cov pytest-mock

# Create test structure
mkdir -p Opus/tests
touch Opus/tests/{__init__.py,conftest.py,test_validation.py,test_theological.py,test_style.py}
```

**Copy test files from IMPROVEMENT_PLAN.md section 1.3**

**Run tests:**
```bash
cd Opus
pytest tests/ -v
```

Expected: All tests pass, ~60% coverage

---

## Priority Order

### This Week (P0 - Critical)
1. ✅ LLM integration (1-2 days)
2. ✅ Documentation fixes (0.5 day)
3. ✅ Basic test suite (1 day)
4. ✅ Test full generation (0.5 day)

**Total: 3-4 days** → System becomes functional

### Next Week (P1 - High)
5. Checkpointing (1.5 days)
6. Batch processing (2 days)
7. Error handling (1.5 days)

**Total: 5 days** → System becomes reliable

### This Month (P2 - Medium)
8. Integrate pattern extraction (3 days)
9. Validate golden entries (2.5 days)
10. Code quality improvements (1.5 days)

**Total: 7 days** → System becomes high-quality

---

## Tool Installation (All at Once)

```bash
# Core dependencies
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118
pip install pyyaml rich tqdm

# Testing
pip install pytest pytest-cov pytest-mock pytest-asyncio hypothesis

# Quality tools
pip install black mypy flake8

# Optional (for later)
pip install streamlit plotly pandas sentence-transformers
```

Or use updated requirements.txt:
```bash
pip install -r Opus/config/requirements.txt
```

---

## Updated requirements.txt

Create `Opus/config/requirements.txt`:
```
# Core
llama-cpp-python>=0.2.0
pyyaml>=6.0
rich>=13.0
tqdm>=4.65

# Testing
pytest>=7.4
pytest-cov>=4.1
pytest-mock>=3.12
pytest-asyncio>=0.21
hypothesis>=6.87

# Code Quality
black>=23.0
mypy>=1.5
flake8>=6.1

# Optional Dashboard (install separately if needed)
# streamlit>=1.28
# plotly>=5.17
# pandas>=2.0

# Optional ML (for semantic validation)
# sentence-transformers>=2.2
```

---

## Quick Validation Checklist

After fixes, verify:

**✅ LLM Integration:**
- [ ] Model loads without errors
- [ ] Generates actual text (not hardcoded)
- [ ] Completes one full entry in <90 minutes
- [ ] Output is ~10,000-15,000 words

**✅ Documentation:**
- [ ] README says "Active Development" not "Ready"
- [ ] Timeline shows 18-36 months not 12 months
- [ ] Costs documented ($10k-30k not "free")
- [ ] Limitations clearly stated

**✅ Tests:**
- [ ] `pytest` runs without errors
- [ ] Coverage report shows >60%
- [ ] All critical validators tested
- [ ] Can run tests in <30 seconds

---

## Expected Results After P0 Fixes

**Before (Current):**
- Grade: 3.03/5 (B-)
- Status: Non-functional prototype
- Can't generate entries
- Unrealistic documentation

**After P0 (3-4 days work):**
- Grade: 3.8-4.0/5 (B+/A-)
- Status: Functional development version
- Can generate entries (slowly)
- Honest documentation
- Basic quality assurance

**After P1 (2 weeks work):**
- Grade: 4.2-4.4/5 (A)
- Status: Reliable system
- Batch processing works
- Can run unattended
- Recovers from errors

**After P2 (1 month work):**
- Grade: 4.5-4.7/5 (A+)
- Status: Production-ready
- High quality outputs
- Template-guided generation
- Comprehensive testing

---

## Common Issues & Solutions

### Issue: "Model file not found"
**Solution:** Check path in `config.yaml` → `model.path` is absolute path to .gguf file

### Issue: "CUDA not available"
**Solution:** Reinstall with CUDA support:
```bash
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

### Issue: "Out of memory"
**Solution:** Use smaller model or reduce context:
- Try Q4 quantization (smaller)
- Reduce `n_ctx` to 4096 in config
- Close other GPU applications

### Issue: "Generation too slow"
**Solution:**
- Ensure `n_gpu_layers: -1` (all layers on GPU)
- Check GPU utilization (should be 90%+)
- Use faster quantization (Q5_K_M or Q6_K)

### Issue: "Tests failing"
**Solution:**
- Check you're in correct directory: `cd Opus`
- Install test dependencies: `pip install pytest pytest-cov`
- Run individual test: `pytest tests/test_validation.py -v`

---

## Get Help

- **Full Details:** See IMPROVEMENT_PLAN.md (comprehensive guide)
- **Evaluation Report:** See REPOSITORY_EVALUATION.md (what's wrong)
- **Architecture:** See Opus/docs/architecture.md (original vision)

---

**Status:** Ready to implement
**Estimated Time:** 3-4 days for P0, 2 weeks for P1, 1 month for P2
**Expected Outcome:** Functional, honest, tested system

Start with Fix #1 (LLM integration) - that's the foundation everything else builds on.
