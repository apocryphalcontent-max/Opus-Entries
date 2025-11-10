"""
FILE 22: JSON BATCH EXPORT (LEAN)
==================================
Efficient JSON export for bulk archival and analysis.
No unnecessary formatting or processing.
File 12 of 20: JSON Export
Optimized for: Direct serialization with minimal overhead
"""
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONBatchExporter:
    """Lean JSON export for archival."""
    def __init__(self, output_dir: Path = Path("ARCHIVES")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_batch(self, entries: Dict[str, str], batch_name: str = None,
                     metadata: Dict = None) -> Path:
        """Export batch of entries as JSON (minimal, direct write)."""
        if batch_name is None:
            batch_name = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = self.output_dir / f"{batch_name}.json"
        
        # Minimal structure
        data = {
            "batch": batch_name,
            "timestamp": datetime.now().isoformat(),
            "count": len(entries),
            "entries": entries
        }
        if metadata:
            data["metadata"] = metadata
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # No indentation for size optimization in 'lean' mode
                json.dump(data, f, ensure_ascii=False, indent=None)
            logger.info(f"Exported batch: {filepath} ({len(entries)} entries)")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export batch {batch_name}: {e}")
            raise

    def export_index(self, batch_files: List[Path]) -> Path:
        """Create index of all batches (for quick lookup)."""
        index_file = self.output_dir / "index.json"
        index = {
            "generated": datetime.now().isoformat(),
            "batches": []
        }
        
        for batch_file in batch_files:
            if batch_file.suffix == '.json' and batch_file.name != "index.json":
                try:
                    with open(batch_file, 'r', encoding='utf-8') as f:
                        # Just read enough to get metadata if possible, but for standard JSON 
                        # we might have to load it all if it's one big object.
                        # For true 'lean' large files, we'd use a streaming parser, 
                        # but standard load is fine for typical batch sizes here.
                        batch_data = json.load(f)
                        index["batches"].append({
                            "file": batch_file.name,
                            "count": batch_data.get("count", 0),
                            "timestamp": batch_data.get("timestamp", "")
                        })
                except Exception as e:
                    logger.warning(f"Failed to index {batch_file}: {e}")
        
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2) # Index can be pretty-printed for human readability
            logger.info(f"Created index: {index_file}")
            return index_file
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise

json_exporter = JSONBatchExporter()