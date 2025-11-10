"""
OPUS MAXIMUS - LLM Interface
==============================
Unified interface for local (llama.cpp) and API-based LLM backends.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from .error_handling import (
    LLMError,
    ConfigurationError,
    retry_with_backoff,
    ErrorContext,
    validate_path
)

logger = logging.getLogger(__name__)


# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================

class BaseLLM(ABC):
    """Abstract base class for LLM backends"""

    @abstractmethod
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
        """Generate text from prompt"""
        pass

    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for text (for semantic validation)"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass


# ============================================================================
# LOCAL LLM (llama.cpp)
# ============================================================================

class LocalLLM(BaseLLM):
    """
    Local LLM using llama-cpp-python.

    Optimized for:
    - 16GB+ VRAM (GPU acceleration)
    - 32GB+ RAM (large context)
    - GGUF model format
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize local LLM.

        Args:
            config: Configuration dictionary with:
                - model_path: Path to GGUF model file
                - n_ctx: Context window size
                - n_batch: Batch size
                - n_gpu_layers: Number of layers to offload to GPU (-1 = all)
                - n_threads: Number of CPU threads
                - verbose: Enable verbose logging

        Raises:
            ConfigurationError: If model file not found
            LLMError: If model fails to load
        """
        self.config = config
        self.model_path = Path(config.get('model_path', 'models/model.gguf'))

        # Validate model exists
        validate_path(self.model_path, must_exist=True, must_be_file=True)

        logger.info(f"Loading model from {self.model_path}")
        logger.info(f"Configuration: n_ctx={config.get('n_ctx', 2048)}, "
                   f"n_gpu_layers={config.get('n_gpu_layers', -1)}")

        try:
            from llama_cpp import Llama

            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=config.get('n_ctx', 16384),
                n_batch=config.get('n_batch', 1024),
                n_gpu_layers=config.get('n_gpu_layers', -1),
                n_threads=config.get('n_threads', 16),
                verbose=config.get('verbose', False)
            )

            logger.info("Model loaded successfully")

            # Test generation
            test_output = self.llm("Test", max_tokens=1, echo=False)
            logger.debug(f"Test generation successful: {test_output}")

        except ImportError as e:
            raise ConfigurationError(
                "llama-cpp-python not installed. "
                "Install with: pip install llama-cpp-python"
            ) from e

        except Exception as e:
            raise LLMError(f"Failed to load model: {e}") from e

    @retry_with_backoff(max_retries=5, exceptions=(RuntimeError, TimeoutError))
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
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            repeat_penalty: Repetition penalty
            stop: Stop sequences

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails
        """
        with ErrorContext("LLM generation", prompt_length=len(prompt)):
            try:
                logger.debug(
                    f"Generating: prompt_length={len(prompt)}, "
                    f"max_tokens={max_tokens}, temperature={temperature}"
                )

                output = self.llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    stop=stop or [],
                    echo=False
                )

                # Validate output structure
                if not output or 'choices' not in output:
                    raise LLMError("Invalid LLM response structure")

                if not output['choices']:
                    raise LLMError("Empty choices in LLM response")

                generated_text = output['choices'][0]['text']

                # Validate generated text
                if not generated_text or len(generated_text.strip()) == 0:
                    raise LLMError("LLM generated empty text")

                logger.debug(f"Generated {len(generated_text)} characters")

                return generated_text.strip()

            except KeyError as e:
                raise LLMError(f"Malformed LLM response: {e}") from e

            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                raise LLMError(f"Generation failed: {e}") from e

    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            LLMError: If embedding generation fails
        """
        try:
            return self.llm.embed(text)
        except Exception as e:
            raise LLMError(f"Failed to generate embeddings: {e}") from e

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Token count
        """
        try:
            tokens = self.llm.tokenize(text.encode('utf-8'))
            return len(tokens)
        except Exception:
            # Fallback: estimate based on characters
            return len(text) // 4

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'llm'):
            logger.debug("Cleaning up LLM")
            del self.llm


# ============================================================================
# API-BASED LLM (OpenAI-compatible)
# ============================================================================

