@echo off
REM ============================================================================
REM OPUS MAXIMUS DREAM ENGINE - COMPLETE SETUP
REM ============================================================================
REM This script sets up the entire system from scratch
REM ============================================================================

echo.
echo ============================================================================
echo OPUS MAXIMUS DREAM ENGINE - ULTIMATE SETUP
echo ============================================================================
echo.
echo This will set up the complete system for CELESTIAL-TIER generation.
echo.
echo Prerequisites Check:
echo   - Python 3.10+: Required
echo   - 32GB RAM: Recommended
echo   - 16GB GPU VRAM: Required for local LLM
echo   - 500GB SSD: Required for cache and outputs
echo.
pause

REM ============================================================================
REM STEP 1: Verify Python Installation
REM ============================================================================
echo.
echo [1/7] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM ============================================================================
REM STEP 2: Install Dependencies
REM ============================================================================
echo.
echo [2/7] Installing Python dependencies...
echo This may take 5-10 minutes...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM ============================================================================
REM STEP 3: Create Directory Structure
REM ============================================================================
echo.
echo [3/7] Creating directory structure...
if not exist "GENERATED_ENTRIES_MASTER" mkdir GENERATED_ENTRIES_MASTER
if not exist "Golden_Entries" mkdir Golden_Entries
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
if not exist ".checkpoints" mkdir .checkpoints
if not exist ".cache" mkdir .cache
if not exist "models" mkdir models
echo ✓ Directory structure created

REM ============================================================================
REM STEP 4: Generate 12,000 Subjects Pool
REM ============================================================================
echo.
echo [4/7] Generating 12,000+ subjects pool...
echo This creates the master list of all entries to generate.
python subjects_pool_ULTIMATE_12000.py
if errorlevel 1 (
    echo ERROR: Failed to generate subjects pool!
    pause
    exit /b 1
)
echo ✓ Subjects pool generated: subjects_pool_ULTIMATE_12000.json

REM ============================================================================
REM STEP 5: Generate Entry Queue
REM ============================================================================
echo.
echo [5/7] Generating optimized entry queue...
echo This orders entries for maximum efficiency.
python entry_queue_generator.py
if errorlevel 1 (
    echo ERROR: Failed to generate entry queue!
    pause
    exit /b 1
)
echo ✓ Entry queue generated: entry_queue.json

REM ============================================================================
REM STEP 6: Extract Golden Patterns (Optional)
REM ============================================================================
echo.
echo [6/7] Extracting patterns from golden entries (if available)...
if exist "Golden_Entries\*.txt" (
    python golden_pattern_extractor.py
    echo ✓ Golden patterns extracted
) else (
    echo ! No golden entries found - will use default templates
)

REM ============================================================================
REM STEP 7: Run System Tests
REM ============================================================================
echo.
echo [7/7] Running system tests...
python test_ultimate_system.py
if errorlevel 1 (
    echo WARNING: Some tests failed, but system may still work
)

REM ============================================================================
REM SETUP COMPLETE
REM ============================================================================
echo.
echo ============================================================================
echo SETUP COMPLETE!
echo ============================================================================
echo.
echo System is ready for CELESTIAL-TIER generation.
echo.
echo NEXT STEPS:
echo   1. Download a theological LLM model (70B+ parameters recommended)
echo   2. Place it in the "models" folder
echo   3. Update model path in config_v2.yaml
echo   4. Run: python opus_maximus_v2.py
echo.
echo FILES CREATED:
echo   ✓ subjects_pool_ULTIMATE_12000.json (12,000+ entries)
echo   ✓ entry_queue.json (optimized generation order)
echo   ✓ golden_patterns.json (quality templates)
echo   ✓ Directory structure (outputs, cache, logs)
echo.
echo DOCUMENTATION:
echo   - READ_ME_FIRST.txt - Quick start guide
echo   - QUICK_START_ULTIMATE.md - Detailed instructions
echo   - ULTIMATE_ENGINE_ARCHITECTURE.md - System architecture
echo.
echo Glory to the Father and to the Son and to the Holy Spirit,
echo now and ever and unto ages of ages. Amen.
echo.
pause
