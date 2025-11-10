"""
OPUS MAXIMUS - Advanced LLM Backends
====================================
Production-grade backends: vLLM, ExLlamaV2, SGLang

These are the BEST inference engines for local LLM generation.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC

from .llm_interface import BaseLLM
from .error_handling import (
    LLMError,
    ConfigurationError,
    retry_with_backoff,
    ErrorContext
)

logger = logging.getLogger(__name__)


# ============================================================================
# vLLM BACKEND (Fastest - Production)
# ============================================================================

class vLLMBackend(BaseLLM):
    """
    vLLM backend - Fastest inference with PagedAttention.

    Features:
    - 3-5x faster than llama.cpp
    - Continuous batching
    - PagedAttention (efficient memory)
    - Multi-GPU support (tensor parallelism)

    Best for: Production batch generation

    Requirements:
    - CUDA GPU with 16GB+ VRAM
    - pip install vllm
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vLLM backend.

        Args:
            config: Configuration with:
                - model: Model name (HF) or path
                - gpu_memory_utilization: GPU memory to use (0.0-1.0)
                - max_model_len: Maximum sequence length
                - tensor_parallel_size: Number of GPUs
                - quantization: Quantization method (awq, gptq)
        """
        self.config = config
        self.model_name = config.get('model', config.get('path'))

        logger.info(f"Initializing vLLM backend: {self.model_name}")

        try:
            from vllm import LLM, SamplingParams
            self.SamplingParams = SamplingParams

            # Initialize vLLM
            logger.info("Loading model... (this may take 2-5 minutes for large models)")

            self.llm = LLM(
                model=self.model_name,
                gpu_memory_utilization=config.get('gpu_memory_utilization', 0.95),
                max_model_len=config.get('max_model_len', 32768),
                tensor_parallel_size=config.get('tensor_parallel_size', 1),
                dtype=config.get('dtype', 'auto'),
                quantization=config.get('quantization'),
                trust_remote_code=config.get('trust_remote_code', True),
                max_num_seqs=config.get('max_num_seqs', 32),
                max_num_batched_tokens=config.get('max_num_batched_tokens', 8192)
            )

            logger.info("vLLM model loaded successfully")

            # Test generation
            test_output = self.llm.generate(
                ["Test"],
                self.SamplingParams(max_tokens=1)
            )
            logger.debug(f"Test generation successful: {test_output}")

        except ImportError as e:
            raise ConfigurationError(
                "vLLM not installed. Install with: pip install vllm"
            ) from e

        except Exception as e:
            raise LLMError(f"Failed to initialize vLLM: {e}") from e

    @retry_with_backoff(max_retries=3, exceptions=(RuntimeError,))
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        stop: Optional[List[str]] = None
    ) -> str:
        """Generate text using vLLM"""

        with ErrorContext("vLLM generation", prompt_length=len(prompt)):
            try:
                sampling_params = self.SamplingParams(
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_tokens=max_tokens,
                    repetition_penalty=repeat_penalty,
                    stop=stop
                )

                outputs = self.llm.generate([prompt], sampling_params)

                if not outputs or not outputs[0].outputs:
                    raise LLMError("vLLM returned empty output")

                generated_text = outputs[0].outputs[0].text

                if not generated_text:
                    raise LLMError("vLLM generated empty text")

                logger.debug(f"Generated {len(generated_text)} characters with vLLM")
                return generated_text.strip()

            except Exception as e:
                logger.error(f"vLLM generation error: {e}")
                raise LLMError(f"vLLM generation failed: {e}") from e

    def get_embeddings(self, text: str) -> List[float]:
        """vLLM doesn't support embeddings - use sentence-transformers"""
        raise NotImplementedError(
            "vLLM doesn't support embeddings. "
            "Use sentence-transformers for embeddings."
        )

    def count_tokens(self, text: str) -> int:
        """Estimate token count"""
        # vLLM uses transformers tokenizer
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            return len(tokenizer.encode(text))
        except Exception:
            # Fallback estimate
            return len(text) // 4


# ============================================================================
# ExLlamaV2 BACKEND (Best for Limited VRAM)
# ============================================================================

