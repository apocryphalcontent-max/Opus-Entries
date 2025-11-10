"""
FILE 14: MODEL ROUTER
====================
Intelligent model routing based on task characteristics and performance metrics.
Dynamically selects optimal model for each section generation.
File 9 of 20: Model Router
Optimized for: VRAM-Aware Dynamic Loading (Edits 19 & 20)
"""
import logging
import time
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task types for routing."""
    BLUEPRINT = "blueprint"
    SECTION = "section"
    CORRECTION = "correction"
    EXPANSION = "expansion"
    VALIDATION = "validation"

@dataclass
class ModelCapabilities:
    """Model capability descriptor."""
    name: str
    capabilities: List[str]
    avg_quality: float = 0.5
    success_rate: float = 0.8
    avg_latency: float = 0.0

class ModelRouter:
    """Intelligent task-to-model routing with VRAM management."""
    def __init__(self):
        self.models: Dict[str, ModelCapabilities] = {}
        self.routing_history: List[Dict] = []
        # Edit 19: VRAM-aware model caching
        self.model_instances: Dict[str, Dict[str, Any]] = {} # {name: {'model': obj, 'vram': float, 'last_used': float}}
        self.vram_available_gb = 16.0 # Target hardware limit
        self.vram_used_gb = 0.0

        self.task_model_mapping: Dict[TaskType, List[str]] = {
            TaskType.BLUEPRINT: ["blueprint", "general", "planning"],
            TaskType.SECTION: ["section", "generation", "writing", "general"],
            TaskType.CORRECTION: ["correction", "refinement", "editing"],
            TaskType.EXPANSION: ["expansion", "generation", "writing"],
            TaskType.VALIDATION: ["validation", "analysis", "review"]
        }

    def register_model(self, name: str, capabilities: List[str]) -> bool:
        """Register model capabilities (does not load model yet)."""
        if name in self.models:
            logger.warning(f"Model already registered: {name}")
            return False
        self.models[name] = ModelCapabilities(name=name, capabilities=capabilities)
        logger.info(f"Registered model capabilities: {name}")
        return True

    def route_task(self, task_type: TaskType, context: Dict = None) -> Optional[str]:
        """Route task to optimal model name."""
        candidates = self._find_candidates(task_type)
        if not candidates:
            logger.warning(f"No candidates found for {task_type.value}")
            return None
        
        # Select best candidate based on metrics
        best_model_name = self._select_best_candidate(candidates)
        
        # Log routing decision
        self.routing_history.append({
            "task": task_type.value,
            "model": best_model_name,
            "timestamp": time.time()
        })
        logger.info(f"Routed {task_type.value} to {best_model_name}")
        return best_model_name

    # Edit 20: Dynamic Model Loading
    def load_model_if_needed(self, model_name: str, model_path: str) -> Any:
        """Load model into VRAM only when needed, managing 16GB limit."""
        if model_name in self.model_instances:
            self.model_instances[model_name]['last_used'] = time.time()
            return self.model_instances[model_name]['model']

        # Defer imports to avoid early VRAM allocation
        try:
            from llama_cpp import Llama
        except ImportError:
            logger.error("llama_cpp not installed, cannot load models dynamically.")
            return None

        # Estimate VRAM usage (rough heuristic: GGUF file size + 10% overhead for context)
        try:
            file_size_gb = Path(model_path).stat().st_size / (1024**3)
            estimated_vram = file_size_gb * 1.1
        except FileNotFoundError:
             logger.error(f"Model file not found at {model_path}")
             return None

        # Evict if necessary
        while self.vram_used_gb + estimated_vram > self.vram_available_gb * 0.95: # 5% buffer
            if not self.model_instances:
                logger.warning(f"Warning: {model_name} ({estimated_vram:.1f}GB) may exceed VRAM ({self.vram_available_gb}GB)")
                break
            self._unload_oldest_model()

        logger.info(f"Dynamically loading {model_name} (~{estimated_vram:.1f}GB)...")
        try:
            # Use standard optimized parameters for 16GB VRAM
            model = Llama(
                model_path=model_path,
                n_ctx=8192,      # Standard context for dynamic models
                n_gpu_layers=-1, # Offload all to GPU
                verbose=False
            )
            self.model_instances[model_name] = {
                'model': model,
                'vram': estimated_vram,
                'last_used': time.time()
            }
            self.vram_used_gb += estimated_vram
            logger.info(f"Loaded {model_name}. VRAM usage: {self.vram_used_gb:.1f}/{self.vram_available_gb} GB")
            return model
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")
            return None

    def _unload_oldest_model(self):
        """Unload least recently used model to free VRAM."""
        if not self.model_instances: return
        # Find model with oldest 'last_used' timestamp
        oldest_name = min(self.model_instances, key=lambda k: self.model_instances[k]['last_used'])
        vram_freed = self.model_instances[oldest_name]['vram']
        
        # Delete the Llama object to free VRAM (Python's GC usually handles this if no references remain)
        del self.model_instances[oldest_name]['model']
        del self.model_instances[oldest_name]
        
        self.vram_used_gb -= vram_freed
        logger.info(f"Unloaded {oldest_name} (freed {vram_freed:.1f}GB)")

    def _find_candidates(self, task_type: TaskType) -> List[str]:
        """Find models capable of task type."""
        required_capabilities = self.task_model_mapping.get(task_type, [])
        candidates = []
        for name, cap in self.models.items():
            if any(req in cap.capabilities for req in required_capabilities):
                candidates.append(name)
        return candidates

    def _select_best_candidate(self, candidates: List[str]) -> str:
        """Select best model from candidates based on scores."""
        if not candidates: return None
        scores = {}
        for name in candidates:
            cap = self.models[name]
            # Weighted score: 60% quality, 30% success rate, 10% latency bonus
            # Latency bonus: 1.0 if 0s latency, decreases as latency increases
            latency_bonus = max(0.0, 1.0 - (cap.avg_latency / 60.0)) 
            score = (cap.avg_quality * 0.6) + (cap.success_rate * 0.3) + (latency_bonus * 0.1)
            
            # Slight boost if already loaded in VRAM (Edit 20 optimization)
            if name in self.model_instances:
                score += 0.05
                
            scores[name] = score
            
        return max(scores, key=scores.get)

    def update_model_metrics(self, model_name: str, quality: float,
                             success: bool = True, latency: float = 0.0):
        """Update model performance metrics."""
        if model_name not in self.models: return
        model = self.models[model_name]
        # Exponential moving averages
        model.avg_quality = (model.avg_quality * 0.8) + (quality * 0.2)
        model.success_rate = (model.success_rate * 0.95) + (1.0 if success else 0.0) * 0.05
        model.avg_latency = (model.avg_latency * 0.9) + (latency * 0.1)

    def get_model_performance_report(self) -> str:
        """Generate model performance report."""
        report = "MODEL ROUTER PERFORMANCE REPORT\n" + "=" * 60 + "\n"
        for name, model in self.models.items():
            loaded_status = "[LOADED]" if name in self.model_instances else "[UNLOADED]"
            report += f" {name} {loaded_status}:\n"
            report += f"   Quality: {model.avg_quality:.2f} | Success: {model.success_rate:.0%} | Latency: {model.avg_latency:.1f}s\n"
        report += f"\nVRAM Usage: {self.vram_used_gb:.1f} / {self.vram_available_gb:.1f} GB\n"
        return report

# Global router instance
model_router = ModelRouter()