class APILLM(BaseLLM):
    """
    API-based LLM for cloud services.

    Compatible with:
    - OpenAI API
    - Anthropic API (Claude)
    - Together.ai API
    - Any OpenAI-compatible endpoint
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize API client.

        Args:
            config: Configuration dictionary with:
                - api_key: API key
                - model: Model identifier
                - base_url: Optional base URL for compatible APIs
                - organization: Optional organization ID

        Raises:
            ConfigurationError: If API key missing
        """
        self.config = config

        api_key = config.get('api_key')
        if not api_key:
            raise ConfigurationError("API key required for API-based LLM")

        self.model = config.get('model', 'gpt-4')
        logger.info(f"Initializing API client for model: {self.model}")

        try:
            import openai

            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=config.get('base_url'),
                organization=config.get('organization')
            )

            logger.info("API client initialized successfully")

        except ImportError as e:
            raise ConfigurationError(
                "openai package not installed. "
                "Install with: pip install openai"
            ) from e

    @retry_with_backoff(max_retries=5, exceptions=(Exception,))
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
        """
        Generate text using API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            top_k: Not used for OpenAI API
            repeat_penalty: Not directly supported, handled via frequency_penalty
            stop: Stop sequences

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails
        """
        with ErrorContext("API generation", model=self.model):
            try:
                logger.debug(
                    f"API call: model={self.model}, "
                    f"max_tokens={max_tokens}, temperature={temperature}"
                )

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=repeat_penalty - 1.0,  # Convert to API format
                    stop=stop
                )

                generated_text = response.choices[0].message.content

                if not generated_text:
                    raise LLMError("API returned empty response")

                logger.debug(f"Generated {len(generated_text)} characters")

                return generated_text.strip()

            except Exception as e:
                logger.error(f"API error: {e}")
                raise LLMError(f"API generation failed: {e}") from e

    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings using API.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            LLMError: If embedding generation fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.config.get('embedding_model', 'text-embedding-ada-002'),
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise LLMError(f"Failed to generate embeddings: {e}") from e

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4


# ============================================================================
# LLM FACTORY
# ============================================================================

def create_llm(config: Dict[str, Any]) -> BaseLLM:
    """
    Factory function to create appropriate LLM backend.

    Args:
        config: Configuration dictionary

    Returns:
        LLM instance (LocalLLM or APILLM)

    Raises:
        ConfigurationError: If configuration is invalid

    Example:
        config = {
            'use_local': True,
            'model_path': 'models/model.gguf',
            'n_ctx': 16384,
            'n_gpu_layers': -1
        }
        llm = create_llm(config)
        text = llm.generate("Write about theosis...")
    """
    use_local = config.get('use_local', True)

    if use_local:
        logger.info("Creating local LLM backend")
        return LocalLLM(config)
    else:
        logger.info("Creating API LLM backend")
        return APILLM(config)


# ============================================================================
# UTILITIES
# ============================================================================

def estimate_generation_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4"
) -> float:
    """
    Estimate cost of API generation.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model identifier

    Returns:
        Estimated cost in USD
    """
    # Pricing as of 2024 (update as needed)
    pricing = {
        'gpt-4': {'input': 0.03 / 1000, 'output': 0.06 / 1000},
        'gpt-3.5-turbo': {'input': 0.0015 / 1000, 'output': 0.002 / 1000},
        'claude-3-opus': {'input': 0.015 / 1000, 'output': 0.075 / 1000},
        'claude-3-sonnet': {'input': 0.003 / 1000, 'output': 0.015 / 1000},
    }

    rates = pricing.get(model, pricing['gpt-4'])  # Default to GPT-4
    cost = (input_tokens * rates['input']) + (output_tokens * rates['output'])

    return cost


def test_llm(llm: BaseLLM) -> bool:
    """
    Test LLM with a simple generation.

    Args:
        llm: LLM instance to test

    Returns:
        True if test passes

    Raises:
        LLMError: If test fails
    """
    logger.info("Testing LLM with sample generation...")

    try:
        result = llm.generate(
            prompt="What is theosis in Orthodox theology? Respond in one sentence.",
            max_tokens=100,
            temperature=0.7
        )

        if len(result) < 10:
            raise LLMError(f"Test generation too short: {result}")

        logger.info(f"Test successful. Generated: {result[:100]}...")
        return True

    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        raise
