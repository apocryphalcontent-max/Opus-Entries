"""
OPUS MAXIMUS ULTIMATE: SETUP & INSTALLATION
===========================================

Automated setup script that:
1. Checks Python version
2. Installs required dependencies
3. Validates all files
4. Creates necessary directories
5. Runs system tests
6. Provides next steps

Run this first before using the system.
"""

import sys
import subprocess
import platform
from pathlib import Path


class OpusMaximusSetup:
    """Setup and validation for Opus Maximus Ultimate"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.python_version = sys.version_info
        
    def print_header(self):
        """Print setup header"""
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*15 + "OPUS MAXIMUS ULTIMATE EDITION v3.0" + " "*29 + "║")
        print("║" + " "*25 + "SETUP & INSTALLATION" + " "*34 + "║")
        print("╚" + "="*78 + "╝\n")
    
    def check_python_version(self):
        """Check Python version (3.10+ required)"""
        print("="*80)
        print("STEP 1: PYTHON VERSION CHECK")
        print("="*80)
        
        major, minor = self.python_version.major, self.python_version.minor
        version_str = f"{major}.{minor}.{self.python_version.micro}"
        
        print(f"\nDetected Python version: {version_str}")
        print(f"Platform: {platform.system()} {platform.machine()}")
        
        if major < 3 or (major == 3 and minor < 10):
            self.errors.append(f"Python 3.10+ required, found {version_str}")
            print(f"❌ Python 3.10+ required, found {version_str}")
            return False
        else:
            print(f"✅ Python version OK ({version_str})")
            return True
    
    def check_dependencies(self):
        """Check if required packages are installed"""
        print("\n" + "="*80)
        print("STEP 2: DEPENDENCY CHECK")
        print("="*80)
        
        dependencies = {
            'networkx': 'Graph analysis for dependency ordering',
            'pyyaml': 'YAML configuration parsing',
        }
        
        missing = []
        
        for package, description in dependencies.items():
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}: {description}")
            except ImportError:
                print(f"❌ {package}: NOT INSTALLED - {description}")
                missing.append(package)
        
        return missing
    
    def install_dependencies(self, missing):
        """Install missing dependencies"""
        if not missing:
            print("\n✅ All dependencies already installed")
            return True
        
        print("\n" + "="*80)
        print("STEP 3: INSTALLING DEPENDENCIES")
        print("="*80)
        
        print(f"\nInstalling {len(missing)} missing package(s)...")
        
        for package in missing:
            print(f"\nInstalling {package}...")
            try:
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    package,
                    "--quiet"
                ])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                self.errors.append(f"Failed to install {package}: {e}")
                print(f"❌ Failed to install {package}")
                return False
        
        print("\n✅ All dependencies installed successfully")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n" + "="*80)
        print("STEP 4: DIRECTORY STRUCTURE")
        print("="*80)
        
        directories = [
            "Golden_Entries",
            "GENERATED_ENTRIES_MASTER",
            "cache",
            "logs"
        ]
        
        for dir_name in directories:
            dir_path = Path(dir_name)
            if dir_path.exists():
                print(f"✅ {dir_name}/ already exists")
            else:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ {dir_name}/ created")
    
    def validate_files(self):
        """Validate all 7 new files exist"""
        print("\n" + "="*80)
        print("STEP 5: FILE VALIDATION")
        print("="*80)
        
        required_files = {
            'Code Files': [
                'golden_pattern_extractor.py',
                'entry_queue_generator.py',
                'subjects_pool_generator.py'
            ],
            'Documentation': [
                'ULTIMATE_ENGINE_ARCHITECTURE.md',
                'ULTIMATE_INTEGRATION_SUMMARY.md',
                'QUICK_START_ULTIMATE.md',
                'VISUAL_ARCHITECTURE_SUMMARY.txt',
                'README_ULTIMATE.md'
            ]
        }
        
        all_valid = True
        
        for category, files in required_files.items():
            print(f"\n{category}:")
            for filename in files:
                file_path = Path(filename)
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"  ✅ {filename} ({size:,} bytes)")
                else:
                    print(f"  ❌ {filename} NOT FOUND")
                    self.errors.append(f"Missing file: {filename}")
                    all_valid = False
        
        return all_valid
    
    def run_system_tests(self):
        """Run system tests"""
        print("\n" + "="*80)
        print("STEP 6: SYSTEM TESTS")
        print("="*80)
        
        try:
            # Import test module
            import test_ultimate_system
            
            # Run tests
            print("\nRunning comprehensive system tests...\n")
            success = test_ultimate_system.main()
            
            return success
        except Exception as e:
            self.errors.append(f"System test failed: {e}")
            print(f"\n❌ System test failed: {e}")
            return False
    
    def print_next_steps(self):
        """Print next steps for user"""
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        
        print("""
