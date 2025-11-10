"""
OPUS MAXIMUS ULTIMATE: SYSTEM TEST
==================================

Tests all 7 core files to ensure they work correctly:
1. opus_maximus_v2.py
2. entry_queue_generator.py
3. subjects_pool_ULTIMATE_12000.py
4. golden_pattern_extractor.py
5. config_v2.yaml
6. requirements.txt
7. test_ultimate_system.py (this file)
"""

import sys
import json
from pathlib import Path
import yaml

def test_imports():
    """Test that all files can be imported without errors"""
    print("="*80)
    print("TEST 1: IMPORT VALIDATION")
    print("="*80)
    
    errors = []
    
    # Test 1: golden_pattern_extractor.py
    try:
        import golden_pattern_extractor
        print("✓ golden_pattern_extractor.py imports successfully")
    except Exception as e:
        errors.append(f"✗ golden_pattern_extractor.py: {e}")
        print(f"✗ golden_pattern_extractor.py: {e}")
    
    # Test 2: entry_queue_generator.py  
    try:
        import entry_queue_generator
        print("✓ entry_queue_generator.py imports successfully")
    except Exception as e:
        errors.append(f"✗ entry_queue_generator.py: {e}")
        print(f"✗ entry_queue_generator.py: {e}")
    
    # Test 3: subjects_pool_ULTIMATE_12000.py
    try:
        import subjects_pool_ULTIMATE_12000
        print("✓ subjects_pool_ULTIMATE_12000.py imports successfully")
    except Exception as e:
        errors.append(f"✗ subjects_pool_ULTIMATE_12000.py: {e}")
        print(f"✗ subjects_pool_ULTIMATE_12000.py: {e}")
    
    # Test 4: opus_maximus_v2.py
    try:
        import opus_maximus_v2
        print("✓ opus_maximus_v2.py imports successfully")
    except Exception as e:
        errors.append(f"✗ opus_maximus_v2.py: {e}")
        print(f"✗ opus_maximus_v2.py: {e}")
    
    return errors


def test_documentation():
    """Test that all documentation files exist and are readable"""
    print("\n" + "="*80)
    print("TEST 2: DOCUMENTATION VALIDATION")
    print("="*80)
    
    errors = []
    docs = [
        "ULTIMATE_ENGINE_ARCHITECTURE.md",
        "ULTIMATE_INTEGRATION_SUMMARY.md",
        "QUICK_START_ULTIMATE.md",
        "VISUAL_ARCHITECTURE_SUMMARY.txt",
        "README_ULTIMATE.md"
    ]
    
    for doc in docs:
        doc_path = Path(doc)
        if doc_path.exists():
            size = doc_path.stat().st_size
            print(f"✓ {doc} exists ({size:,} bytes)")
        else:
            errors.append(f"✗ {doc} not found")
            print(f"✗ {doc} not found")
    
    return errors


def test_golden_pattern_extractor():
    """Test golden pattern extractor functionality"""
    print("\n" + "="*80)
    print("TEST 3: GOLDEN PATTERN EXTRACTOR")
    print("="*80)
    
    errors = []
    
    try:
        from golden_pattern_extractor import GoldenEntryAnalyzer
        
        analyzer = GoldenEntryAnalyzer()
        print("✓ GoldenEntryAnalyzer instantiated")
        
        # Check if Golden_Entries directory exists
        golden_dir = Path("Golden_Entries")
        if not golden_dir.exists():
            print("⚠ Warning: Golden_Entries/ directory not found")
            print("  Create this directory and add golden entries to test extraction")
            return []
        
        # Check for markdown files
        md_files = list(golden_dir.glob("*.md"))
        if len(md_files) == 0:
            print("⚠ Warning: No .md files in Golden_Entries/")
            return []
        
        print(f"✓ Found {len(md_files)} golden entries")
        
        # Test on first entry if available
        if md_files:
            first_entry = md_files[0]
            print(f"✓ Testing extraction on: {first_entry.name}")
            
            try:
                pattern = analyzer.analyze_golden_entry(first_entry)
                print(f"✓ Extraction successful!")
                print(f"  - Vocabulary score: {pattern.vocabulary.avg_word_length:.2f} avg chars")
                print(f"  - Sentences: {pattern.sentences.avg_sentence_length:.1f} avg words")
                print(f"  - Overall quality: {pattern.overall_score:.4f}")
            except Exception as e:
                errors.append(f"✗ Extraction failed: {e}")
                print(f"✗ Extraction failed: {e}")
        
    except Exception as e:
        errors.append(f"✗ Golden pattern extractor error: {e}")
        print(f"✗ Error: {e}")
    
    return errors


def test_subjects_pool_generator():
    """Test subjects pool generator"""
    print("\n" + "="*80)
    print("TEST 4: SUBJECTS POOL GENERATOR")
    print("="*80)
    
    errors = []
    
    try:
        from subjects_pool_ULTIMATE_12000 import generate_ultimate_subjects_pool
        
        subjects = generate_ultimate_subjects_pool()
        print(f"✓ Generated {len(subjects)} subjects")
        
        # Validate structure
        if subjects:
            first = subjects[0]
            required_keys = ['name', 'tier', 'category', 'description', 'estimated_difficulty']
            
            for key in required_keys:
                if key in first:
                    print(f"✓ Required field '{key}' present")
                else:
                    errors.append(f"✗ Missing required field: {key}")
                    print(f"✗ Missing required field: {key}")
        
        # Test JSON serialization
        try:
            json_str = json.dumps(subjects, indent=2)
            print(f"✓ Subjects are JSON-serializable")
        except Exception as e:
            errors.append(f"✗ JSON serialization failed: {e}")
            print(f"✗ JSON serialization failed: {e}")
            
    except Exception as e:
        errors.append(f"✗ Subjects pool generator error: {e}")
        print(f"✗ Error: {e}")
    
    return errors


