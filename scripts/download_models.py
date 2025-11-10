#!/usr/bin/env python3
"""
OPUS MAXIMUS - Model Download Script
====================================
Automated download of recommended models for theological generation.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List
import subprocess
import json


# ============================================================================
# RECOMMENDED MODELS
# ============================================================================

MODELS = {
    # Tier 1: Best Quality (70B+)
    'qwen2.5-72b-q5': {
        'name': 'Qwen 2.5 72B Instruct (Q5_K_M)',
        'repo': 'Qwen/Qwen2.5-72B-Instruct-GGUF',
        'file': 'qwen2.5-72b-instruct-q5_k_m.gguf',
        'size': '50GB',
        'vram': '48GB',
        'quality': 'Excellent',
        'recommended': True
    },
    'qwen2.5-72b-q4': {
        'name': 'Qwen 2.5 72B Instruct (Q4_K_M)',
        'repo': 'Qwen/Qwen2.5-72B-Instruct-GGUF',
        'file': 'qwen2.5-72b-instruct-q4_k_m.gguf',
        'size': '42GB',
        'vram': '40GB',
        'quality': 'Very Good'
    },
    'llama3.1-70b-q5': {
        'name': 'Llama 3.1 70B Instruct (Q5_K_M)',
        'repo': 'bartowski/Meta-Llama-3.1-70B-Instruct-GGUF',
        'file': 'Meta-Llama-3.1-70B-Instruct-Q5_K_M.gguf',
        'size': '48GB',
        'vram': '46GB',
        'quality': 'Excellent'
    },

    # Tier 2: Best Value (32B)
    'qwen2.5-32b-q5': {
        'name': 'Qwen 2.5 32B Instruct (Q5_K_M)',
        'repo': 'Qwen/Qwen2.5-32B-Instruct-GGUF',
        'file': 'qwen2.5-32b-instruct-q5_k_m.gguf',
        'size': '22GB',
        'vram': '24GB',
        'quality': 'Very Good',
        'recommended': True
    },
    'qwen2.5-32b-q6': {
        'name': 'Qwen 2.5 32B Instruct (Q6_K)',
        'repo': 'Qwen/Qwen2.5-32B-Instruct-GGUF',
        'file': 'qwen2.5-32b-instruct-q6_k.gguf',
        'size': '26GB',
        'vram': '28GB',
        'quality': 'Excellent'
    },

    # Tier 3: Budget (14B)
    'qwen2.5-14b-q5': {
        'name': 'Qwen 2.5 14B Instruct (Q5_K_M)',
        'repo': 'Qwen/Qwen2.5-14B-Instruct-GGUF',
        'file': 'qwen2.5-14b-instruct-q5_k_m.gguf',
        'size': '10GB',
        'vram': '12GB',
        'quality': 'Good'
    },

    # For vLLM (non-quantized)
    'qwen2.5-72b-hf': {
        'name': 'Qwen 2.5 72B Instruct (HF, for vLLM)',
        'repo': 'Qwen/Qwen2.5-72B-Instruct',
        'file': None,  # Whole repo
        'size': '144GB',
        'vram': '80GB+ (FP16) or 48GB+ (AWQ)',
        'quality': 'Excellent',
        'note': 'For vLLM with AWQ quantization'
    },
    'qwen2.5-32b-hf': {
        'name': 'Qwen 2.5 32B Instruct (HF, for vLLM)',
        'repo': 'Qwen/Qwen2.5-32B-Instruct',
        'file': None,
        'size': '64GB',
        'vram': '40GB+ (FP16) or 24GB+ (AWQ)',
        'quality': 'Very Good'
    }
}


# ============================================================================
# DOWNLOAD FUNCTIONS
# ============================================================================

def download_gguf_model(model_id: str, output_dir: Path) -> bool:
    """Download GGUF model using huggingface-cli"""

    model_info = MODELS[model_id]
    repo = model_info['repo']
    file = model_info['file']

    print(f"\n{'='*70}")
    print(f"Downloading: {model_info['name']}")
    print(f"Repository: {repo}")
    print(f"File: {file}")
    print(f"Size: {model_info['size']}")
    print(f"VRAM Required: {model_info['vram']}")
    print(f"Quality: {model_info['quality']}")
    print(f"{'='*70}\n")

    # Create model directory
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=True)

    # Download using huggingface-cli
    cmd = [
        'huggingface-cli',
        'download',
        repo,
        file,
        '--local-dir', str(model_dir),
        '--local-dir-use-symlinks', 'False'
    ]

    print(f"Running: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Download complete: {model_dir / file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Download failed: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ Error: huggingface-cli not found.")
        print("Install with: pip install huggingface_hub[cli]")
        return False


def download_hf_model(model_id: str, output_dir: Path) -> bool:
    """Download full HuggingFace model (for vLLM)"""

    model_info = MODELS[model_id]
    repo = model_info['repo']

    print(f"\n{'='*70}")
    print(f"Downloading: {model_info['name']}")
    print(f"Repository: {repo}")
    print(f"Size: {model_info['size']}")
    print(f"VRAM Required: {model_info['vram']}")
    print(f"Quality: {model_info['quality']}")
    if 'note' in model_info:
        print(f"Note: {model_info['note']}")
    print(f"{'='*70}\n")

    # Create model directory
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=True)

    # Download entire repository
    cmd = [
        'huggingface-cli',
        'download',
        repo,
        '--local-dir', str(model_dir),
        '--local-dir-use-symlinks', 'False'
    ]

    print(f"Running: {' '.join(cmd)}\n")
    print("⚠️  This will download the entire model (~144GB). It may take hours.")
    print("Press Ctrl+C within 10 seconds to cancel...\n")

    import time
    time.sleep(10)

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Download complete: {model_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Download failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        return False


def list_models():
    """List all available models"""
    print("\n" + "="*70)
    print("AVAILABLE MODELS FOR OPUS MAXIMUS")
    print("="*70 + "\n")

    print("TIER 1: BEST QUALITY (70B+) - Recommended for production\n")
    for model_id, info in MODELS.items():
        if '72b' in model_id or '70b' in model_id:
            recommended = " ⭐ RECOMMENDED" if info.get('recommended') else ""
            print(f"  {model_id:20s} {info['name']}{recommended}")
            print(f"  {'':20s} Size: {info['size']}, VRAM: {info['vram']}, Quality: {info['quality']}")
            print()

    print("\nTIER 2: BEST VALUE (32B) - Good quality, fits 24GB VRAM\n")
    for model_id, info in MODELS.items():
        if '32b' in model_id:
            recommended = " ⭐ RECOMMENDED" if info.get('recommended') else ""
            print(f"  {model_id:20s} {info['name']}{recommended}")
            print(f"  {'':20s} Size: {info['size']}, VRAM: {info['vram']}, Quality: {info['quality']}")
            print()

    print("\nTIER 3: BUDGET (14B) - Limited VRAM option\n")
    for model_id, info in MODELS.items():
        if '14b' in model_id:
            print(f"  {model_id:20s} {info['name']}")
            print(f"  {'':20s} Size: {info['size']}, VRAM: {info['vram']}, Quality: {info['quality']}")
            print()

    print("="*70 + "\n")


def check_disk_space(required_gb: float) -> bool:
    """Check if sufficient disk space available"""
    import shutil

    stat = shutil.disk_usage(Path.cwd())
    available_gb = stat.free / (1024**3)

    print(f"Disk space: {available_gb:.1f} GB available, {required_gb:.1f} GB required")

    if available_gb < required_gb:
        print(f"⚠️  WARNING: Insufficient disk space!")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Download models for Opus Maximus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available models
  python download_models.py --list

  # Download recommended 72B model (Q5, best quality)
  python download_models.py --model qwen2.5-72b-q5

  # Download 32B model (fits 24GB VRAM)
  python download_models.py --model qwen2.5-32b-q5

  # Download for vLLM (non-quantized)
  python download_models.py --model qwen2.5-72b-hf

  # Download multiple models
  python download_models.py --model qwen2.5-72b-q5 --model qwen2.5-32b-q5

  # Custom output directory
  python download_models.py --model qwen2.5-72b-q5 --output /path/to/models
        """
    )

    parser.add_argument(
        '--model',
        action='append',
        choices=list(MODELS.keys()),
        help='Model to download (can be specified multiple times)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available models'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('models'),
        help='Output directory for models (default: models/)'
    )

    parser.add_argument(
        '--recommended',
        action='store_true',
        help='Download all recommended models'
    )

    args = parser.parse_args()

    # List models
    if args.list:
        list_models()
        return

    # Check if model specified
    if not args.model and not args.recommended:
        parser.print_help()
        print("\n✗ Error: Please specify --model or --list")
        sys.exit(1)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {args.output.absolute()}")

    # Get models to download
    if args.recommended:
        models_to_download = [
            model_id for model_id, info in MODELS.items()
            if info.get('recommended')
        ]
        print(f"\nDownloading {len(models_to_download)} recommended models...")
    else:
        models_to_download = args.model

    # Download each model
    success = 0
    failed = 0

    for model_id in models_to_download:
        # Check disk space
        model_info = MODELS[model_id]
        size_str = model_info['size']
        size_gb = float(size_str.replace('GB', ''))

        if not check_disk_space(size_gb + 10):  # +10GB buffer
            print(f"Skipping {model_id} due to insufficient disk space\n")
            failed += 1
            continue

        # Download
        if model_info['file'] is None:
            # Full HF repo
            result = download_hf_model(model_id, args.output)
        else:
            # GGUF file
            result = download_gguf_model(model_id, args.output)

        if result:
            success += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Successful: {success}")
    print(f"Failed: {failed}")
    print(f"Output directory: {args.output.absolute()}")
    print("="*70 + "\n")

    if success > 0:
        print("✓ Models ready! Update Opus/config/config.yaml to use them.")
        print("\nExample config.yaml:")
        print("  model:")
        print(f"    path: \"{args.output}/{models_to_download[0]}/{MODELS[models_to_download[0]]['file']}\"")
        print("    backend: \"llamacpp\"  # or vllm for non-GGUF")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
