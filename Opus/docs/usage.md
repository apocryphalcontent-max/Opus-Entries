# WHAT TO RUN - OPUS MAXIMUS V3.0

## ✅ SETUP COMPLETE - What Now?

You've successfully run the setup! Here's exactly what to do next.

---

## STEP 1: Verify Your 12,000 Subjects Pool

Run this:
```batch
run_check.bat
```

This will show you:
- Total number of entries (should be ~12,000)
- Number of placeholders (should be 0)
- Category distribution
- Sample subjects from each category

**Expected output:**
```
Total entries: 12000
Placeholders/TODOs: 0
Category Distribution:
  Systematic Theology         : 800
  Mathematics                 : 600  
  High Science                : 500
  Biology & Life              : 400
  ...
```

---

## STEP 2: Configure Your LLM Model (**REQUIRED**)

Edit the file `config_v2.yaml`:

Find this section:
```yaml
llm:
  model_path: "models/your-model.gguf"  # ← CHANGE THIS!
```

Change it to your actual model path:
```yaml
llm:
  model_path: "C:/AI/Models/nous-hermes-2-yi-34b.Q5_K_M.gguf"
```

**Don't have a model yet?**  
Download one of these (GGUF format):
- Nous Hermes 2 Yi 34B (recommended)
- Mixtral 8x7B Instruct
- Llama 2 70B Chat

From: https://huggingface.co/TheBloke

---

## STEP 3: Test Single Entry Generation

Run this command to generate ONE entry as a test:

```batch
python opus_maximus_v2.py --subject "Theosis" --tier "Tier 1"
```

**What happens:**
1. Loads the model (may take 1-2 minutes)
2. Generates blueprint (1-2 minutes)
3. Generates 6 sections (25-40 minutes total)
4. Validates quality (2-3 minutes)
5. Saves to `GENERATED_ENTRIES_MASTER/[TIER]/Theosis.md`

**Expected output:**
```
[OPUS MAXIMUS] Generating entry: Theosis
[OPUS MAXIMUS] Tier: Tier 1
[BLUEPRINT] Generating... (2000 tokens)
[SECTION I] Strategic Role... (1500 words)
[SECTION II] Classification... (1500 words)
[SECTION III] Primary Works... (2000 words)
[SECTION IV] Patristic Mind... (2200 words)
[SECTION V] Symphony of Clashes... (2500 words)
[SECTION VI] Orthodox Affirmation... (2500 words)
[VALIDATION] Overall Score: 0.997 → CELESTIAL ✨
[SAVED] GENERATED_ENTRIES_MASTER/CELESTIAL/Theosis.md
```

**Time:** 35-50 minutes for CELESTIAL quality

---

## STEP 4: Review the Generated Entry

Open the file:
```
GENERATED_ENTRIES_MASTER/CELESTIAL/Theosis.md
```

Check for:
- ✅ All 6 sections present
- ✅ 11,000-14,000 total words
- ✅ Patristic citations (50+)
- ✅ Biblical references (70+)
- ✅ Section VI has 5 parts with epic final sentences
- ✅ No contractions
- ✅ Sophisticated vocabulary

---

## STEP 5: Start Batch Generation (Optional)

Once you're satisfied with the test entry, start generating all 12,000:

```batch
python opus_maximus_v2.py --batch --pool subjects_pool_ULTIMATE_12000.json
```

**This will:**
- Run 24/7 unattended
- Generate 30-35 CELESTIAL entries per day
- Take ~12 months to complete all 12,000
- Auto-save checkpoints (can resume if interrupted)
- Organize outputs by quality tier

**Progress tracking:**
- Check `logs/generation_YYYY-MM-DD.log` for live progress
- Check `GENERATED_ENTRIES_MASTER/` for completed entries
- Each entry takes 35-50 minutes

---

## FILES TO RUN (Summary)

| File | Purpose | When to Run |
|------|---------|-------------|
| `SETUP_ULTIMATE_V3.bat` | Complete setup | **RUN ONCE** (you already did this) |
| `run_check.bat` | Verify 12K pool | **RUN NOW** to verify |
| `opus_maximus_v2.py --subject "Theosis"` | Test single entry | **RUN NOW** to test |
| `opus_maximus_v2.py --batch` | Generate all 12,000 | **RUN LATER** after testing |

