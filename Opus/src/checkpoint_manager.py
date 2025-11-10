"""
OPUS MAXIMUS - Checkpoint Manager
==================================
Manage generation checkpoints for resumable, fault-tolerant operation.
"""

import json
import pickle
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .error_handling import CheckpointError, ErrorContext

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class GenerationCheckpoint:
    """Checkpoint data for a generation in progress"""
    subject: str
    tier: str
    category: str
    timestamp: str
    phase: str  # "blueprint", "section_X", "assembly", "validation"

    # Generation state
    blueprint: Optional[str] = None
    sections: Dict[str, str] = None
    metadata: Dict[str, Any] = None

    # Progress tracking
    sections_completed: List[str] = None
    sections_remaining: List[str] = None
    attempts: Dict[str, int] = None

    # Validation results
    validation_results: Dict[str, Any] = None

    def __post_init__(self):
        if self.sections is None:
            self.sections = {}
        if self.metadata is None:
            self.metadata = {}
        if self.sections_completed is None:
            self.sections_completed = []
        if self.sections_remaining is None:
            self.sections_remaining = []
        if self.attempts is None:
            self.attempts = {}


# ============================================================================
# CHECKPOINT MANAGER
# ============================================================================

class CheckpointManager:
    """
    Manage generation checkpoints for resumability.

    Features:
    - Save/load generation state
    - Progress tracking
    - Automatic cleanup
    - Corruption detection
    - Multiple checkpoint formats (JSON + pickle)
    """

    def __init__(self, checkpoint_dir: Path):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Checkpoint manager initialized: {self.checkpoint_dir}")

    def save_checkpoint(
        self,
        subject: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save generation checkpoint.

        Args:
            subject: Subject being generated
            state: Generation state dictionary
            metadata: Optional metadata

        Returns:
            Path to saved checkpoint

        Raises:
            CheckpointError: If save fails
        """
        with ErrorContext(f"Saving checkpoint for {subject}"):
            try:
                checkpoint_id = self._generate_checkpoint_id(subject)
                checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
                pickle_file = self.checkpoint_dir / f"{checkpoint_id}.pkl"

                # Create checkpoint data
                checkpoint_data = {
                    'subject': subject,
                    'timestamp': datetime.now().isoformat(),
                    'state': state,
                    'metadata': metadata or {},
                    'version': '1.0',
                    'checksum': self._calculate_checksum(state)
                }

                # Save as JSON (human-readable)
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

                # Save as pickle (for complex objects)
                with open(pickle_file, 'wb') as f:
                    pickle.dump(checkpoint_data, f, protocol=pickle.HIGHEST_PROTOCOL)

                logger.info(f"Checkpoint saved: {checkpoint_file}")
                logger.debug(f"Checkpoint phase: {state.get('phase', 'unknown')}")

                return checkpoint_file

            except Exception as e:
                raise CheckpointError(f"Failed to save checkpoint: {e}") from e

    def load_checkpoint(self, subject: str) -> Optional[Dict[str, Any]]:
        """
        Load most recent checkpoint for subject.

        Args:
            subject: Subject to load checkpoint for

        Returns:
            Checkpoint data or None if not found

        Raises:
            CheckpointError: If checkpoint is corrupted
        """
        with ErrorContext(f"Loading checkpoint for {subject}", raise_on_error=False):
            checkpoint_id = self._generate_checkpoint_id(subject)
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            pickle_file = self.checkpoint_dir / f"{checkpoint_id}.pkl"

            # Try JSON first
            if checkpoint_file.exists():
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Verify checksum
                    if not self._verify_checksum(data):
                        logger.warning("Checkpoint checksum mismatch, trying pickle")
                        raise CheckpointError("Checksum verification failed")

                    logger.info(f"Checkpoint loaded: {checkpoint_file}")
                    logger.debug(f"Checkpoint timestamp: {data.get('timestamp')}")

                    return data

                except Exception as e:
                    logger.warning(f"Failed to load JSON checkpoint: {e}")

            # Try pickle as fallback
            if pickle_file.exists():
                try:
                    with open(pickle_file, 'rb') as f:
                        data = pickle.load(f)

                    logger.info(f"Checkpoint loaded from pickle: {pickle_file}")
                    return data

                except Exception as e:
                    logger.error(f"Failed to load pickle checkpoint: {e}")
                    raise CheckpointError(f"Corrupted checkpoint: {e}") from e

            logger.debug(f"No checkpoint found for {subject}")
            return None

    def delete_checkpoint(self, subject: str) -> bool:
        """
        Delete checkpoint after successful completion.

        Args:
            subject: Subject to delete checkpoint for

        Returns:
            True if deleted, False if not found
        """
        checkpoint_id = self._generate_checkpoint_id(subject)
        deleted = False

        for suffix in ['.json', '.pkl']:
            file_path = self.checkpoint_dir / f"{checkpoint_id}{suffix}"
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted checkpoint: {file_path}")
                deleted = True

        if deleted:
            logger.info(f"Checkpoint deleted for {subject}")

        return deleted

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.

        Returns:
            List of checkpoint info dictionaries
        """
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                checkpoints.append({
                    'subject': data.get('subject'),
                    'timestamp': data.get('timestamp'),
                    'phase': data.get('state', {}).get('phase'),
                    'file': str(checkpoint_file)
                })

            except Exception as e:
                logger.warning(f"Could not read checkpoint {checkpoint_file}: {e}")

        return sorted(checkpoints, key=lambda x: x['timestamp'], reverse=True)

    def get_progress(self, subject: str) -> Optional[Dict[str, Any]]:
        """
        Get progress information for a subject.

        Args:
            subject: Subject to check

        Returns:
            Progress info or None if no checkpoint
        """
        checkpoint = self.load_checkpoint(subject)
        if not checkpoint:
            return None

        state = checkpoint.get('state', {})
        sections_completed = state.get('sections_completed', [])
        sections_remaining = state.get('sections_remaining', [])

        total_sections = len(sections_completed) + len(sections_remaining)
        progress_pct = (len(sections_completed) / total_sections * 100) if total_sections > 0 else 0

        return {
            'subject': subject,
            'phase': state.get('phase'),
            'progress': progress_pct,
            'sections_completed': len(sections_completed),
            'sections_remaining': len(sections_remaining),
            'timestamp': checkpoint.get('timestamp')
        }

    def cleanup_old_checkpoints(self, max_age_days: int = 30) -> int:
        """
        Delete checkpoints older than specified age.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of checkpoints deleted
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=max_age_days)
        deleted = 0

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                timestamp = datetime.fromisoformat(data.get('timestamp'))

                if timestamp < cutoff:
                    # Delete both JSON and pickle
                    checkpoint_id = checkpoint_file.stem
                    for suffix in ['.json', '.pkl']:
                        file_path = self.checkpoint_dir / f"{checkpoint_id}{suffix}"
                        if file_path.exists():
                            file_path.unlink()
                            deleted += 1

                    logger.debug(f"Deleted old checkpoint: {checkpoint_file}")

            except Exception as e:
                logger.warning(f"Could not process {checkpoint_file}: {e}")

        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old checkpoint files")

        return deleted

    def _generate_checkpoint_id(self, subject: str) -> str:
        """
        Generate unique checkpoint ID from subject.

        Args:
            subject: Subject name

        Returns:
            Checkpoint ID (MD5 hash)
        """
        return hashlib.md5(subject.encode('utf-8')).hexdigest()

    def _calculate_checksum(self, state: Dict[str, Any]) -> str:
        """
        Calculate checksum for state data.

        Args:
            state: State dictionary

        Returns:
            Checksum string
        """
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode('utf-8')).hexdigest()

    def _verify_checksum(self, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Verify checkpoint integrity.

        Args:
            checkpoint_data: Checkpoint data

        Returns:
            True if valid
        """
        try:
            stored_checksum = checkpoint_data.get('checksum')
            if not stored_checksum:
                return True  # Old checkpoint without checksum

            calculated = self._calculate_checksum(checkpoint_data.get('state', {}))
            return calculated == stored_checksum

        except Exception:
            return False


# ============================================================================
# RESUMABLE GENERATION MIXIN
# ============================================================================

class ResumableGenerationMixin:
    """
    Mixin to add checkpoint/resume capability to generators.

    Usage:
        class MyGenerator(ResumableGenerationMixin):
            def __init__(self):
                self.checkpoint_mgr = CheckpointManager(Path(".checkpoints"))

            def generate(self, subject):
                state = self.checkpoint_mgr.load_checkpoint(subject)
                if state:
                    return self._resume_generation(subject, state)
                else:
                    return self._start_new_generation(subject)
    """

    def save_progress(
        self,
        subject: str,
        phase: str,
        **state_data
    ):
        """
        Save generation progress.

        Args:
            subject: Subject being generated
            phase: Current phase
            **state_data: Additional state data
        """
        if not hasattr(self, 'checkpoint_mgr'):
            logger.warning("No checkpoint manager available")
            return

        state = {
            'phase': phase,
            **state_data
        }

        self.checkpoint_mgr.save_checkpoint(subject, state)

    def try_resume(self, subject: str) -> Optional[Dict[str, Any]]:
        """
        Try to resume from checkpoint.

        Args:
            subject: Subject to resume

        Returns:
            Checkpoint state or None
        """
        if not hasattr(self, 'checkpoint_mgr'):
            return None

        checkpoint = self.checkpoint_mgr.load_checkpoint(subject)
        if checkpoint:
            logger.info(
                f"Resuming from checkpoint: {subject} "
                f"(phase: {checkpoint.get('state', {}).get('phase')})"
            )
            return checkpoint.get('state')

        return None

    def mark_complete(self, subject: str):
        """
        Mark generation as complete and delete checkpoint.

        Args:
            subject: Subject that was completed
        """
        if hasattr(self, 'checkpoint_mgr'):
            self.checkpoint_mgr.delete_checkpoint(subject)
            logger.info(f"Marked {subject} as complete")