class ExLlamaV2Backend(BaseLLM):
    """
    ExLlamaV2 backend - Optimized for large models on limited VRAM.

    Features:
    - EXL2 quantization (2-8 bits)
    - Very memory efficient
    - Fast generation speed
    - Dynamic quantization

    Best for: Large models (70B+) on 16-24GB VRAM

    Requirements:
    - CUDA GPU
    - pip install exllamav2
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ExLlamaV2 backend.

        Args:
            config: Configuration with:
                - model_path: Path to EXL2 model directory
                - max_seq_len: Maximum sequence length
                - cache_8bit: Use 8-bit cache
        """
        self.config = config
        model_path = Path(config.get('model_path', config.get('path')))

        logger.info(f"Initializing ExLlamaV2 backend: {model_path}")

        try:
            from exllamav2 import (
                ExLlamaV2,
                ExLlamaV2Config,
                ExLlamaV2Cache,
                ExLlamaV2Tokenizer
            )
            from exllamav2.generator import ExLlamaV2BaseGenerator

            # Load config
            config_obj = ExLlamaV2Config()
            config_obj.model_dir = str(model_path)
            config_obj.prepare()

            config_obj.max_seq_len = config.get('max_seq_len', 32768)

            # Load model
            logger.info("Loading model...")
            model = ExLlamaV2(config_obj)

            logger.info("Loading tokenizer...")
            tokenizer = ExLlamaV2Tokenizer(config_obj)

            # Create cache
            cache_8bit = config.get('cache_8bit', True)
            cache = ExLlamaV2Cache(model, lazy=True, max_seq_len=config_obj.max_seq_len)

            # Create generator
            self.generator = ExLlamaV2BaseGenerator(model, cache, tokenizer)

            self.model = model
            self.tokenizer = tokenizer
            self.cache = cache

            logger.info("ExLlamaV2 loaded successfully")

        except ImportError as e:
            raise ConfigurationError(
                "ExLlamaV2 not installed. Install with: pip install exllamav2"
            ) from e

        except Exception as e:
            raise LLMError(f"Failed to initialize ExLlamaV2: {e}") from e

    @retry_with_backoff(max_retries=3)
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        stop: Optional[List[str]] = None
    ) -> str:
        """Generate text using ExLlamaV2"""

        with ErrorContext("ExLlamaV2 generation"):
            try:
                from exllamav2.generator import ExLlamaV2Sampler

                # Set generation settings
                settings = ExLlamaV2Sampler.Settings()
                settings.temperature = temperature
                settings.top_p = top_p
                settings.top_k = top_k
                settings.token_repetition_penalty = repeat_penalty

                # Generate
                output = self.generator.generate_simple(
                    prompt,
                    settings,
                    max_tokens,
                    seed=None,
                    stop_conditions=stop or []
                )

                if not output:
                    raise LLMError("ExLlamaV2 generated empty output")

                logger.debug(f"Generated {len(output)} characters with ExLlamaV2")
                return output.strip()

            except Exception as e:
                logger.error(f"ExLlamaV2 generation error: {e}")
                raise LLMError(f"ExLlamaV2 generation failed: {e}") from e

    def get_embeddings(self, text: str) -> List[float]:
        """Not supported"""
        raise NotImplementedError("ExLlamaV2 doesn't support embeddings")

    def count_tokens(self, text: str) -> int:
        """Count tokens using model tokenizer"""
        try:
            tokens = self.tokenizer.encode(text)
            return len(tokens[0])  # ExLlamaV2 returns tuple
        except Exception:
            return len(text) // 4


# ============================================================================
# SGLang BACKEND (Structured Generation)
# ============================================================================

class SGLangBackend(BaseLLM):
    """
    SGLang backend - Structured generation with constraints.

    Features:
    - Constrained decoding (regex, JSON schema)
    - vLLM-based (fast)
    - Grammar-based generation
    - Built-in caching

    Best for: Structured output (citations, sections)

    Requirements:
    - CUDA GPU
    - pip install "sglang[all]"
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SGLang backend.

        Args:
            config: Configuration with model path/name
        """
        self.config = config
        self.model_name = config.get('model', config.get('path'))

        logger.info(f"Initializing SGLang backend: {self.model_name}")

        try:
            import sglang as sgl

            # Initialize runtime
            logger.info("Starting SGLang runtime...")

            self.runtime = sgl.Runtime(
                model_path=self.model_name,
                port=config.get('port', 30000),
                mem_fraction_static=config.get('gpu_memory_utilization', 0.95)
            )

            sgl.set_default_backend(self.runtime)

            self.sgl = sgl

            logger.info("SGLang ready")

        except ImportError as e:
            raise ConfigurationError(
                "SGLang not installed. Install with: pip install 'sglang[all]'"
            ) from e

        except Exception as e:
            raise LLMError(f"Failed to initialize SGLang: {e}") from e

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        stop: Optional[List[str]] = None
    ) -> str:
        """Generate with SGLang"""

        @self.sgl.function
        def generate_text(s, user_prompt):
            s += user_prompt
            s += self.sgl.gen(
                "response",
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop
            )

        try:
            state = generate_text.run(user_prompt=prompt)
            return state["response"].strip()

        except Exception as e:
            raise LLMError(f"SGLang generation failed: {e}") from e

    def generate_with_regex(
        self,
        prompt: str,
        regex: str,
        max_tokens: int = 2048
    ) -> str:
        """Generate text matching regex pattern"""

        @self.sgl.function
        def constrained_gen(s, user_prompt, pattern):
            s += user_prompt
            s += self.sgl.gen(
                "response",
                max_tokens=max_tokens,
                regex=pattern
            )

        try:
            state = constrained_gen.run(user_prompt=prompt, pattern=regex)
            return state["response"].strip()

        except Exception as e:
            raise LLMError(f"SGLang constrained generation failed: {e}") from e

    def get_embeddings(self, text: str) -> List[float]:
        """Not supported"""
        raise NotImplementedError("SGLang doesn't support embeddings")

    def count_tokens(self, text: str) -> int:
        """Estimate tokens"""
        return len(text) // 4

    def __del__(self):
        """Shutdown runtime"""
        if hasattr(self, 'runtime'):
            self.runtime.shutdown()