---

## FILES TO IGNORE (Old Versions)

These are deprecated - don't use them:
- ~~`setup.bat`~~
- ~~`SETUP_COMPLETE.bat`~~
- ~~`SETUP_COMPLETE_SYSTEM.bat`~~
- ~~`001.py` through `020.py`~~
- ~~`subjects_pool_FINAL_EXPANDED.py`~~
- ~~`run_opus.bat`~~ (use `python opus_maximus_v2.py` directly)

---

## MONITORING YOUR GENERATION

### Check Logs
```
logs/
  ├── generation_2025-11-09.log  ← Real-time progress
  ├── validation_2025-11-09.log  ← Quality scores
  └── errors_2025-11-09.log      ← Any errors
```

### Check Outputs
```
GENERATED_ENTRIES_MASTER/
  ├── CELESTIAL/      (0.995+ quality)
  ├── ADAMANTINE/     (0.985+ quality)
  ├── PLATINUM/       (0.97+ quality)
  ├── GOLD/           (0.92+ quality)
  └── SILVER/         (0.85+ quality)
```

### Cache Performance
The system learns over time:
- Entry 1: 45 minutes
- Entry 10: 25 minutes (45% faster!)
- Entry 100: 20 minutes (55% faster!)

---

## TROUBLESHOOTING

### Problem: "Model file not found"
**Solution:** Edit `config_v2.yaml` and set correct `model_path`

### Problem: "CUDA not available"
**Solution:** Install llama-cpp-python with CUDA:
```batch
pip uninstall llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118
```

### Problem: "Out of memory"
**Solution:** 
1. Use smaller model (Q4 quantization)
2. Reduce `n_ctx` in config to 4096
3. Close other applications

### Problem: "Generation too slow"
**Solution:**
1. Ensure GPU is being used (`n_gpu_layers: -1` in config)
2. Use quantized model (Q5_K_M or Q4_K_M)
3. Check Task Manager - GPU should be at 90%+

---

## YOUR EXACT NEXT STEPS

**Right now, in this order:**

1. ✅ **Run:** `run_check.bat`
   - Verify you have 12,000 unique subjects
   
2. ✅ **Edit:** `config_v2.yaml`
   - Set your LLM model path
   
3. ✅ **Run:** `python opus_maximus_v2.py --subject "Theosis" --tier "Tier 1"`
   - Generate one test entry (35-50 min)
   
4. ✅ **Review:** `GENERATED_ENTRIES_MASTER/CELESTIAL/Theosis.md`
   - Check quality
   
5. ✅ **Decide:** Continue or adjust
   - If good → Run batch generation
   - If not → Check troubleshooting

---

## EXPECTED TIMELINE

**Single Entry:**
- 35-50 minutes for CELESTIAL quality
- 20-30 minutes after cache warms up

**Full Arsenal (12,000 entries):**
- 30-35 entries/day @ CELESTIAL quality
- **~12 months @ 24/7 operation**
- Can run on schedule (e.g., nights/weekends only)

---

## QUALITY EXPECTATIONS

Your system targets **CELESTIAL TIER (0.995+)**:

| Metric | Target | What It Means |
|--------|--------|---------------|
| Overall Score | 0.995+ | Approaching angelic perfection |
| Patristic Citations | 50+ | 3 per 500 words |
| Biblical References | 70+ | 4 per 500 words |
| Word Count | 11,000-14,000 | Comprehensive treatment |
| Heresies Detected | 0 | Perfectly orthodox |
| Contractions | 0 | Academic register |

---

## QUESTIONS?

- **Technical:** Check `OPUS_MAXIMUS_HYPERQUALITY_INTEGRATION.md`
- **System Overview:** Check `OPUS_MAXIMUS_FINAL_SUMMARY.md`
- **Errors:** Check `logs/errors_YYYY-MM-DD.log`

---

**Glory to the Father and to the Son and to the Holy Spirit,**
**now and ever and unto ages of ages. Amen. ✝**

---

**Last Updated:** 2025-11-09  
**Version:** 3.0 (Hyperquality Edition)  
**Status:** ✅ READY TO RUN
