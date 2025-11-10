"""
OPUS MAXIMUS - Core Generation Engine
======================================
Main engine integrating all components for theological encyclopedia generation.
"""

import logging
import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from .llm_interface import create_llm, BaseLLM
from .validators import (
    TheologicalValidator,
    StyleValidator,
    PatristicCitationValidator,
    StructuralValidator,
    ValidationResult
)
from .checkpoint_manager import CheckpointManager, ResumableGenerationMixin
from .caching import MultiTierCache, make_cache_key
from .prompts import PromptTemplates, SectionType
from .error_handling import (
    GenerationError,
    ValidationError,
    retry_with_backoff,
    ErrorContext,
    validate_config
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class OpusConfig:
    """Configuration for Opus Maximus Engine"""

    # LLM settings
    use_local: bool = True
    model_path: str = "models/model.gguf"
    n_ctx: int = 16384
    n_batch: int = 1024
    n_gpu_layers: int = -1
    n_threads: int = 16
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1

    # Generation settings
    min_total_words: int = 10000
    max_total_words: int = 15000
    max_section_attempts: int = 3
    max_expansion_attempts: int = 2

    # Validation thresholds
    quality_threshold: float = 0.85
    min_patristic_citations: int = 40
    min_biblical_references: int = 60

    # Paths
    output_dir: Path = Path("GENERATED_ENTRIES_MASTER")
    checkpoint_dir: Path = Path(".checkpoints")
    cache_dir: Path = Path(".cache")

    # Caching
    enable_caching: bool = True
    l1_cache_size: int = 5000
    l2_cache_size: int = 50000

    # Validation settings (for validators)
    validation: Dict[str, Any] = None

    def __post_init__(self):
        """Convert paths to Path objects"""
        self.output_dir = Path(self.output_dir)
        self.checkpoint_dir = Path(self.checkpoint_dir)
        self.cache_dir = Path(self.cache_dir)

        if self.validation is None:
            self.validation = {}

    @classmethod
    def from_yaml(cls, config_path: Path) -> 'OpusConfig':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        # Flatten nested structure
        config_dict = {}

        # Model settings
        if 'model' in data:
            config_dict['model_path'] = data['model'].get('path', 'models/model.gguf')
            config_dict['n_ctx'] = data['model'].get('n_ctx', 16384)
            config_dict['n_batch'] = data['model'].get('n_batch', 1024)
            config_dict['n_gpu_layers'] = data['model'].get('n_gpu_layers', -1)
            config_dict['n_threads'] = data['model'].get('n_threads', 16)
            config_dict['temperature'] = data['model'].get('temperature', 0.7)
            config_dict['top_p'] = data['model'].get('top_p', 0.9)
            config_dict['top_k'] = data['model'].get('top_k', 40)
            config_dict['repeat_penalty'] = data['model'].get('repeat_penalty', 1.1)

        # Generation settings
        if 'generation' in data:
            config_dict['min_total_words'] = data['generation'].get('min_total_words', 10000)
            config_dict['max_total_words'] = data['generation'].get('max_total_words', 15000)
            config_dict['max_section_attempts'] = data['generation'].get('max_section_attempts', 3)

        # Validation settings
        if 'validation' in data:
            config_dict['validation'] = data['validation']
            config_dict['quality_threshold'] = data['validation'].get('quality_threshold', 0.85)
            config_dict['min_patristic_citations'] = data['validation'].get('min_patristic_citations', 40)
            config_dict['min_biblical_references'] = data['validation'].get('min_biblical_references', 60)

        # Caching settings
        if 'caching' in data:
            config_dict['enable_caching'] = data['caching'].get('enable', True)
            config_dict['l1_cache_size'] = data['caching'].get('l1_cache_size', 5000)
            config_dict['l2_cache_size'] = data['caching'].get('l2_cache_size', 50000)

        # Paths
        if 'paths' in data:
            config_dict['output_dir'] = Path(data['paths'].get('output_dir', 'GENERATED_ENTRIES_MASTER'))
            config_dict['checkpoint_dir'] = Path(data['paths'].get('checkpoint_dir', '.checkpoints'))
            config_dict['cache_dir'] = Path(data['paths'].get('cache_dir', '.cache'))

        return cls(**config_dict)


# ============================================================================
# GENERATION RESULT
# ============================================================================

@dataclass
class GenerationResult:
    """Result of entry generation"""
    subject: str
    tier: str
    category: str
    content: str
    word_count: int
    generation_time_seconds: float
    validation: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


# ============================================================================
# OPUS MAXIMUS ENGINE
# ============================================================================

class OpusMaximusEngine(ResumableGenerationMixin):
    """
    Main generation engine for Opus Maximus.

    Features:
    - Complete entry generation with 6 sections
    - Multi-tier caching
    - Checkpoint/resume capability
    - Comprehensive validation
    - Error recovery
    """

    def __init__(self, config: OpusConfig):
        """
        Initialize Opus Maximus Engine.

        Args:
            config: Engine configuration
        """
        self.config = config
        logger.info("Initializing Opus Maximus Engine...")

        # Create output directories
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Initialize LLM
        with ErrorContext("Initializing LLM"):
            llm_config = {
                'use_local': config.use_local,
                'model_path': config.model_path,
                'n_ctx': config.n_ctx,
                'n_batch': config.n_batch,
                'n_gpu_layers': config.n_gpu_layers,
                'n_threads': config.n_threads,
            }
            self.llm = create_llm(llm_config)
            logger.info("LLM initialized successfully")

        # Initialize validators
        self.theological_validator = TheologicalValidator(config.validation)
        self.style_validator = StyleValidator(asdict(config))
        self.citation_validator = PatristicCitationValidator()
        self.structural_validator = StructuralValidator()
        logger.info("Validators initialized")

        # Initialize caching
        if config.enable_caching:
            self.cache = MultiTierCache(
                l1_size=config.l1_cache_size,
                l2_size=config.l2_cache_size,
                cache_dir=config.cache_dir,
                enable_l3=True
            )
            logger.info("Multi-tier caching enabled")
        else:
            self.cache = None
            logger.info("Caching disabled")

        # Initialize checkpoint manager
        self.checkpoint_mgr = CheckpointManager(config.checkpoint_dir)
        logger.info("Checkpoint manager initialized")

        logger.info("Opus Maximus Engine ready")

    def generate_entry(
        self,
        subject: str,
        tier: str = "Tier 1",
        category: str = "Theology",
        resume: bool = True
    ) -> GenerationResult:
        """
        Generate complete encyclopedia entry.

        Args:
            subject: Entry subject
            tier: Priority tier
            category: Subject category
            resume: Whether to resume from checkpoint

        Returns:
            GenerationResult with complete entry

        Raises:
            GenerationError: If generation fails
        """
        start_time = time.time()
        logger.info(f"Starting generation: {subject} ({tier}, {category})")

        # Try to resume from checkpoint
        state = None
        if resume:
            state = self.try_resume(subject)

        if state:
            logger.info(f"Resuming from checkpoint: phase={state.get('phase')}")
            blueprint = state.get('blueprint')
            sections = state.get('sections', {})
        else:
            blueprint = None
            sections = {}

        try:
            # Phase 1: Generate blueprint
            if not blueprint:
                blueprint = self._generate_blueprint(subject, tier, category)
                self.save_progress(subject, 'blueprint_complete', blueprint=blueprint, sections=sections)

            # Phase 2: Generate sections
            section_types = list(SectionType)

            for section_type in section_types:
                section_key = section_type.value

                # Skip if already generated
                if section_key in sections:
                    logger.info(f"Section {section_key} already generated, skipping")
                    continue

                # Generate section
                section_content = self._generate_section(subject, section_type, blueprint)
                sections[section_key] = section_content

                # Save checkpoint after each section
                self.save_progress(
                    subject,
                    f'section_{section_key}_complete',
                    blueprint=blueprint,
                    sections=sections
                )

            # Phase 3: Assemble entry
            logger.info("Assembling complete entry...")
            full_content = self._assemble_entry(subject, sections)

            # Phase 4: Final validation
            logger.info("Running final validation...")
            validation_result = self._validate_entry(full_content)

            # Create result
            result = GenerationResult(
                subject=subject,
                tier=tier,
                category=category,
                content=full_content,
                word_count=len(full_content.split()),
                generation_time_seconds=time.time() - start_time,
                validation={
                    'valid': validation_result.valid,
                    'errors': validation_result.errors,
                    'warnings': validation_result.warnings,
                    'metrics': validation_result.metrics,
                    'score': validation_result.score
                },
                metadata={
                    'blueprint_length': len(blueprint.split()),
                    'sections_count': len(sections),
                    'config': asdict(self.config)
                },
                timestamp=datetime.now().isoformat()
            )

            # Save entry
            self._save_entry(result)

            # Mark complete (delete checkpoint)
            self.mark_complete(subject)

            logger.info(
                f"Generation complete: {subject} "
                f"({result.word_count} words, {result.generation_time_seconds:.1f}s, "
                f"score: {result.validation['score']:.3f})"
            )

            return result

        except Exception as e:
            logger.error(f"Generation failed for {subject}: {e}")
            # Keep checkpoint for resume
            raise GenerationError(f"Failed to generate {subject}: {e}") from e

    @retry_with_backoff(max_retries=3)
    def _generate_blueprint(self, subject: str, tier: str, category: str) -> str:
        """Generate entry blueprint/outline"""

        # Check cache
        cache_key = make_cache_key("blueprint", subject=subject, tier=tier, category=category)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("Blueprint retrieved from cache")
                return cached

        # Generate prompt
        prompt = PromptTemplates.blueprint_prompt(subject, tier, category)

        # Generate
        logger.info(f"Generating blueprint for {subject}...")
        blueprint = self.llm.generate(
            prompt=prompt,
            max_tokens=3000,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            repeat_penalty=self.config.repeat_penalty
        )

        # Cache
        if self.cache:
            self.cache.put(cache_key, blueprint)

        logger.info(f"Blueprint generated ({len(blueprint.split())} words)")
        return blueprint

    def _generate_section(
        self,
        subject: str,
        section_type: SectionType,
        blueprint: str
    ) -> str:
        """Generate individual section with validation and retry"""

        # Word count targets per section
        word_targets = {
            SectionType.STRATEGIC_ROLE: (1200, 1800),
            SectionType.CLASSIFICATION: (1200, 1800),
            SectionType.PRIMARY_WORKS: (1500, 2500),
            SectionType.PATRISTIC_MIND: (1800, 2500),
            SectionType.SYMPHONY_CLASHES: (2000, 3000),
            SectionType.ORTHODOX_AFFIRMATION: (2000, 2500)
        }

        min_words, max_words = word_targets.get(section_type, (1500, 2000))

        # Check cache
        cache_key = make_cache_key(
            "section",
            subject=subject,
            section=section_type.value,
            blueprint_hash=hash(blueprint)[:16]
        )

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Section {section_type.value} retrieved from cache")
                return cached

        # Generate with retry logic
        for attempt in range(self.config.max_section_attempts):
            logger.info(
                f"Generating section {section_type.value} "
                f"(attempt {attempt + 1}/{self.config.max_section_attempts})"
            )

            # Build prompt
            prompt = PromptTemplates.section_prompt(
                subject=subject,
                section_type=section_type,
                blueprint=blueprint,
                min_words=min_words,
                max_words=max_words,
                context={}
            )

            # Generate
            max_tokens = int(max_words * 1.5)  # ~1.3 tokens per word
            section_content = self.llm.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                repeat_penalty=self.config.repeat_penalty
            )

            # Validate
            validation = self._validate_section(section_content)

            # Check if acceptable
            if validation.valid or len(validation.errors) < 3:
                logger.info(
                    f"Section {section_type.value} generated successfully "
                    f"({len(section_content.split())} words, "
                    f"{len(validation.errors)} errors, "
                    f"{len(validation.warnings)} warnings)"
                )

                # Cache
                if self.cache:
                    self.cache.put(cache_key, section_content)

                return section_content

            # If not acceptable and attempts remain, try correction
            if attempt < self.config.max_section_attempts - 1:
                logger.warning(
                    f"Section validation failed ({len(validation.errors)} errors), "
                    f"attempting correction..."
                )

                correction_prompt = PromptTemplates.correction_prompt(
                    original_prompt=prompt,
                    generated_text=section_content,
                    errors=validation.errors
                )

                section_content = self.llm.generate(
                    prompt=correction_prompt,
                    max_tokens=max_tokens
                )

        # If we exhausted attempts, return best effort
        logger.warning(
            f"Section {section_type.value} generated with errors "
            f"after {self.config.max_section_attempts} attempts"
        )
        return section_content

    def _validate_section(self, content: str) -> ValidationResult:
        """Validate section content"""
        result = ValidationResult(valid=True)

        # Run style validation
        style_result = self.style_validator.validate(content)
        result.errors.extend(style_result.errors)
        result.warnings.extend(style_result.warnings)
        result.metrics.update(style_result.metrics)

        # Run theological validation
        theo_result = self.theological_validator.validate(content)
        result.errors.extend(theo_result.errors)
        result.warnings.extend(theo_result.warnings)
        result.metrics.update(theo_result.metrics)

        result.valid = len(result.errors) == 0
        result.score = (style_result.score + theo_result.score) / 2

        return result

    def _assemble_entry(self, subject: str, sections: Dict[str, str]) -> str:
        """Assemble sections into complete entry"""

        # Build entry with proper structure
        entry_parts = [
            f"# {subject.upper()}",
            "",
            "## I. STRATEGIC ROLE",
            sections.get(SectionType.STRATEGIC_ROLE.value, ""),
            "",
            "## II. CLASSIFICATION",
            sections.get(SectionType.CLASSIFICATION.value, ""),
            "",
            "## III. PRIMARY WORKS",
            sections.get(SectionType.PRIMARY_WORKS.value, ""),
            "",
            "## IV. THE PATRISTIC MIND",
            sections.get(SectionType.PATRISTIC_MIND.value, ""),
            "",
            "## V. SYMPHONY OF CLASHES",
            sections.get(SectionType.SYMPHONY_CLASHES.value, ""),
            "",
            "## VI. ORTHODOX AFFIRMATION",
            sections.get(SectionType.ORTHODOX_AFFIRMATION.value, ""),
        ]

        return "\n".join(entry_parts)

    def _validate_entry(self, content: str) -> ValidationResult:
        """Comprehensive validation of complete entry"""
        result = ValidationResult(valid=True)

        # Structural validation
        struct_result = self.structural_validator.validate(content)
        result.errors.extend(struct_result.errors)
        result.warnings.extend(struct_result.warnings)
        result.metrics.update(struct_result.metrics)

        # Style validation
        style_result = self.style_validator.validate(content)
        result.errors.extend(style_result.errors)
        result.warnings.extend(style_result.warnings)
        result.metrics.update(style_result.metrics)

        # Theological validation
        theo_result = self.theological_validator.validate(content)
        result.errors.extend(theo_result.errors)
        result.warnings.extend(theo_result.warnings)
        result.metrics.update(theo_result.metrics)

        # Overall score
        result.score = (
            struct_result.score * 0.2 +
            style_result.score * 0.4 +
            theo_result.score * 0.4
        )

        result.valid = result.score >= self.config.quality_threshold

        logger.info(
            f"Final validation: score={result.score:.3f}, "
            f"errors={len(result.errors)}, warnings={len(result.warnings)}"
        )

        return result

    def _save_entry(self, result: GenerationResult):
        """Save generated entry to disk"""

        # Create tier directory
        tier_dir = self.config.output_dir / result.tier.replace(' ', '_')
        tier_dir.mkdir(parents=True, exist_ok=True)

        # Save markdown
        safe_name = result.subject.replace(' ', '_').replace('/', '_')
        md_file = tier_dir / f"{safe_name}.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            # YAML frontmatter
            f.write("---\n")
            f.write(f"title: {result.subject}\n")
            f.write(f"tier: {result.tier}\n")
            f.write(f"category: {result.category}\n")
            f.write(f"word_count: {result.word_count}\n")
            f.write(f"validation_score: {result.validation['score']:.3f}\n")
            f.write(f"generated: {result.timestamp}\n")
            f.write("---\n\n")

            # Content
            f.write(result.content)

        logger.info(f"Entry saved: {md_file}")

        # Save JSON metadata
        json_file = tier_dir / f"{safe_name}.json"
        import json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        logger.debug(f"Metadata saved: {json_file}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_engine_from_config(config_path: Path) -> OpusMaximusEngine:
    """
    Create engine from configuration file.

    Args:
        config_path: Path to YAML configuration

    Returns:
        Initialized OpusMaximusEngine
    """
    config = OpusConfig.from_yaml(config_path)
    return OpusMaximusEngine(config)
