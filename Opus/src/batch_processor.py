"""
OPUS MAXIMUS - Batch Processor
===============================
Process multiple entries from subject pools with progress tracking.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from tqdm import tqdm
import time

from .opus_engine import OpusMaximusEngine, GenerationResult
from .error_handling import GenerationError, ErrorContext

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class BatchStatistics:
    """Statistics for batch processing"""
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_words_generated: int = 0
    average_time_per_entry: float = 0.0
    average_quality_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubjectEntry:
    """Subject pool entry"""
    name: str
    tier: str = "Tier 1"
    category: str = "Theology"


# ============================================================================
# BATCH PROCESSOR
# ============================================================================

class BatchProcessor:
    """
    Process multiple entries from subject pool.

    Features:
    - Progress tracking with tqdm
    - Error logging and recovery
    - Skip existing entries
    - Comprehensive statistics
    - Resume capability (via checkpoints)
    """

    def __init__(
        self,
        engine: OpusMaximusEngine,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize batch processor.

        Args:
            engine: OpusMaximusEngine instance
            output_dir: Output directory (defaults to engine's output_dir)
        """
        self.engine = engine
        self.output_dir = output_dir or engine.config.output_dir
        self.stats = BatchStatistics()
        self.errors_log = []

        logger.info("Batch processor initialized")

    def process_pool(
        self,
        pool_file: Path,
        start_index: int = 0,
        max_entries: Optional[int] = None,
        skip_existing: bool = True,
        pause_between: float = 1.0
    ) -> BatchStatistics:
        """
        Process all entries in a subject pool.

        Args:
            pool_file: Path to subject pool JSON file
            start_index: Index to start from
            max_entries: Maximum entries to process (None = all)
            skip_existing: Skip already-generated entries
            pause_between: Seconds to pause between entries

        Returns:
            BatchStatistics with processing results
        """
        logger.info(f"Loading subject pool: {pool_file}")

        # Load subject pool
        with open(pool_file, 'r', encoding='utf-8') as f:
            pool_data = json.load(f)

        # Extract subjects
        if isinstance(pool_data, dict):
            subjects_data = pool_data.get('subjects', [])
        elif isinstance(pool_data, list):
            subjects_data = pool_data
        else:
            raise ValueError(f"Invalid pool file format: {pool_file}")

        # Parse subjects
        subjects = []
        for item in subjects_data:
            if isinstance(item, str):
                subjects.append(SubjectEntry(name=item))
            elif isinstance(item, dict):
                subjects.append(SubjectEntry(
                    name=item.get('name', item.get('subject', 'Unknown')),
                    tier=item.get('tier', 'Tier 1'),
                    category=item.get('category', 'Theology')
                ))

        # Apply filters
        if max_entries:
            subjects = subjects[start_index:start_index + max_entries]
        else:
            subjects = subjects[start_index:]

        # Initialize statistics
        self.stats = BatchStatistics(
            total=len(subjects),
            start_time=datetime.now().isoformat()
        )

        logger.info(
            f"Starting batch processing: {len(subjects)} entries "
            f"(start_index={start_index}, skip_existing={skip_existing})"
        )

        # Process with progress bar
        entry_times = []
        quality_scores = []

        with tqdm(
            total=len(subjects),
            desc="Generating entries",
            unit="entry"
        ) as pbar:
            for idx, subject in enumerate(subjects):
                try:
                    # Check if already exists
                    if skip_existing and self._entry_exists(subject.name, subject.tier):
                        logger.info(f"Skipping {subject.name} (already exists)")
                        self.stats.skipped += 1
                        pbar.set_postfix({
                            'completed': self.stats.completed,
                            'failed': self.stats.failed,
                            'skipped': self.stats.skipped,
                            'current': subject.name[:30]
                        })
                        pbar.update(1)
                        continue

                    # Generate entry
                    logger.info(
                        f"Processing {idx + 1}/{len(subjects)}: "
                        f"{subject.name} ({subject.tier})"
                    )

                    start = time.time()

                    result = self.engine.generate_entry(
                        subject=subject.name,
                        tier=subject.tier,
                        category=subject.category,
                        resume=True  # Always enable resume
                    )

                    elapsed = time.time() - start

                    # Update statistics
                    self.stats.completed += 1
                    self.stats.total_words_generated += result.word_count
                    entry_times.append(elapsed)
                    quality_scores.append(result.validation['score'])

                    # Update progress bar
                    pbar.set_postfix({
                        'completed': self.stats.completed,
                        'failed': self.stats.failed,
                        'skipped': self.stats.skipped,
                        'avg_time': f"{sum(entry_times)/len(entry_times):.1f}s",
                        'avg_score': f"{sum(quality_scores)/len(quality_scores):.3f}",
                        'current': subject.name[:30]
                    })
                    pbar.update(1)

                    logger.info(
                        f"Completed {subject.name}: "
                        f"{result.word_count} words, "
                        f"{elapsed:.1f}s, "
                        f"score: {result.validation['score']:.3f}"
                    )

                except GenerationError as e:
                    logger.error(f"Generation error for {subject.name}: {e}")
                    self.stats.failed += 1
                    self._log_error(subject.name, str(e))
                    pbar.update(1)
                    continue

                except Exception as e:
                    logger.error(f"Unexpected error for {subject.name}: {e}", exc_info=True)
                    self.stats.failed += 1
                    self._log_error(subject.name, f"Unexpected error: {e}")
                    pbar.update(1)
                    continue

                # Pause between entries to avoid overheating
                if pause_between > 0:
                    time.sleep(pause_between)

        # Finalize statistics
        self.stats.end_time = datetime.now().isoformat()

        if entry_times:
            self.stats.average_time_per_entry = sum(entry_times) / len(entry_times)
        if quality_scores:
            self.stats.average_quality_score = sum(quality_scores) / len(quality_scores)

        # Save statistics
        self._save_stats()

        # Print summary
        self._print_summary()

        logger.info(
            f"Batch processing complete: "
            f"{self.stats.completed} completed, "
            f"{self.stats.failed} failed, "
            f"{self.stats.skipped} skipped"
        )

        return self.stats

    def process_subjects_list(
        self,
        subjects: List[str],
        tier: str = "Tier 1",
        category: str = "Theology",
        skip_existing: bool = True
    ) -> BatchStatistics:
        """
        Process a list of subject names.

        Args:
            subjects: List of subject names
            tier: Tier to assign
            category: Category to assign
            skip_existing: Skip already-generated entries

        Returns:
            BatchStatistics
        """
        # Convert to SubjectEntry objects
        subject_entries = [
            SubjectEntry(name=name, tier=tier, category=category)
            for name in subjects
        ]

        # Create temporary pool file
        temp_pool = Path(".temp_pool.json")
        with open(temp_pool, 'w', encoding='utf-8') as f:
            json.dump([asdict(s) for s in subject_entries], f, indent=2)

        try:
            return self.process_pool(temp_pool, skip_existing=skip_existing)
        finally:
            # Clean up temp file
            if temp_pool.exists():
                temp_pool.unlink()

    def _entry_exists(self, subject: str, tier: str) -> bool:
        """Check if entry already generated"""
        safe_name = subject.replace(' ', '_').replace('/', '_')
        tier_dir = self.output_dir / tier.replace(' ', '_')

        # Check for markdown file
        md_file = tier_dir / f"{safe_name}.md"
        if md_file.exists():
            return True

        # Check in all tier directories if tier dir doesn't exist
        if not tier_dir.exists():
            for tier_dir in self.output_dir.glob("*/"):
                md_file = tier_dir / f"{safe_name}.md"
                if md_file.exists():
                    return True

        return False

    def _log_error(self, subject: str, error: str):
        """Log generation error"""
        error_entry = {
            'subject': subject,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }

        self.errors_log.append(error_entry)

        # Append to errors file
        error_file = self.output_dir / "errors.jsonl"
        with open(error_file, 'a', encoding='utf-8') as f:
            json.dump(error_entry, f, ensure_ascii=False)
            f.write('\n')

    def _save_stats(self):
        """Save batch statistics"""
        stats_file = self.output_dir / "batch_stats.json"

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Statistics saved: {stats_file}")

    def _print_summary(self):
        """Print batch processing summary"""
        print("\n" + "="*70)
        print("BATCH PROCESSING SUMMARY")
        print("="*70)

        print(f"\nTotal entries processed: {self.stats.total}")
        print(f"  Completed: {self.stats.completed}")
        print(f"  Failed: {self.stats.failed}")
        print(f"  Skipped: {self.stats.skipped}")

        if self.stats.completed > 0:
            print(f"\nGeneration metrics:")
            print(f"  Total words generated: {self.stats.total_words_generated:,}")
            print(f"  Average time per entry: {self.stats.average_time_per_entry:.1f}s")
            print(f"  Average quality score: {self.stats.average_quality_score:.3f}")

        if self.stats.start_time and self.stats.end_time:
            start = datetime.fromisoformat(self.stats.start_time)
            end = datetime.fromisoformat(self.stats.end_time)
            duration = (end - start).total_seconds()
            print(f"\nTotal time: {duration:.1f}s ({duration/60:.1f} minutes)")

        if self.stats.failed > 0:
            print(f"\n⚠ {self.stats.failed} entries failed. See errors.jsonl for details.")

        print("="*70 + "\n")


# ============================================================================
# CLI FUNCTION
# ============================================================================

def run_batch_from_cli(
    config_path: Path,
    pool_file: Path,
    start: int = 0,
    max_entries: Optional[int] = None,
    skip_existing: bool = True
):
    """
    Run batch processing from command line.

    Args:
        config_path: Path to configuration file
        pool_file: Path to subject pool
        start: Start index
        max_entries: Maximum entries to process
        skip_existing: Skip existing entries
    """
    from .opus_engine import create_engine_from_config

    logger.info(f"Loading configuration: {config_path}")
    engine = create_engine_from_config(config_path)

    logger.info("Initializing batch processor...")
    processor = BatchProcessor(engine)

    logger.info(f"Processing subject pool: {pool_file}")
    stats = processor.process_pool(
        pool_file=pool_file,
        start_index=start,
        max_entries=max_entries,
        skip_existing=skip_existing
    )

    print("\n✓ Batch processing complete!")
    print(f"Results saved to: {engine.config.output_dir}")

    return stats
