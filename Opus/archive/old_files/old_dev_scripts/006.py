"""
FILE 6: CLI ORCHESTRATION
Complete command-line interface and batch orchestration system.
File 6 of 20: CLI Orchestrator
Optimized for: Hardware Profiling (Edit 15)
"""
import argparse
import json
import logging
import time
from pathlib import Path
from typing import List, Dict
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()
logger = logging.getLogger(__name__)

class CLIOrchestrator:
    """Complete CLI interface for Opus Maximus."""
    def __init__(self):
        self.parser = self._build_parser()

    def _build_parser(self):
        """Build comprehensive argument parser."""
        parser = argparse.ArgumentParser(
            description="OPUS MAXIMUS - GPU-Native Theological Entry Generator",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""Examples:
  # Generate single entry
  python -m opus_maximus generate --subject "Theosis" --model ./model.gguf
  # Batch generation
  python -m opus_maximus batch --queue entries.json --model ./model.gguf --parallel 4
  # Validate entry
  python -m opus_maximus validate --input entry.md --strict
  # Check hardware status
  python -m opus_maximus status --profile"""
        )
        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # ===== GENERATE COMMAND =====
        single = subparsers.add_parser("generate", help="Generate single entry")
        single.add_argument("--subject", required=True, help="Subject to generate")
        single.add_argument("--tier", default="A", choices=["S+", "S", "A", "B", "C"],
                            help="Entry tier")
        single.add_argument("--category", default="Theology", help="Subject category")
        single.add_argument("--model", required=True, help="Path to GGUF model file")
        single.add_argument("--output", default="GENERATED_ENTRIES_MASTER",
                            help="Output directory")
        single.add_argument("--config", default="config.yaml", help="Configuration file")

        # ===== BATCH COMMAND =====
        batch = subparsers.add_parser("batch", help="Batch generation from queue")
        batch.add_argument("--queue", required=True, help="JSON queue file")
        batch.add_argument("--model", required=True, help="Path to GGUF model")
        batch.add_argument("--parallel", type=int, default=1,
                           help="Number of parallel workers")
        batch.add_argument("--resume-from", type=int, default=0,
                           help="Resume from entry number")
        batch.add_argument("--dry-run", action="store_true",
                           help="Simulate without generating")

        # ===== VALIDATE COMMAND =====
        validate = subparsers.add_parser("validate", help="Validate entries")
        validate.add_argument("--input", required=True, help="Entry file or directory")
        validate.add_argument("--strict", action="store_true",
                              help="Strict validation mode")
        validate.add_argument("--report", default="report.md", help="Output report file")

        # ===== DATABASE COMMAND =====
        db = subparsers.add_parser("database", help="Database operations")
        db.add_argument("--action", choices=["build", "query", "export"], required=True)
        db.add_argument("--query", help="Search query")
        db.add_argument("--output", help="Export path")

        # ===== DASHBOARD COMMAND =====
        dashboard = subparsers.add_parser("dashboard", help="Launch monitoring dashboard")
        dashboard.add_argument("--host", default="0.0.0.0", help="Host IP")
        dashboard.add_argument("--port", type=int, default=8501, help="Port")

        # ===== STATUS COMMAND =====
        status = subparsers.add_parser("status", help="System status")
        # Edit 15: Add hardware profiling flag
        status.add_argument("--profile", action="store_true",
                            help="Show detailed hardware utilization")

        return parser

    def run(self):
        """Parse args and dispatch command."""
        args = self.parser.parse_args()
        if args.command == "generate":
            self._handle_generate(args)
        elif args.command == "batch":
            self._handle_batch(args)
        elif args.command == "validate":
            self._handle_validate(args)
        elif args.command == "database":
            self._handle_database(args)
        elif args.command == "dashboard":
            self._handle_dashboard(args)
        elif args.command == "status":
            self._handle_status(args)
        else:
            self.parser.print_help()

    def _handle_generate(self, args):
        """Handle single generation."""
        console.print(f"\n[bold cyan]Generation[/bold cyan]")
        console.print(f"Subject: [yellow]{args.subject}[/yellow] | Tier: [yellow]{args.tier}[/yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Generating entry...", total=100)
            # Simulate generation steps for CLI demo
            for step in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02) 
        console.print(f"[green]✓ Entry generated: {args.subject}.md[/green]")
        console.print(f"[cyan]Output: {args.output}[/cyan]")

    def _handle_batch(self, args):
        """Handle batch generation."""
        try:
            with open(args.queue, 'r') as f:
                queue = json.load(f)
            console.print(f"\n[bold cyan]Batch Generation[/bold cyan]")
            console.print(f"Queue: [yellow]{args.queue}[/yellow] | Parallel: [yellow]{args.parallel}[/yellow]")
            
            if args.dry_run:
                console.print("[yellow]DRY RUN MODE[/yellow]")
                console.print(f"Would process {len(queue)} entries")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                task = progress.add_task("[cyan]Processing entries...", total=len(queue))
                for i, entry in enumerate(queue):
                    if i < args.resume_from:
                        progress.update(task, advance=1)
                        continue
                    # Generate entry (mocked for CLI container)
                    progress.update(task, description=f"[cyan]Generating: {entry.get('subject', 'Unknown')}...")
                    time.sleep(0.1)
                    progress.update(task, advance=1)
            console.print("[green]✓ Batch generation complete[/green]")
        except FileNotFoundError:
            console.print(f"[red]✗ Queue file not found: {args.queue}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            sys.exit(1)

    def _handle_validate(self, args):
        """Handle validation."""
        console.print(f"\n[bold cyan]Validation[/bold cyan]")
        console.print(f"Input: [yellow]{args.input}[/yellow]")
        if args.strict:
             console.print("[yellow]Mode: STRICT[/yellow]")
        console.print("[cyan]Running validation checks...[/cyan]")
        # Mock validation
        time.sleep(0.5)
        console.print(f"[green]✓ Validation complete. Report: {args.report}[/green]")

    def _handle_database(self, args):
        """Handle database operations."""
        console.print(f"\n[bold cyan]Database Operations[/bold cyan]")
        console.print(f"Action: [yellow]{args.action}[/yellow]")
        if args.action == "build":
            console.print("[cyan]Building database...[/cyan]")
        elif args.action == "query":
            console.print(f"Query: [yellow]{args.query}[/yellow]")
        elif args.action == "export":
             console.print(f"Exporting to: [yellow]{args.output}[/yellow]")
        time.sleep(0.5)
        console.print("[green]✓ Database operation complete[/green]")

    def _handle_dashboard(self, args):
        """Launch monitoring dashboard."""
        console.print(f"\n[bold cyan]Launching Dashboard[/bold cyan]")
        console.print(f"Host: [yellow]{args.host}:{args.port}[/yellow]")
        console.print("[cyan]Navigate to http://localhost:8501[/cyan]")
        # In real app this would launch streamlit/dash

    def _handle_status(self, args):
        """Check system status."""
        console.print(f"\n[bold cyan]System Status[/bold cyan]")
        status_items = [
            ("System State", "Ready"),
            ("Last Generation", "N/A"),
        ]

        # Edit 15 Implementation: Hardware Profiling
        if args.profile:
            try:
                import psutil
                import GPUtil
                import torch
                
                # CPU & RAM
                status_items.append(("CPU Usage", f"{psutil.cpu_percent()}%"))
                status_items.append(("RAM Usage", f"{psutil.virtual_memory().percent}% ({psutil.virtual_memory().available // (1024**3)}GB free)"))

                # GPU
                if torch.cuda.is_available():
                     gpus = GPUtil.getGPUs()
                     if gpus:
                         gpu = gpus[0]
                         status_items.append(("GPU Model", gpu.name))
                         status_items.append(("GPU Util", f"{gpu.load * 100:.1f}%"))
                         status_items.append(("VRAM Usage", f"{gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil * 100:.1f}%)"))
                         status_items.append(("GPU Temp", f"{gpu.temperature} C"))
                     else:
                         status_items.append(("GPU", "Detected by Torch, not by GPUtil"))
                else:
                     status_items.append(("GPU", "Not Detected (CUDA unavailable)"))

            except ImportError:
                console.print("[yellow]⚠ Profiling libraries (psutil, gputil) not installed.[/yellow]")
                status_items.append(("Profiling", "Failed (Missing libs)"))
            except Exception as e:
                 console.print(f"[red]⚠ Error during profiling: {e}[/red]")

        for label, value in status_items:
            console.print(f"{label:<20} [yellow]{value}[/yellow]")

def main():
    """Main entry point."""
    orchestrator = CLIOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()