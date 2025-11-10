#!/usr/bin/env python3
"""
Overnight batch processor - Automated batch generation with error handling and logging
Optimized for long-running unattended operation
"""
import sys
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from opus_entries import EntryGenerator, EntryValidator, EntryRefiner, CitationChecker


def setup_logging(log_dir="logs"):
    """Setup logging for overnight batch processing"""
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"overnight_batch_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file


def monitor_gpu_temperature():
    """
    Monitor GPU temperature (if nvidia-smi available)
    Returns temperature in Celsius or None if not available
    """
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return None


def overnight_batch_generate(
    topics_file,
    output_dir="output/overnight",
    model="mixtral:8x7b",
    celestial_only=True,
    max_refinement_attempts=3,
    thermal_threshold=80,  # Celsius
    error_recovery=True
):
    """
    Overnight batch generation with monitoring and error recovery
    
    Args:
        topics_file: Path to JSON file with topics list
        output_dir: Directory to save generated entries
        model: LLM model to use
        celestial_only: If True, refine until CELESTIAL tier achieved
        max_refinement_attempts: Maximum refinement attempts per entry
        thermal_threshold: GPU temperature threshold for automatic cooling
        error_recovery: If True, continue on errors and save progress
    """
    # Setup logging
    log_file = setup_logging()
    logging.info(f"Starting overnight batch generation")
    logging.info(f"Log file: {log_file}")
    
    # Load topics
    with open(topics_file, 'r') as f:
        topics = json.load(f)
    
    logging.info(f"Loaded {len(topics)} topics from {topics_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    try:
        generator = EntryGenerator()
        validator = EntryValidator()
        refiner = EntryRefiner()
        citation_checker = CitationChecker()
    except Exception as e:
        logging.error(f"Failed to initialize components: {e}")
        return
    
    # Progress tracking
    progress_file = os.path.join(output_dir, "progress.json")
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        logging.info(f"Resuming from progress: {progress['completed']}/{progress['total']} completed")
    else:
        progress = {
            "total": len(topics),
            "completed": 0,
            "celestial_first_pass": 0,
            "celestial_after_refinement": 0,
            "failed_celestial": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat()
        }
    
    # Process each topic
    for i, topic in enumerate(topics):
        if i < progress["completed"]:
            continue  # Skip already completed
        
        logging.info(f"\n{'='*80}")
        logging.info(f"[{i+1}/{len(topics)}] Processing: {topic}")
        
        try:
            # Check GPU temperature
            gpu_temp = monitor_gpu_temperature()
            if gpu_temp and gpu_temp > thermal_threshold:
                logging.warning(f"GPU temperature high ({gpu_temp}°C). Cooling down...")
                time.sleep(300)  # 5 minute cooldown
            
            # Generate entry
            start_time = time.time()
            logging.info("Phase 1: Generating entry...")
            entry = generator.generate(topic, model=model)
            
            # Validate
            logging.info("Phase 2: Validating...")
            result = validator.validate(entry)
            logging.info(f"Initial score: {result.score:.2f}/100 ({result.quality_tier.value})")
            
            # Citation check
            logging.info("Phase 3: Citation quality check...")
            citation_report = citation_checker.generate_citation_report(entry)
            logging.info(f"Citation score: {citation_report['scores']['composite']:.2f}/100")
            
            # Refinement if needed
            if celestial_only and result.score < 95:
                logging.info("Phase 4: Refining to CELESTIAL tier...")
                entry = refiner.refine_to_celestial(entry, model=model, max_attempts=max_refinement_attempts)
                
                result = validator.validate(entry)
                logging.info(f"Final score: {result.score:.2f}/100 ({result.quality_tier.value})")
                
                if result.score >= 95:
                    progress["celestial_after_refinement"] += 1
                else:
                    progress["failed_celestial"] += 1
                    logging.warning(f"Failed to achieve CELESTIAL")
            elif result.score >= 95:
                progress["celestial_first_pass"] += 1
            
            # Save entry
            filename = f"{topic.replace(' ', '_').replace('/', '_')}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(entry.to_markdown())
            
            elapsed = time.time() - start_time
            logging.info(f"✓ Completed in {elapsed/60:.1f} minutes")
            logging.info(f"Saved to: {filepath}")
            
            # Update progress
            progress["completed"] += 1
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
            
            # Cooldown between entries
            time.sleep(30)
            
        except Exception as e:
            logging.error(f"ERROR processing '{topic}': {e}")
            progress["errors"] += 1
            
            if not error_recovery:
                raise
            
            # Save progress and continue
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
            
            time.sleep(60)  # Extra cooldown after error
    
    # Final summary
    progress["end_time"] = datetime.now().isoformat()
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)
    
    logging.info(f"\n{'='*80}")
    logging.info("OVERNIGHT BATCH COMPLETE")
    logging.info(f"{'='*80}")
    logging.info(f"Total entries: {progress['total']}")
    logging.info(f"Completed: {progress['completed']}")
    logging.info(f"CELESTIAL first-pass: {progress['celestial_first_pass']}")
    logging.info(f"CELESTIAL after refinement: {progress['celestial_after_refinement']}")
    logging.info(f"Failed CELESTIAL: {progress['failed_celestial']}")
    logging.info(f"Errors: {progress['errors']}")
    
    total_celestial = progress['celestial_first_pass'] + progress['celestial_after_refinement']
    if progress['completed'] > 0:
        logging.info(f"CELESTIAL rate: {total_celestial/progress['completed']*100:.1f}%")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Overnight batch entry generation")
    parser.add_argument("topics_file", help="Path to JSON file with topics list")
    parser.add_argument("--output-dir", default="output/overnight", help="Output directory")
    parser.add_argument("--model", default="mixtral:8x7b", help="LLM model to use")
    parser.add_argument("--no-celestial-mandate", action="store_true", help="Disable CELESTIAL mandate")
    parser.add_argument("--max-refinement-attempts", type=int, default=3, help="Max refinement attempts")
    parser.add_argument("--thermal-threshold", type=int, default=80, help="GPU temp threshold (C)")
    
    args = parser.parse_args()
    
    overnight_batch_generate(
        topics_file=args.topics_file,
        output_dir=args.output_dir,
        model=args.model,
        celestial_only=not args.no_celestial_mandate,
        max_refinement_attempts=args.max_refinement_attempts,
        thermal_threshold=args.thermal_threshold
    )
