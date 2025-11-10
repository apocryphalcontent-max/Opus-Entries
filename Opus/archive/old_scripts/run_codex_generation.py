"""
OPUS MAXIMUS - MASTER ORCHESTRATOR
=====================================
The fully automated "manager" agent for the 12,000-entry codex.

This script is the missing piece for "fully automated" generation.
It is designed to be a long-running process that:
1.  Loads the master 12,000-entry queue (from generate_entry_queue.py).
2.  Scans the output directory to find already-completed entries.
3.  Determines the next highest-priority (Tier S+ > S > A > B > C) entry to generate.
4.  Invokes the "worker" agent (OpusMaximusAgenticGenerator) for that single entry.
5.  Logs the result (success/failure) to orchestrator.log.
6.  Loops to find the next entry, running until the 12,000-entry queue is complete.

Usage:
    python run_codex_generation.py \
        --model-path ./models/Qwen2.5-Coder-14B-Instruct-Q8.gguf \
        --queue-file ./ENTRY_GENERATION_QUEUE.json \
        --n-gpu-layers -1
"""

import sys
import logging
from pathlib import Path
import argparse
import time
from typing import Optional, Dict, List, Set

try:
    import orjson
    from rich.console import Console
    from rich.logging import RichHandler
    from opus_maximus_master_generator import OpusMaximusAgenticGenerator
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Please ensure all dependencies from requirements.txt are installed.")
    sys.exit(1)

# --- Logging Setup ---
# We create a new log file just for this master process
log_format = '%(asctime)s [%(levelname)s] (Orchestrator) %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler('orchestrator.log'),
        RichHandler(console=Console(stderr=True), rich_tracebacks=True)
    ]
)
logger = logging.getLogger("rich")

# --- Configuration ---
DEFAULT_QUEUE_FILE = 'ENTRY_GENERATION_QUEUE.json'
DEFAULT_OUTPUT_DIR = 'GENERATED_ENTRIES_MASTER'
DEFAULT_GOLDEN_DIR = 'OPUS_MAXIMUS_INDIVIDUALIZED/Enhancement_Corpus'
TIER_PRIORITY = ['S+', 'S', 'A', 'B', 'C']


