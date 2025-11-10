"""
FILE 23: OUTPUT MANAGER (LEAN)
=============================
Unified output orchestration. Routes entries to appropriate output format
with zero overhead. Only what's needed.
File 13 of 20: Output Manager
Optimized for: Unified lean export orchestration
"""
import logging
from typing import Dict, Optional, List
from pathlib import Path
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OutputFormat(Enum):
    """Output formats."""
    MARKDOWN = "markdown"
    JSON = "json"
    BOTH = "both"

class OutputManager:
    """Lean output orchestration."""
    def __init__(self, base_dir: Path = Path("GENERATED_ENTRIES_MASTER")):
        self.base_dir = Path(base_dir)
        self.markdown_dir = self.base_dir / "markdown"
        self.json_dir = self.base_dir / "json"
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.export_log: List[Dict] = []

    def export_entry(self, entry_id: str, content: str, format: OutputFormat = OutputFormat.BOTH,
                     metadata: Dict = None) -> Dict:
        """Export single entry. Returns paths dict."""
        results = {"entry_id": entry_id, "paths": {}}
        try:
            if format in [OutputFormat.MARKDOWN, OutputFormat.BOTH]:
                md_path = self._save_markdown(entry_id, content, metadata)
                results["paths"]["markdown"] = str(md_path)
            
            if format in [OutputFormat.JSON, OutputFormat.BOTH]:
                json_path = self._save_json(entry_id, content, metadata)
                results["paths"]["json"] = str(json_path)
                
            results["success"] = True
            self.export_log.append({"entry_id": entry_id, "format": format.value, "success": True})
            logger.info(f"Exported {entry_id}: {format.value}")
            
        except Exception as e:
            logger.error(f"Failed to export {entry_id}: {e}")
            results["success"] = False
            results["error"] = str(e)
            self.export_log.append({"entry_id": entry_id, "format": format.value, "success": False})
            
        return results

    def export_batch(self, entries: Dict[str, str], format: OutputFormat = OutputFormat.BOTH,
                     metadata: Dict = None) -> Dict:
        """Export batch of entries. Returns summary."""
        summary = {
            "total": len(entries),
            "successful": 0,
            "failed": 0,
            "format": format.value,
            "timestamp": datetime.now().isoformat()
        }
        
        for entry_id, content in entries.items():
            result = self.export_entry(entry_id, content, format, metadata)
            if result["success"]:
                summary["successful"] += 1
            else:
                summary["failed"] += 1
                
        logger.info(f"Batch export complete: {summary['successful']}/{summary['total']} successful")
        return summary

    def _save_markdown(self, entry_id: str, content: str, metadata: Dict = None) -> Path:
        """Save markdown file."""
        filepath = self.markdown_dir / f"{entry_id}.md"
        output = ""
        if metadata:
            output += "---\n"
            for key, value in metadata.items():
                 # Basic YAML escaping could be added here if needed
                if key not in ["content"]:
                    output += f"{key}: {value}\n"
            output += "---\n\n"
        output += content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output)
        return filepath

    def _save_json(self, entry_id: str, content: str, metadata: Dict = None) -> Path:
        """Save JSON file."""
        filepath = self.json_dir / f"{entry_id}.json"
        data = {
            "id": entry_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            data.update(metadata)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def get_export_statistics(self) -> Dict:
        """Get export statistics."""
        if not self.export_log:
            return {"total_exports": 0}
        
        successful = len([e for e in self.export_log if e["success"]])
        total = len(self.export_log)
        
        return {
            "total_exports": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0
        }

    def cleanup_old_exports(self, days_old: int = 30) -> int:
        """Remove exports older than N days. Returns count."""
        from datetime import timedelta
        import time
        
        cutoff = time.time() - (days_old * 86400)
        count = 0
        
        for directory in [self.markdown_dir, self.json_dir]:
            if directory.exists():
                for file in directory.glob("*"):
                    if file.is_file():
                        if file.stat().st_mtime < cutoff:
                            try:
                                file.unlink()
                                count += 1
                            except Exception as e:
                                logger.warning(f"Failed to delete {file}: {e}")
                                
        if count > 0:
            logger.info(f"Cleaned up {count} old exports")
        return count

output_manager = OutputManager()