QUICK START (5 Steps):

1. EXTRACT GOLDEN PATTERNS (5 min)
   cd "C:\\Users\\Edwin Boston\\Desktop\\Opus"
   python golden_pattern_extractor.py
   
   → Analyzes Golden_Entries/*.md
   → Creates golden_patterns.json

2. CREATE SUBJECTS POOL (varies)
   python subjects_pool_generator.py
   → Creates subjects_pool_sample.json (60 sample subjects)
   
   OR manually create subjects_pool.json with 12,000 subjects

3. GENERATE ENTRY QUEUE (2 min)
   python entry_queue_generator.py
   → Creates entry_queue.json (strategically ordered)

4. INTEGRATE WITH YOUR ENGINE (30 min)
   - Enhance opus_maximus_v2.py with template loading
   - See QUICK_START_ULTIMATE.md for code examples

5. DEPLOY TO PRODUCTION (9 months, 24/7)
   - Process entire queue
   - Monitor quality dashboard
   - Human review celestial entries

READ THESE FIRST:
  1. README_ULTIMATE.md - System overview
  2. QUICK_START_ULTIMATE.md - Getting started guide  
  3. ULTIMATE_INTEGRATION_SUMMARY.md - How it all works

SUPPORT:
  - Check documentation files for detailed guidance
  - All Python files have comprehensive docstrings
  - VISUAL_ARCHITECTURE_SUMMARY.txt provides diagrams
        """)
    
    def print_summary(self):
        """Print setup summary"""
        print("\n" + "="*80)
        print("SETUP SUMMARY")
        print("="*80)
        
        if self.errors:
            print(f"\n❌ SETUP FAILED - {len(self.errors)} ERROR(S):\n")
            for error in self.errors:
                print(f"  • {error}")
            print("\nPlease fix these errors and run setup again.")
            return False
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNING(S):\n")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print("\n✅ SETUP COMPLETE!")
        print("\nOPUS MAXIMUS ULTIMATE v3.0 is ready for use.")
        print("\nGlory to the Father and to the Son and to the Holy Spirit,")
        print("now and ever and unto ages of ages. Amen. ✝")
        
        return True
    
    def run(self):
        """Run complete setup process"""
        self.print_header()
        
        # Step 1: Python version
        if not self.check_python_version():
            self.print_summary()
            return False
        
        # Step 2: Dependencies
        missing = self.check_dependencies()
        
        # Step 3: Install dependencies
        if missing:
            if not self.install_dependencies(missing):
                self.print_summary()
                return False
        
        # Step 4: Create directories
        self.create_directories()
        
        # Step 5: Validate files
        if not self.validate_files():
            self.print_summary()
            return False
        
        # Step 6: Run tests
        if not self.run_system_tests():
            self.warnings.append("Some system tests failed - check output above")
        
        # Next steps
        self.print_next_steps()
        
        # Summary
        return self.print_summary()


def main():
    """Main entry point"""
    setup = OpusMaximusSetup()
    success = setup.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
