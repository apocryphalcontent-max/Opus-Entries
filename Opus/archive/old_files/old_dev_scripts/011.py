"""
FILE 21: MARKDOWN OUTPUT MANAGER (LEAN)
=======================================
Minimal overhead markdown export. Direct markdown output with zero conversion time.
Designed for efficiency - no unnecessary processing.
File 11 of 20: Markdown Output
Optimized for: Zero-Overhead Direct Write
"""
import logging
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class MarkdownOutputManager:
    """Lean markdown output for fast export."""
    def __init__(self, output_dir: Path = Path("GENERATED_ENTRIES_MASTER")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_entry(self, entry_id: str, content: str, metadata: Dict = None) -> Path:
        """Save entry as markdown (no conversion, direct write)."""
        filename = f"{entry_id}.md"
        filepath = self.output_dir / filename
        
        # Prepend metadata as YAML front matter (minimal)
        output = ""
        if metadata:
            output += "---\n"
            output += f"id: {entry_id}\n"
            output += f"generated: {datetime.now().isoformat()}\n"
            output += f"status: approved\n"
            if "subject" in metadata:
                output += f"subject: {metadata['subject']}\n"
            if "tier" in metadata:
                output += f"tier: {metadata['tier']}\n"
            output += "---\n\n"
        
        output += content
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save markdown {filepath}: {e}")
            raise

    def save_batch(self, entries: Dict[str, str], metadata: Dict = None) -> int:
        """Save multiple entries. Returns count."""
        count = 0
        for entry_id, content in entries.items():
            try:
                self.save_entry(entry_id, content, metadata)
                count += 1
            except Exception as e:
                logger.error(f"Failed to save {entry_id} in batch: {e}")
        
        logger.info(f"Batch save complete: {count}/{len(entries)} entries saved")
        return count

markdown_output = MarkdownOutputManager()