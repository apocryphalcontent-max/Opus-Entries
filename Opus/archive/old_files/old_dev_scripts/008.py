"""
FILE 13: ENSEMBLE GENERATION
=============================
Multi-model synthesis combining outputs from multiple LLMs for superior quality.
Implements voting, merging, and selection strategies.
File 8 of 20: Ensemble Generator
Optimized for: Parallel Execution (Edit 18)
"""
import logging
import concurrent.futures
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class EnsembleStrategy(Enum):
    """Ensemble combination strategies."""
    VOTING = "voting"           # Majority vote on best
    MERGING = "merging"         # Combine strengths
    SELECTION = "selection"     # Pick best by criteria
    WEIGHTED = "weighted"       # Weight by confidence scores
    HIERARCHICAL = "hierarchical" # Cascade through models

@dataclass
class GenerationOutput:
    """Single model's output."""
    model_name: str
    content: str
    quality_score: float
    confidence: float
    metadata: Dict = None

class EnsembleGenerator:
    """Combines outputs from multiple models."""
    def __init__(self, models: List = None, strategy: EnsembleStrategy = EnsembleStrategy.WEIGHTED):
        self.models = models or []
        self.strategy = strategy
        self.outputs: List[GenerationOutput] = []
        self.final_output: str = ""
        self.generation_log: List[Dict] = []

    # Edit 18: Parallel Model Generation
    def generate_and_synthesize(self, prompt: str, section_metadata: Dict = None) -> Tuple[str, Dict]:
        """Generate with all models in parallel and synthesize."""
        self.outputs = []
        
        def _generate_single(model):
            """Helper for parallel execution."""
            try:
                # Assuming model.generate is thread-safe or handles its own locking if sharing GPU
                output = model.generate(prompt, temperature=0.7)
                quality = self._evaluate_quality(output)
                confidence = self._compute_confidence(output, quality)
                return GenerationOutput(
                    model_name=model.name,
                    content=output,
                    quality_score=quality,
                    confidence=confidence,
                    metadata={"tokens": len(output.split()), "model_type": type(model).__name__}
                )
            except Exception as e:
                logger.error(f"Model {model.name} failed during ensemble generation: {e}")
                return None

        # Use ThreadPoolExecutor for parallelism. 
        # Note: If models are strictly GPU-bound and cannot run concurrently on same GPU, 
        # this might need ProcessPoolExecutor or sequential execution depending on VRAM.
        # Assuming here that models are either API-based or small enough to co-exist/swap efficiently.
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(self.models), 8)) as executor:
            future_to_model = {executor.submit(_generate_single, model): model for model in self.models}
            for future in concurrent.futures.as_completed(future_to_model):
                result = future.result()
                if result:
                    self.outputs.append(result)
                    logger.info(f"Ensemble model finished: {result.model_name} (Q:{result.quality_score:.2f})")

        if not self.outputs:
            raise Exception("All ensemble models failed to produce output")

        # Synthesize based on strategy
        if self.strategy == EnsembleStrategy.VOTING:
            self.final_output = self._voting_synthesis()
        elif self.strategy == EnsembleStrategy.MERGING:
            self.final_output = self._merging_synthesis()
        elif self.strategy == EnsembleStrategy.SELECTION:
            self.final_output = self._selection_synthesis()
        elif self.strategy == EnsembleStrategy.WEIGHTED:
            self.final_output = self._weighted_synthesis()
        elif self.strategy == EnsembleStrategy.HIERARCHICAL:
            self.final_output = self._hierarchical_synthesis()

        metadata = self._generate_metadata()
        return self.final_output, metadata

    def _voting_synthesis(self) -> str:
        """Majority vote synthesis."""
        # Simplified: select most frequent quality tier
        qualities = [o.quality_score for o in self.outputs]
        best_idx = qualities.index(max(qualities))
        result = self.outputs[best_idx].content
        logger.info(f"Voting: selected {self.outputs[best_idx].model_name}")
        return result

    def _merging_synthesis(self) -> str:
        """Merge outputs by taking unique sentences."""
        all_sentences = set()
        for output in self.outputs:
            sentences = output.content.split('.')
            all_sentences.update(sentences)
        # Basic reassembly - in production needs advanced NLP to order correctly
        result = '. '.join(sorted([s.strip() for s in all_sentences if s.strip()])) + '.'
        logger.info("Merging: combined unique content")
        return result

    def _selection_synthesis(self) -> str:
        """Select best by criteria."""
        best = max(self.outputs, key=lambda x: x.quality_score + x.confidence)
        logger.info(f"Selection: {best.model_name} (score={best.quality_score:.2f})")
        return best.content

    def _weighted_synthesis(self) -> str:
        """Weighted combination (currently selects highest weighted whole output)."""
        # Normalize weights
        total_weight = sum(o.confidence * o.quality_score for o in self.outputs) or 1
        weights = [o.confidence * o.quality_score / total_weight for o in self.outputs]
        
        # Start with highest weight output
        best_idx = weights.index(max(weights))
        result = self.outputs[best_idx].content
        logger.info(f"Weighted: {self.outputs[best_idx].model_name} (weight={weights[best_idx]:.2f})")
        return result

    def _hierarchical_synthesis(self) -> str:
        """Cascade through models by confidence."""
        sorted_outputs = sorted(self.outputs, key=lambda x: x.confidence, reverse=True)
        # Use highest confidence output
        best = sorted_outputs[0]
        logger.info(f"Hierarchical: selected {best.model_name} (confidence={best.confidence:.2f})")
        return best.content

    def _evaluate_quality(self, content: str) -> float:
        """Evaluate output quality (0.0-1.0)."""
        # Simplified evaluation
        score = 0.5
        # Length score
        words = len(content.split())
        score += min(words / 1000, 0.2) # Up to 0.2 for adequate length
        # Coherence (simplified)
        if "." in content and "," in content:
            score += 0.15
        # Structure (simplified)
        if content.count("\n") > 3:
            score += 0.15
        return min(score, 1.0)

    def _compute_confidence(self, content: str, quality: float) -> float:
        """Compute model confidence in output."""
        # Based on content coherence and quality
        return min(quality * 1.1, 1.0)

    def _generate_metadata(self) -> Dict:
        """Generate synthesis metadata."""
        return {
            "strategy": self.strategy.value,
            "models_used": len(self.outputs),
            "model_names": [o.model_name for o in self.outputs],
            "avg_quality": sum(o.quality_score for o in self.outputs) / len(self.outputs) if self.outputs else 0,
            "best_quality": max(o.quality_score for o in self.outputs) if self.outputs else 0,
        }

    def get_synthesis_report(self) -> str:
        """Generate synthesis report."""
        report = "ENSEMBLE SYNTHESIS REPORT\n"
        report += "=" * 60 + "\n"
        report += f"Strategy: {self.strategy.value}\n"
        report += f"Models: {len(self.outputs)}\n\n"
        report += "Model Outputs:\n"
        for output in self.outputs:
            report += f"  {output.model_name}:\n"
            report += f"    Quality: {output.quality_score:.2f}\n"
            report += f"    Confidence: {output.confidence:.2f}\n"
            report += f"    Words: {len(output.content.split())}\n"
        report += f"\nFinal Output: {len(self.final_output.split())} words\n"
        return report

ensemble_generator = EnsembleGenerator()