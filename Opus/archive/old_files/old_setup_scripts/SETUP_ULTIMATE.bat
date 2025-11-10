@echo off
REM ============================================================================
REM OPUS MAXIMUS DREAM ENGINE - ULTIMATE SETUP
REM ============================================================================
REM
REM This script sets up the complete OPUS MAXIMUS system for generating
REM CELESTIAL-TIER Orthodox theological entries with highest academic rigor.
REM
REM Prerequisites:
REM   - Python 3.10+
REM   - 32GB RAM (recommended)
REM   - 16GB+ GPU VRAM (for LLM)
REM   - 500GB+ NVMe SSD
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

REM Step 1: Check Python
echo.
echo [1/7] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM Step 2: Install dependencies
echo.
echo [2/7] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM Step 3: Generate expanded subjects pool (3000+ entries)
echo.
echo [3/7] Generating EXPANDED subjects pool (3000+ entries)...
python subjects_pool_FINAL_EXPANDED.py
if errorlevel 1 (
    echo ERROR: Failed to generate subjects pool!
    pause
    exit /b 1
)

REM Step 4: Generate entry queue
echo.
echo [4/7] Generating optimized entry queue...
python entry_queue_generator.py
if errorlevel 1 (
    echo WARNING: Entry queue generation failed. This is optional.
)

REM Step 5: Extract golden patterns
echo.
echo [5/7] Extracting patterns from golden entries...
python golden_pattern_extractor.py
if errorlevel 1 (
    echo WARNING: Golden pattern extraction failed. This is optional.
)

REM Step 6: Create cache directories
echo.
echo [6/7] Creating cache and output directories...
if not exist "cache" mkdir cache
if not exist "cache\l1" mkdir cache\l1
if not exist "cache\l2" mkdir cache\l2
if not exist "cache\l3" mkdir cache\l3
if not exist "logs" mkdir logs
if not exist "GENERATED_ENTRIES_MASTER" mkdir GENERATED_ENTRIES_MASTER

REM Step 7: Test system
echo.
echo [7/7] Running system validation test...
python test_ultimate_system.py
if errorlevel 1 (
    echo WARNING: System test failed. Review logs.
)

echo.
echo ============================================================================
echo SETUP COMPLETE!
echo ============================================================================
echo.
echo Next Steps:
echo.
echo 1. CONFIGURE MODEL:
echo    Edit config_v2.yaml and set your LLM model path
echo.
echo 2. RUN SINGLE ENTRY TEST:
echo    run_opus.bat "Theosis"
echo.
echo 3. RUN BATCH GENERATION (3000+ entries):
echo    run_final_expanded.bat
echo.
echo 4. MONITOR PROGRESS:
echo    Check logs\ directory for detailed logs
echo    Check GENERATED_ENTRIES_MASTER\ for outputs
echo.
echo ============================================================================
echo.
pause