def test_entry_queue_generator():
    """Test entry queue generator (without running full generation)"""
    print("\n" + "="*80)
    print("TEST 5: ENTRY QUEUE GENERATOR")
    print("="*80)
    
    errors = []
    
    try:
        from entry_queue_generator import EntryQueueGenerator, SubjectAnalysis
        
        generator = EntryQueueGenerator()
        print("✓ EntryQueueGenerator instantiated")
        
        # Test SubjectAnalysis dataclass
        test_subject = SubjectAnalysis(
            name="Test Subject",
            tier="A",
            category="Test",
            theological_depth=0.5,
            patristic_requirements=3,
            controversies_involved=[],
            prerequisites=[],
            related_concepts=[],
            estimated_difficulty=0.5,
            estimated_words=1500,
            optimal_template="default",
            golden_entry_similarity=0.8
        )
        print("✓ SubjectAnalysis dataclass works correctly")
        
        # Check dependencies
        try:
            import networkx
            print("✓ NetworkX is available")
        except ImportError:
            errors.append("✗ NetworkX not installed (pip install networkx)")
            print("⚠ Warning: NetworkX not installed")
            print("  Install with: pip install networkx")
        
        try:
            import yaml
            print("✓ PyYAML is available")
        except ImportError:
            errors.append("✗ PyYAML not installed (pip install pyyaml)")
            print("⚠ Warning: PyYAML not installed")
            print("  Install with: pip install pyyaml")
        
    except Exception as e:
        errors.append(f"✗ Entry queue generator error: {e}")
        print(f"✗ Error: {e}")
    
    return errors


def test_config():
    """Test configuration file"""
    print("\n" + "="*80)
    print("TEST 6: CONFIGURATION VALIDATION")
    print("="*80)
    
    errors = []
    
    try:
        config_path = Path("config_v2.yaml")
        if not config_path.exists():
            errors.append("✗ config_v2.yaml not found")
            print("✗ config_v2.yaml not found")
            return errors
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✓ config_v2.yaml is valid YAML")
        
        # Check required sections
        required_sections = ['model', 'generation', 'validation', 'caching', 'paths']
        for section in required_sections:
            if section in config:
                print(f"✓ Section '{section}' present")
            else:
                errors.append(f"✗ Missing section: {section}")
                print(f"✗ Missing section: {section}")
        
    except Exception as e:
        errors.append(f"✗ Config validation error: {e}")
        print(f"✗ Error: {e}")
    
    return errors


def test_requirements():
    """Test requirements.txt"""
    print("\n" + "="*80)
    print("TEST 7: REQUIREMENTS VALIDATION")
    print("="*80)
    
    errors = []
    
    try:
        req_path = Path("requirements.txt")
        if not req_path.exists():
            errors.append("✗ requirements.txt not found")
            print("✗ requirements.txt not found")
            return errors
        
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✓ requirements.txt exists ({len(lines)} lines)")
        
        # Check for critical dependencies
        critical_deps = ['pyyaml', 'langchain', 'llama-cpp-python', 'chromadb', 
                        'networkx', 'rich', 'sentence-transformers']
        
        content = "".join(lines).lower()
        for dep in critical_deps:
            if dep in content:
                print(f"✓ Critical dependency '{dep}' listed")
            else:
                errors.append(f"⚠ Missing recommended dependency: {dep}")
                print(f"⚠ Warning: '{dep}' not found in requirements")
        
    except Exception as e:
        errors.append(f"✗ Requirements validation error: {e}")
        print(f"✗ Error: {e}")
    
    return errors


def main():
    """Run all tests"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "OPUS MAXIMUS ULTIMATE SYSTEM TEST" + " "*25 + "║")
    print("╚" + "="*78 + "╝")
    
    all_errors = []
    
    # Run all tests
    all_errors.extend(test_imports())
    all_errors.extend(test_documentation())
    all_errors.extend(test_golden_pattern_extractor())
    all_errors.extend(test_subjects_pool_generator())
    all_errors.extend(test_entry_queue_generator())
    all_errors.extend(test_config())
    all_errors.extend(test_requirements())
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if not all_errors:
        print("✅ ALL TESTS PASSED!")
        print("\nSystem is ready for:")
        print("  1. Generate subjects pool: python subjects_pool_ULTIMATE_12000.py")
        print("  2. Generate entry queue: python entry_queue_generator.py")
        print("  3. Extract patterns: python golden_pattern_extractor.py")
        print("  4. Run generator: python opus_maximus_v2.py")
        return 0
    else:
        print(f"❌ {len(all_errors)} ERROR(S) DETECTED:")
        for error in all_errors:
            print(f"  {error}")
        print("\nPlease resolve errors before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if all_errors:
        print(f"\n❌ {len(all_errors)} ERROR(S) FOUND:\n")
        for error in all_errors:
            print(f"  {error}")
        print("\nPlease fix these errors before proceeding.")
        return False
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("\nSystem is ready for use. Next steps:")
        print("  1. Run: python golden_pattern_extractor.py")
        print("  2. Run: python subjects_pool_generator.py")
        print("  3. Run: python entry_queue_generator.py")
        print("\nSee QUICK_START_ULTIMATE.md for detailed instructions.")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
