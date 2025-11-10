#!/usr/bin/env python3
"""
OPUS MAXIMUS - Model Benchmarking Tool
======================================
Benchmark different models and backends for theological generation.
"""

import sys
import time
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Opus.src.llm_interface import create_llm
from Opus.src.llm_backends_advanced import create_advanced_llm, list_available_backends


# ============================================================================
# TEST PROMPTS
# ============================================================================

TEST_PROMPTS = {
    'short': "What is theosis in Orthodox theology?",

    'medium': """Explain the concept of theosis in Orthodox theology, including:
- Biblical foundations
- Patristic development
- Distinction from Western soteriology
- Practical spiritual implications

Write 300-500 words.""",

    'long': """You are a world-class Orthodox theologian. Write a sophisticated theological analysis of theosis (deification) that includes:

1. Biblical Foundations (Genesis 1:26-27, 2 Peter 1:4, Psalm 82:6, John 10:34-36)
2. Patristic Development (Saint Athanasius, Saint Maximus the Confessor, Saint Gregory Palamas)
3. The essence-energies distinction
4. Contrast with Western forensic justification
5. Practical ascetical implications
6. Liturgical expressions

Requirements:
- Use sophisticated theological vocabulary
- Include at least 5 patristic citations
- Include at least 8 biblical references
- Average word length ≥ 5.2 characters
- Formal, scholarly tone (no contractions)
- 800-1200 words

Write the analysis now."""
}


# ============================================================================
# BENCHMARK RESULT
# ============================================================================

@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    backend: str
    model: str
    prompt_type: str
    prompt_length: int
    output_length: int
    time_seconds: float
    tokens_per_second: float
    first_token_latency: float
    timestamp: str
    config: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# BENCHMARKING
# ============================================================================

def benchmark_single(
    llm,
    prompt: str,
    prompt_type: str,
    config: Dict[str, Any],
    iterations: int = 3
) -> List[BenchmarkResult]:
    """Benchmark a single prompt with multiple iterations"""

    results = []

    print(f"\n{'='*70}")
    print(f"Benchmarking: {prompt_type.upper()} prompt")
    print(f"Iterations: {iterations}")
    print(f"{'='*70}\n")

    for i in range(iterations):
        print(f"Run {i+1}/{iterations}...", end=' ', flush=True)

        start = time.time()

        # Generate
        output = llm.generate(
            prompt=prompt,
            max_tokens=2048,
            temperature=0.7
        )

        elapsed = time.time() - start

        # Estimate tokens (rough)
        output_tokens = llm.count_tokens(output)
        prompt_tokens = llm.count_tokens(prompt)

        tokens_per_sec = output_tokens / elapsed if elapsed > 0 else 0

        print(f"{elapsed:.2f}s ({tokens_per_sec:.1f} tok/s)")

        result = BenchmarkResult(
            backend=llm.__class__.__name__,
            model=config.get('model', config.get('path', 'unknown')),
            prompt_type=prompt_type,
            prompt_length=prompt_tokens,
            output_length=output_tokens,
            time_seconds=elapsed,
            tokens_per_second=tokens_per_sec,
            first_token_latency=0.0,  # Would need streaming to measure
            timestamp=datetime.now().isoformat(),
            config=config
        )

        results.append(result)

    # Print summary
    avg_time = sum(r.time_seconds for r in results) / len(results)
    avg_tps = sum(r.tokens_per_second for r in results) / len(results)

    print(f"\n  Average: {avg_time:.2f}s ({avg_tps:.1f} tok/s)")

    return results


def benchmark_suite(
    config: Dict[str, Any],
    prompt_types: List[str] = ['short', 'medium', 'long'],
    iterations: int = 3
) -> List[BenchmarkResult]:
    """Run complete benchmark suite"""

    print("\n" + "="*70)
    print("OPUS MAXIMUS - MODEL BENCHMARK")
    print("="*70)
    print(f"Backend: {config.get('backend', 'llamacpp')}")
    print(f"Model: {config.get('model', config.get('path'))}")
    print(f"Prompt types: {', '.join(prompt_types)}")
    print(f"Iterations per prompt: {iterations}")
    print("="*70)

    # Create LLM
    print("\nInitializing model... (this may take a few minutes for large models)")
    start_init = time.time()

    if config.get('backend') in ['vllm', 'exllamav2', 'sglang']:
        llm = create_advanced_llm(config)
    else:
        llm = create_llm(config)

    init_time = time.time() - start_init
    print(f"✓ Model loaded in {init_time:.1f}s")

    # Run benchmarks
    all_results = []

    for prompt_type in prompt_types:
        if prompt_type not in TEST_PROMPTS:
            print(f"Warning: Unknown prompt type '{prompt_type}', skipping")
            continue

        prompt = TEST_PROMPTS[prompt_type]
        results = benchmark_single(llm, prompt, prompt_type, config, iterations)
        all_results.extend(results)

    return all_results


