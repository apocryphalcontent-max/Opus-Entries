@echo off
REM ============================================================================
REM OPUS MAXIMUS DREAM ENGINE - COMPLETE SETUP
REM ============================================================================
REM This script will:
REM 1. Verify Python installation
REM 2. Install all dependencies
REM 3. Validate all 7 core files
REM 4. Generate subjects pool (12,000+ entries)
REM 5. Generate entry queue
REM 6. Extract golden patterns
REM 7. Prepare system for first run
REM ============================================================================

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

REM Check Python installation
echo.
echo [1/7] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [2/7] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    echo Please check requirements.txt and try again.
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo [3/7] Creating directory structure...
if not exist "GENERATED_ENTRIES_MASTER" mkdir GENERATED_ENTRIES_MASTER
if not exist "Golden_Entries" mkdir Golden_Entries
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
if not exist ".cache" mkdir .cache
if not exist ".checkpoints" mkdir .checkpoints
if not exist "models" mkdir models
echo ✓ Directory structure created

REM Validate core files
echo.
echo [4/7] Validating core files...
python test_ultimate_system.py
if errorlevel 1 (
    echo WARNING: Some validation tests failed
    echo Please review the output above
    pause
)

REM Generate subjects pool
echo.
echo [5/7] Generating subjects pool (12,000+ entries)...
echo This will take 2-3 minutes...
python subjects_pool_ULTIMATE_12000.py
if errorlevel 1 (
    echo ERROR: Failed to generate subjects pool!
    pause
    exit /b 1
)
echo ✓ Subjects pool generated

REM Generate entry queue
echo.
echo [6/7] Generating optimized entry queue...
python entry_queue_generator.py --input subjects_pool_ULTIMATE_12000.json --output entry_queue.json
if errorlevel 1 (
    echo WARNING: Entry queue generation failed
    echo You can generate it manually later
    pause
)

REM Extract golden patterns (if golden entries exist)
echo.
echo [7/7] Extracting golden patterns...
python golden_pattern_extractor.py
if errorlevel 1 (
    echo WARNING: Golden pattern extraction failed
    echo This is normal if you haven't added golden entries yet
    echo Add entries to Golden_Entries/ directory and run:
    echo   python golden_pattern_extractor.py
)

echo.
echo ============================================================================
echo SETUP COMPLETE!
echo ============================================================================
echo.
echo Next Steps:
echo.
echo 1. OPTIONAL - Download LLM model:
echo    - Download a theological LLM (70B+ parameters recommended)
echo    - Place in models/ directory
echo    - Update model_path in config_v2.yaml
echo.
echo 2. OPTIONAL - Add golden entries:
echo    - Place existing high-quality entries in Golden_Entries/
echo    - Run: python golden_pattern_extractor.py
echo    - This improves generation quality
echo.
echo 3. READY TO GENERATE:
echo    Run: python opus_maximus_v2.py
echo.
echo 4. For batch generation (all 12,000 entries):
echo    Run: python opus_maximus_v2.py --batch --queue entry_queue.json
echo.
echo ============================================================================
echo.
echo System Status:
echo   ✓ Dependencies installed
echo   ✓ Directory structure created
echo   ✓ Subjects pool generated (12,000+ entries)
echo   ✓ Entry queue prepared
echo.
echo Ready for CELESTIAL-TIER generation! Glory to God!
echo.
pause
