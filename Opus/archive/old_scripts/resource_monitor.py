"""
OPUS MAXIMUS - RESOURCE MONITORING & GRACEFUL DEGRADATION
============================================================
Monitors GPU VRAM, system RAM, and CPU usage.
Automatically degrades generation parameters when resources are constrained.

Usage:
    from resource_monitor import ResourceMonitor

    monitor = ResourceMonitor()
    status = monitor.check_resources()
    params = monitor.adapt_generation_params(status)

Author: Automated System for Orthodox Apologetics
Date: 2025-11-07
Version: GPU-NATIVE-V2
"""

import logging
import psutil
from typing import Dict, Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - VRAM monitoring disabled")


# ============================================================================
# RESOURCE STATUS
# ============================================================================

ResourceStatus = Literal['NORMAL', 'WARNING', 'CRITICAL']


@dataclass
class ResourceSnapshot:
    """Snapshot of current system resources"""
    vram_total_gb: float
    vram_used_gb: float
    vram_free_gb: float
    ram_total_gb: float
    ram_used_gb: float
    ram_free_gb: float
    cpu_percent: float
    status: ResourceStatus


# ============================================================================
# RESOURCE MONITOR
# ============================================================================

class ResourceMonitor:
    """
    Monitor system resources and adapt generation parameters dynamically
    """

    def __init__(self,
                 vram_critical_threshold: float = 2.0,
                 vram_warning_threshold: float = 5.0,
                 ram_critical_threshold: float = 4.0,
                 ram_warning_threshold: float = 8.0):
        """
        Initialize resource monitor

        Args:
            vram_critical_threshold: VRAM threshold for CRITICAL status (GB)
            vram_warning_threshold: VRAM threshold for WARNING status (GB)
            ram_critical_threshold: RAM threshold for CRITICAL status (GB)
            ram_warning_threshold: RAM threshold for WARNING status (GB)
        """
        self.vram_critical_threshold = vram_critical_threshold
        self.vram_warning_threshold = vram_warning_threshold
        self.ram_critical_threshold = ram_critical_threshold
        self.ram_warning_threshold = ram_warning_threshold

        self.torch_available = TORCH_AVAILABLE

        logger.info(f"ResourceMonitor initialized (VRAM monitoring: {self.torch_available})")

    def get_vram_info(self) -> tuple:
        """
        Get VRAM usage information

        Returns:
            (total_gb, used_gb, free_gb) or (0, 0, 0) if unavailable
        """
        if not self.torch_available:
            return 0.0, 0.0, 0.0

        try:
            free_bytes, total_bytes = torch.cuda.mem_get_info()
            total_gb = total_bytes / 1e9
            free_gb = free_bytes / 1e9
            used_gb = total_gb - free_gb
            return total_gb, used_gb, free_gb
        except Exception as e:
            logger.error(f"Failed to get VRAM info: {e}")
            return 0.0, 0.0, 0.0

    def get_ram_info(self) -> tuple:
        """
        Get system RAM usage information

        Returns:
            (total_gb, used_gb, free_gb)
        """
        try:
            mem = psutil.virtual_memory()
            total_gb = mem.total / 1e9
            used_gb = mem.used / 1e9
            free_gb = mem.available / 1e9
            return total_gb, used_gb, free_gb
        except Exception as e:
            logger.error(f"Failed to get RAM info: {e}")
            return 0.0, 0.0, 0.0

    def get_cpu_percent(self) -> float:
        """
        Get current CPU usage percentage

        Returns:
            CPU percentage (0-100)
        """
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.error(f"Failed to get CPU usage: {e}")
            return 0.0

    def get_snapshot(self) -> ResourceSnapshot:
        """
        Get current resource snapshot

        Returns:
            ResourceSnapshot object
        """
        vram_total, vram_used, vram_free = self.get_vram_info()
        ram_total, ram_used, ram_free = self.get_ram_info()
        cpu_percent = self.get_cpu_percent()

        status = self._determine_status(vram_free, ram_free)

        return ResourceSnapshot(
            vram_total_gb=vram_total,
            vram_used_gb=vram_used,
            vram_free_gb=vram_free,
            ram_total_gb=ram_total,
            ram_used_gb=ram_used,
            ram_free_gb=ram_free,
            cpu_percent=cpu_percent,
            status=status
        )

    def _determine_status(self, vram_free_gb: float, ram_free_gb: float) -> ResourceStatus:
        """
        Determine overall resource status

        Args:
            vram_free_gb: Free VRAM in GB
            ram_free_gb: Free RAM in GB

        Returns:
            ResourceStatus
        """
        if vram_free_gb < self.vram_critical_threshold or ram_free_gb < self.ram_critical_threshold:
            return 'CRITICAL'
        elif vram_free_gb < self.vram_warning_threshold or ram_free_gb < self.ram_warning_threshold:
            return 'WARNING'
        else:
            return 'NORMAL'

    def check_resources(self) -> ResourceStatus:
        """
        Check current resource status

        Returns:
            ResourceStatus ('NORMAL', 'WARNING', or 'CRITICAL')
        """
        snapshot = self.get_snapshot()

        if snapshot.status == 'CRITICAL':
            logger.warning(
                f"CRITICAL resources: VRAM free: {snapshot.vram_free_gb:.1f}GB, "
                f"RAM free: {snapshot.ram_free_gb:.1f}GB"
            )
        elif snapshot.status == 'WARNING':
            logger.info(
                f"WARNING resources: VRAM free: {snapshot.vram_free_gb:.1f}GB, "
                f"RAM free: {snapshot.ram_free_gb:.1f}GB"
            )

        return snapshot.status

    def adapt_generation_params(self, resource_status: ResourceStatus) -> Dict[str, any]:
        """
        Adapt generation parameters based on resource availability

        Args:
            resource_status: Current resource status

        Returns:
            Dict of adjusted parameters
        """
        if resource_status == 'CRITICAL':
            logger.warning("CRITICAL resources - applying aggressive degradation")
            return {
                'n_ctx': 4096,              # Reduce from 8192
                'max_tokens': 5000,         # Reduce from 10000
                'skip_research_facts': True,  # Disable expensive queries
                'reduce_batch_size': True,
                'patristic_limit': 3,       # Reduce from 10
                'biblical_limit': 2,        # Reduce from 5
                'temperature_reduction': 0.1
            }
        elif resource_status == 'WARNING':
            logger.info("WARNING resources - applying moderate degradation")
            return {
                'n_ctx': 6144,              # Reduce from 8192
                'max_tokens': 7500,         # Reduce from 10000
                'skip_research_facts': False,
                'reduce_batch_size': False,
                'patristic_limit': 6,       # Reduce from 10
                'biblical_limit': 3,        # Reduce from 5
                'temperature_reduction': 0.0
            }
        else:
            # NORMAL - use default parameters
            return {
                'n_ctx': 8192,
                'max_tokens': 10000,
                'skip_research_facts': False,
                'reduce_batch_size': False,
                'patristic_limit': 10,
                'biblical_limit': 5,
                'temperature_reduction': 0.0
            }

    def log_resource_summary(self):
        """
        Log a detailed summary of current resources
        """
        snapshot = self.get_snapshot()

        logger.info("=" * 60)
        logger.info("RESOURCE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {snapshot.status}")
        logger.info(f"VRAM: {snapshot.vram_used_gb:.1f}GB / {snapshot.vram_total_gb:.1f}GB "
                   f"(Free: {snapshot.vram_free_gb:.1f}GB)")
        logger.info(f"RAM:  {snapshot.ram_used_gb:.1f}GB / {snapshot.ram_total_gb:.1f}GB "
                   f"(Free: {snapshot.ram_free_gb:.1f}GB)")
        logger.info(f"CPU:  {snapshot.cpu_percent:.1f}%")
        logger.info("=" * 60)

    def check_model_will_fit(self, model_size_gb: float, n_ctx: int, n_gpu_layers: int) -> tuple:
        """
        Check if a model + context will fit in VRAM

        Args:
            model_size_gb: Model size in GB
            n_ctx: Context window size
            n_gpu_layers: Number of GPU layers (-1 for all)

        Returns:
            (will_fit: bool, recommendation: str)
        """
        if not self.torch_available:
            return True, "VRAM monitoring unavailable - proceed with caution"

        vram_total, vram_used, vram_free = self.get_vram_info()

        # Estimate context VRAM usage (heuristic: ~1MB per 1024 tokens)
        context_vram_gb = (n_ctx / 1024) * 0.001

        # Estimate embeddings + FAISS overhead
        overhead_gb = 3.0

        total_required = model_size_gb + context_vram_gb + overhead_gb

        if n_gpu_layers == -1:
            # All layers on GPU
            if total_required <= vram_free:
                return True, f"Model will fit ({total_required:.1f}GB required, {vram_free:.1f}GB available)"
            else:
                return False, (
                    f"INSUFFICIENT VRAM: {total_required:.1f}GB required but only {vram_free:.1f}GB available. "
                    f"Recommend setting --n-gpu-layers to ~{int(n_gpu_layers * 0.7)} to offload to RAM."
                )
        else:
            # Partial offloading - less strict
            if model_size_gb * 0.7 <= vram_free:
                return True, f"Model will fit with partial offloading"
            else:
                return False, (
                    f"VRAM may be tight. Recommend reducing context window or using smaller model."
                )


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    """Test resource monitoring"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("=" * 80)
    print("OPUS MAXIMUS - RESOURCE MONITOR TEST")
    print("=" * 80)

    monitor = ResourceMonitor()

    # Get and display snapshot
    snapshot = monitor.get_snapshot()

    print(f"\nStatus: {snapshot.status}")
    print(f"\nVRAM:")
    print(f"  Total: {snapshot.vram_total_gb:.2f} GB")
    print(f"  Used:  {snapshot.vram_used_gb:.2f} GB")
    print(f"  Free:  {snapshot.vram_free_gb:.2f} GB")

    print(f"\nRAM:")
    print(f"  Total: {snapshot.ram_total_gb:.2f} GB")
    print(f"  Used:  {snapshot.ram_used_gb:.2f} GB")
    print(f"  Free:  {snapshot.ram_free_gb:.2f} GB")

    print(f"\nCPU: {snapshot.cpu_percent:.1f}%")

    # Test adaptation
    print("\n" + "=" * 80)
    print("ADAPTIVE PARAMETERS")
    print("=" * 80)

    params = monitor.adapt_generation_params(snapshot.status)
    print(f"\nRecommended parameters for {snapshot.status} status:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    # Test model fit check
    print("\n" + "=" * 80)
    print("MODEL FIT CHECK")
    print("=" * 80)

    test_model_size = 15.0  # 15GB model
    will_fit, recommendation = monitor.check_model_will_fit(test_model_size, 8192, -1)

    print(f"\nModel: {test_model_size}GB, Context: 8192, GPU Layers: -1 (all)")
    print(f"Will fit: {will_fit}")
    print(f"Recommendation: {recommendation}")

    print("\n" + "=" * 80)