def save_results(results: List[BenchmarkResult], output_file: Path):
    """Save benchmark results to JSON"""

    data = {
        'benchmark_date': datetime.now().isoformat(),
        'total_runs': len(results),
        'results': [r.to_dict() for r in results]
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def print_summary(results: List[BenchmarkResult]):
    """Print benchmark summary"""

    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70 + "\n")

    # Group by prompt type
    by_type = {}
    for result in results:
        if result.prompt_type not in by_type:
            by_type[result.prompt_type] = []
        by_type[result.prompt_type].append(result)

    # Print table
    print(f"{'Prompt Type':<15} {'Avg Time':<12} {'Avg Tokens/sec':<15} {'Runs'}")
    print("-" * 70)

    for prompt_type, prompt_results in sorted(by_type.items()):
        avg_time = sum(r.time_seconds for r in prompt_results) / len(prompt_results)
        avg_tps = sum(r.tokens_per_second for r in prompt_results) / len(prompt_results)

        print(f"{prompt_type:<15} {avg_time:>10.2f}s  {avg_tps:>13.1f}  {len(prompt_results):>7}")

    print("\n" + "="*70 + "\n")

    # Overall stats
    total_time = sum(r.time_seconds for r in results)
    total_tokens = sum(r.output_length for r in results)
    overall_tps = total_tokens / total_time if total_time > 0 else 0

    print(f"Total time: {total_time:.1f}s")
    print(f"Total tokens: {total_tokens}")
    print(f"Overall throughput: {overall_tps:.1f} tokens/sec")
    print()


def compare_backends(
    configs: List[Dict[str, Any]],
    prompt_type: str = 'medium',
    iterations: int = 3
):
    """Compare multiple backends/models"""

    print("\n" + "="*70)
    print("OPUS MAXIMUS - BACKEND COMPARISON")
    print("="*70 + "\n")

    all_results = []

    for i, config in enumerate(configs):
        print(f"\n[{i+1}/{len(configs)}] Testing: {config['backend']} - {config.get('model', config.get('path'))}")

        try:
            results = benchmark_suite(config, [prompt_type], iterations)
            all_results.extend(results)
        except Exception as e:
            print(f"✗ Failed: {e}")
            continue

    # Print comparison
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70 + "\n")

    print(f"{'Backend':<20} {'Model':<30} {'Avg Time':<12} {'Tokens/sec'}")
    print("-" * 70)

    # Group by backend
    by_backend = {}
    for result in all_results:
        key = f"{result.backend}:{result.model}"
        if key not in by_backend:
            by_backend[key] = []
        by_backend[key].append(result)

    for key, backend_results in sorted(by_backend.items()):
        backend, model = key.split(':', 1)
        avg_time = sum(r.time_seconds for r in backend_results) / len(backend_results)
        avg_tps = sum(r.tokens_per_second for r in backend_results) / len(backend_results)

        # Truncate model name if too long
        model_short = model[:27] + "..." if len(model) > 30 else model

        print(f"{backend:<20} {model_short:<30} {avg_time:>10.2f}s  {avg_tps:>10.1f}")

    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Opus Maximus models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Benchmark default llama.cpp backend
  python benchmark_models.py --model models/qwen2.5-72b/model.gguf

  # Benchmark vLLM
  python benchmark_models.py --backend vllm --model Qwen/Qwen2.5-72B-Instruct

  # Quick test (short prompt only, 1 iteration)
  python benchmark_models.py --quick

  # Compare backends
  python benchmark_models.py --compare --backends vllm llamacpp
        """
    )

    parser.add_argument(
        '--backend',
        default='llamacpp',
        choices=['llamacpp', 'vllm', 'exllamav2', 'sglang'],
        help='LLM backend to use'
    )

    parser.add_argument(
        '--model',
        help='Model path or HuggingFace repo'
    )

    parser.add_argument(
        '--prompts',
        nargs='+',
        default=['short', 'medium', 'long'],
        choices=['short', 'medium', 'long'],
        help='Prompt types to test'
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=3,
        help='Iterations per prompt'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('benchmark_results.json'),
        help='Output file for results'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test (short prompt, 1 iteration)'
    )

    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare multiple backends'
    )

    args = parser.parse_args()

    # Quick mode
    if args.quick:
        args.prompts = ['short']
        args.iterations = 1

    # Build config
    config = {
        'backend': args.backend,
        'model': args.model or 'models/model.gguf',
        'path': args.model or 'models/model.gguf',
        'n_ctx': 32768,
        'n_gpu_layers': -1,
        'gpu_memory_utilization': 0.95
    }

    # Check model exists for llamacpp
    if args.backend == 'llamacpp':
        model_path = Path(config['model'])
        if not model_path.exists():
            print(f"Error: Model file not found: {model_path}")
            print("\nAvailable models:")
            models_dir = Path('models')
            if models_dir.exists():
                for gguf in models_dir.rglob('*.gguf'):
                    print(f"  {gguf}")
            sys.exit(1)

    # Run benchmark
    results = benchmark_suite(config, args.prompts, args.iterations)

    # Print summary
    print_summary(results)

    # Save results
    save_results(results, args.output)

    print(f"\n✓ Benchmark complete!")


if __name__ == '__main__':
    main()