# ============================================================================
# BACKEND FACTORY (Enhanced)
# ============================================================================

def create_advanced_llm(config: Dict[str, Any]) -> BaseLLM:
    """
    Factory function to create advanced LLM backends.

    Args:
        config: Configuration with 'backend' key

    Returns:
        Initialized LLM backend

    Supported backends:
    - vllm: vLLM (fastest, production)
    - exllamav2: ExLlamaV2 (VRAM efficient)
    - sglang: SGLang (structured generation)
    - llamacpp: llama.cpp (fallback)
    - api: OpenAI-compatible API

    Example:
        config = {
            'backend': 'vllm',
            'model': 'Qwen/Qwen2.5-72B-Instruct',
            'gpu_memory_utilization': 0.95
        }
        llm = create_advanced_llm(config)
    """
    backend = config.get('backend', 'llamacpp').lower()

    logger.info(f"Creating LLM backend: {backend}")

    if backend == 'vllm':
        return vLLMBackend(config)

    elif backend == 'exllamav2' or backend == 'exllama':
        return ExLlamaV2Backend(config)

    elif backend == 'sglang':
        return SGLangBackend(config)

    elif backend == 'llamacpp' or backend == 'llama.cpp':
        from .llm_interface import LocalLLM
        return LocalLLM(config)

    elif backend == 'api':
        from .llm_interface import APILLM
        return APILLM(config)

    else:
        raise ConfigurationError(
            f"Unknown backend: {backend}. "
            f"Supported: vllm, exllamav2, sglang, llamacpp, api"
        )


# ============================================================================
# UTILITIES
# ============================================================================

def benchmark_backend(llm: BaseLLM, prompt: str, iterations: int = 5) -> Dict[str, float]:
    """
    Benchmark LLM backend.

    Args:
        llm: LLM backend to test
        prompt: Test prompt
        iterations: Number of runs

    Returns:
        Statistics dictionary
    """
    import time

    logger.info(f"Benchmarking {llm.__class__.__name__}...")

    times = []
    tokens = []

    for i in range(iterations):
        start = time.time()

        output = llm.generate(prompt, max_tokens=200)

        elapsed = time.time() - start
        times.append(elapsed)

        token_count = llm.count_tokens(output)
        tokens.append(token_count)

        logger.info(f"Run {i+1}/{iterations}: {elapsed:.2f}s, {token_count} tokens")

    avg_time = sum(times) / len(times)
    avg_tokens = sum(tokens) / len(tokens)
    tokens_per_sec = avg_tokens / avg_time

    stats = {
        'backend': llm.__class__.__name__,
        'iterations': iterations,
        'avg_time_seconds': avg_time,
        'avg_tokens': avg_tokens,
        'tokens_per_second': tokens_per_sec,
        'min_time': min(times),
        'max_time': max(times)
    }

    logger.info(
        f"Benchmark complete: {tokens_per_sec:.2f} tokens/sec "
        f"({avg_time:.2f}s avg)"
    )

    return stats


def list_available_backends() -> List[str]:
    """List all installed backends"""
    backends = ['llamacpp']  # Always available

    try:
        import vllm
        backends.append('vllm')
    except ImportError:
        pass

    try:
        import exllamav2
        backends.append('exllamav2')
    except ImportError:
        pass

    try:
        import sglang
        backends.append('sglang')
    except ImportError:
        pass

    return backends
