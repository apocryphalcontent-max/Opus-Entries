# OPUS MAXIMUS ULTIMATE v3.0 - SETUP GUIDE

## Quick Installation

### Windows Users (Easiest)

1. **Double-click** `setup.bat`
2. Wait for setup to complete
3. Follow on-screen instructions

### All Users (Command Line)

```bash
cd "C:\Users\Edwin Boston\Desktop\Opus"
python setup.py
```

---

## What Setup Does

The setup script automatically:

✅ **Checks Python version** (3.10+ required)  
✅ **Installs dependencies** (networkx, pyyaml)  
✅ **Creates directories** (Golden_Entries, GENERATED_ENTRIES_MASTER, cache, logs)  
✅ **Validates all files** (7 new files)  
✅ **Runs system tests** (comprehensive validation)  
✅ **Provides next steps**

---

## System Requirements

### Software

- **Python**: 3.10 or higher
- **pip**: Latest version
- **Dependencies** (auto-installed):
  - networkx (for dependency graphs)
  - pyyaml (for configuration)

### Hardware

- **RAM**: 32GB recommended (for caching)
- **Storage**: 500GB+ (for 12,000 entries)
- **CPU**: Modern multi-core processor
- **GPU**: 16GB VRAM (for LLM, if using local model)

---

## Manual Installation

If automatic setup fails, install dependencies manually:

```bash
# Install dependencies
pip install networkx
pip install pyyaml

# Create directories
mkdir Golden_Entries
mkdir GENERATED_ENTRIES_MASTER
mkdir cache
mkdir logs

# Run tests
python test_ultimate_system.py
```

---

## Troubleshooting

### "Python not found"

Make sure Python is in your PATH:
```bash
python --version
```

If not found, reinstall Python with "Add to PATH" checked.

### "Permission denied"

Run terminal as Administrator (Windows) or use `sudo` (Linux/Mac).

### "Module not found: networkx"

Install manually:
```bash
pip install networkx pyyaml
```

### "Golden_Entries directory empty"

This is OK for initial setup. You can:
1. Use your existing golden entries
2. Add sample entries later
3. Skip pattern extraction temporarily

---

## Next Steps After Setup

### 1. Extract Golden Patterns (5 min)

```bash
python golden_pattern_extractor.py
```

**Prerequisites**: 
- Golden_Entries/ directory exists
- Contains .md files with golden entries

**Output**: 
- `golden_patterns.json`

### 2. Create Subjects Pool (varies)

```bash
# Sample (60 subjects)
python subjects_pool_generator.py

# Or create manually: subjects_pool.json
```

**Output**:
- `subjects_pool_sample.json` (sample)
- OR `subjects_pool.json` (your 12,000 subjects)

### 3. Generate Entry Queue (2 min)

```bash
python entry_queue_generator.py
```

**Prerequisites**:
- `subjects_pool.json` exists
- `golden_patterns.json` exists

**Output**:
- `entry_queue.json` (strategically ordered)

---

## File Structure After Setup

```
C:\Users\Edwin Boston\Desktop\Opus\
│
├── setup.py                               ✅ Setup script
├── setup.bat                              ✅ Windows launcher
├── test_ultimate_system.py                ✅ System tests
│
├── golden_pattern_extractor.py            ✅ Extract quality DNA
├── entry_queue_generator.py               ✅ Order entries
├── subjects_pool_generator.py             ✅ Sample subjects
│
├── ULTIMATE_ENGINE_ARCHITECTURE.md        ✅ Architecture docs
├── ULTIMATE_INTEGRATION_SUMMARY.md        ✅ Integration guide
├── QUICK_START_ULTIMATE.md                ✅ Quick start
├── VISUAL_ARCHITECTURE_SUMMARY.txt        ✅ Visual reference
├── README_ULTIMATE.md                     ✅ Main README
├── SETUP_README.md                        ✅ This file
│
├── Golden_Entries/                        📁 Your golden entries
├── GENERATED_ENTRIES_MASTER/              📁 Generated output
├── cache/                                 📁 System cache
└── logs/                                  📁 Processing logs
```

---

## Validation Checklist

After running setup, verify:

- [ ] Python 3.10+ detected
- [ ] networkx installed
- [ ] pyyaml installed
- [ ] All 7 files present
- [ ] All 4 directories created
- [ ] System tests passed
- [ ] No errors in setup output

---

## Getting Help

### Documentation

1. **QUICK_START_ULTIMATE.md** - Start here
2. **README_ULTIMATE.md** - System overview
3. **ULTIMATE_INTEGRATION_SUMMARY.md** - How it works
4. **ULTIMATE_ENGINE_ARCHITECTURE.md** - Technical details

### Common Issues

**Q: Setup says "Golden_Entries not found"**  
A: Create the directory and add your golden entries, or skip this test for now.

**Q: "NetworkX not installed" warning**  
A: Run: `pip install networkx`

**Q: Can I skip some steps?**  
A: Yes, but you need at minimum:
   - Python 3.10+
   - All 7 files present
   - Dependencies installed

---

## Success Criteria

Setup is complete when you see:

```
✅ ALL TESTS PASSED!

System is ready for use. Next steps:
  1. Run: python golden_pattern_extractor.py
  2. Run: python subjects_pool_generator.py
  3. Run: python entry_queue_generator.py
```

---

## Support

If setup fails:

1. Check Python version: `python --version`
2. Check pip works: `pip --version`
3. Try manual installation (see above)
4. Read error messages carefully
5. Check TROUBLESHOOTING section above

---

**Ready?** Run `python setup.py` or double-click `setup.bat`

---

**Glory to the Father and to the Son and to the Holy Spirit,**  
**now and ever and unto ages of ages. Amen. ✝**