class MasterOrchestrator:
    """
    The "manager" agent that finds the next job and tells the "worker"
    (OpusMaximusAgenticGenerator) to execute it.
    """
    def __init__(self, generator_args: Dict):
        self.output_dir = Path(generator_args['output_dir'])
        self.queue_file = Path(generator_args['queue_file'])
        self.master_queue = self.load_master_queue()
        
        logger.info("Initializing OpusMaximusAgenticGenerator (the 'worker')...")
        try:
            self.generator = OpusMaximusAgenticGenerator(
                model_path=generator_args['model_path'],
                golden_dir=Path(generator_args['golden_dir']),
                output_dir=self.output_dir,
                n_gpu_layers=generator_args['n_gpu_layers'],
                n_ctx=generator_args['n_ctx']
            )
            logger.info("Worker agent (OpusMaximusAgenticGenerator) initialized successfully.")
        except Exception as e:
            logger.error(f"FATAL: Could not initialize worker agent: {e}", exc_info=True)
            logger.error("Please ensure your model path is correct and all dependencies are installed.")
            sys.exit(1)

    def load_master_queue(self) -> List[Dict]:
        """Loads the 12,000-entry JSON queue file."""
        if not self.queue_file.exists():
            logger.error(f"FATAL: Master queue file not found: {self.queue_file}")
            logger.error(f"Please run `generate_entry_queue.py` to create it.")
            sys.exit(1)
        
        logger.info(f"Loading master queue from {self.queue_file}...")
        with open(self.queue_file, 'rb') as f:
            queue = orjson.loads(f.read())
        logger.info(f"Loaded {len(queue):,} total entries from queue.")
        return queue

    def get_completed_entries(self) -> Set[str]:
        """Scans the output directory for all completed .md files."""
        if not self.output_dir.exists():
            logger.warning(f"Output directory not found. Creating: {self.output_dir}")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return set()
        
        # Use rglob to find all .md files in all subdirectories
        completed_files = self.output_dir.rglob('*.md')
        
        # We store entries by a normalized "subject" key
        # e.g., "The Book of Revelation" -> "the_book_of_revelation"
        completed_set = {
            self._normalize_subject(f.stem) for f in completed_files
        }
        
        logger.info(f"Found {len(completed_set)} already completed entries.")
        return completed_set

    def _normalize_subject(self, subject: str) -> str:
        """Creates a consistent key from a subject name."""
        return subject.lower().replace(' ', '_').replace(':', '')

    def get_next_entry_to_generate(self) -> Optional[Dict]:
        """
        Finds the next highest-priority entry in the queue that has not
        already been completed.
        """
        completed = self.get_completed_entries()
        
        # Sort the master queue by our defined priority
        try:
            sorted_queue = sorted(
                self.master_queue,
                key=lambda x: TIER_PRIORITY.index(x.get('tier', 'C'))
            )
        except ValueError as e:
            logger.error(f"FATAL: An entry in {self.queue_file} has an invalid tier: {e}")
            logger.error(f"Valid tiers are: {TIER_PRIORITY}")
            sys.exit(1)

        for entry in sorted_queue:
            subject_key = self._normalize_subject(entry.get('subject', ''))
            if not subject_key:
                logger.warning(f"Skipping malformed queue entry: {entry}")
                continue
                
            if subject_key not in completed:
                logger.info(f"Next entry selected (Priority: {entry['tier']}): {entry['subject']}")
                return entry
        
        # If we get here, all entries are complete
        return None

    def run_generation_loop(self):
        """
        The main control loop for the fully automated generation process.
        """
        logger.info("===== MASTER ORCHESTRATOR: ONLINE =====")
        logger.info("Starting automated generation loop. Press Ctrl+C to stop.")
        
        while True:
            try:
                next_entry = self.get_next_entry_to_generate()
                
                if next_entry is None:
                    logger.info("===== ALL ENTRIES COMPLETE =====")
                    logger.info("Master queue is finished. Shutting down orchestrator.")
                    break
                
                subject = next_entry['subject']
                tier = next_entry['tier']
                category = next_entry['category']
                
                logger.info(f"--- Starting generation for: {subject} (Tier {tier}) ---")
                start_time = time.time()
                
                try:
                    # Invoke the "worker" agent for this single job
                    result = self.generator.generate_entry(subject, tier, category)
                    end_time = time.time()
                    
                    if result and result.approved:
                        logger.info(f"--- SUCCESS: Completed '{subject}' in {end_time - start_time:.2f}s ---")
                    else:
                        logger.error(f"--- FAILED: Generation for '{subject}' was not approved by worker agent. ---")
                
                except Exception as e:
                    end_time = time.time()
                    logger.error(f"--- CRITICAL FAILURE: Unhandled exception during generation for '{subject}': {e} ---", exc_info=True)
                    # Log the error but continue to the next entry to ensure robustness
                
                # Wait for a moment before starting the next job
                time.sleep(10)
            
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt detected. Shutting down orchestrator...")
                break
            except Exception as e:
                logger.error(f"FATAL ORCHESTRATOR ERROR: {e}", exc_info=True)
                logger.error("The orchestrator will sleep for 60 seconds and attempt to restart.")
                time.sleep(60)

        logger.info("===== MASTER ORCHESTRATOR: OFFLINE =====")
        self.generator.cleanup()


def main():
    parser = argparse.ArgumentParser(description="Opus Maximus Master Orchestrator (GPU-Native)")
    parser.add_argument('--model-path', required=True, help='Path to GGUF model file')
    parser.add_argument('--queue-file', default=DEFAULT_QUEUE_FILE, help=f"Master JSON queue file (default: {DEFAULT_QUEUE_FILE})")
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument('--golden-dir', default=DEFAULT_GOLDEN_DIR, help=f"Golden corpus directory (default: {DEFAULT_GOLDEN_DIR})")
    parser.add_argument('--n-gpu-layers', type=int, default=-1, help='Number of GPU layers to offload (-1 for all)')
    parser.add_argument('--n-ctx', type=int, default=8192, help='Context window size')
    
    args = parser.parse_args()
    
    # Pack args for the generator
    generator_args = {
        'model_path': args.model_path,
        'golden_dir': args.golden_dir,
        'output_dir': args.output_dir,
        'n_gpu_layers': args.n_gpu_layers,
        'n_ctx': args.n_ctx,
        'queue_file': args.queue_file  # Orchestrator needs this
    }

    orchestrator = MasterOrchestrator(generator_args)
    orchestrator.run_generation_loop()

if __name__ == "__main__":
    main()