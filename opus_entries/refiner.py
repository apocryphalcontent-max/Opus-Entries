"""
Iterative refinement module for achieving CELESTIAL-tier entries
"""
from typing import Optional
from .models import Entry, ValidationResult
from .validator import EntryValidator
from .llm_client import LLMClient
from .config import Config


class EntryRefiner:
    """Refiner for iteratively improving entries to CELESTIAL tier (95-100 score)"""
    
    def __init__(self, config: Optional[Config] = None, llm_client: Optional[LLMClient] = None):
        """
        Initialize the refiner
        
        Args:
            config: Configuration object (creates default if not provided)
            llm_client: LLM client (creates default if not provided)
        """
        self.config = config or Config()
        self.validator = EntryValidator(config=self.config)
        
        if llm_client:
            self.llm_client = llm_client
        else:
            llm_config = self.config.get_llm_config()
            self.llm_client = LLMClient(
                base_url=llm_config.get("base_url", "http://localhost:11434"),
                timeout=llm_config.get("timeout", 300)
            )
    
    def refine_to_celestial(self, entry: Entry, model: str = "llama2", max_attempts: int = 3) -> Entry:
        """
        Iteratively refine entry until CELESTIAL tier (95+) achieved
        
        Args:
            entry: The entry to refine
            model: LLM model to use for refinement
            max_attempts: Maximum refinement attempts before giving up
        
        Returns:
            Refined entry (CELESTIAL tier or best achieved)
        """
        celestial_threshold = self.config.get("refinement.celestial_threshold", 95)
        
        for attempt in range(max_attempts):
            # Validate current entry
            result = self.validator.validate(entry)
            
            if result.score >= celestial_threshold:
                # CELESTIAL achieved!
                return entry
            
            # Identify deficiencies and apply targeted refinement
            if result.theological_depth_score < 90:
                entry = self.enhance_theological_depth(entry, model)
            
            if result.word_count_score < 100:
                entry = self.expand_sections(entry, model)
            
            if result.coherence_score < 90:
                entry = self.improve_flow(entry, model)
            
            if result.section_balance_score < 90:
                entry = self.rebalance_sections(entry, model)
            
            if result.orthodox_perspective_score < 90:
                entry = self.strengthen_orthodox_voice(entry, model)
        
        # Return best achieved (even if not CELESTIAL)
        return entry
    
    def enhance_theological_depth(self, entry: Entry, model: str = "llama2") -> Entry:
        """
        Enhance theological depth by adding Patristic citations and theological vocabulary
        
        Args:
            entry: Entry to enhance
            model: LLM model to use
        
        Returns:
            Enhanced entry
        """
        # Focus on sections that need more theological depth
        for section in entry.sections:
            if section.name in ["The Patristic Mind", "Orthodox Affirmation", "Symphony of Clashes"]:
                prompt = f"""Enhance the theological depth of this section by adding:
- More Patristic citations (cite specific works and Church Fathers)
- Scripture references with exegesis
- Orthodox theological vocabulary (Theosis, Energies, Perichoresis, etc.)
- Liturgical connections

Current section content:
{section.content}

Provide enhanced version with deeper theological content while maintaining the original structure and voice."""
                
                enhanced_content = self.llm_client.generate(
                    prompt=prompt,
                    model=model,
                    system_prompt="You are an Orthodox Christian theological scholar. Enhance theological depth while maintaining liturgical voice and style mandates."
                )
                
                section.content = enhanced_content
        
        return entry
    
    def expand_sections(self, entry: Entry, model: str = "llama2") -> Entry:
        """
        Expand sections to meet minimum word counts
        
        Args:
            entry: Entry to expand
            model: LLM model to use
        
        Returns:
            Expanded entry
        """
        section_minimums = {
            "Introduction": 1750,
            "The Patristic Mind": 2250,
            "Symphony of Clashes": 2350,
            "Orthodox Affirmation": 2250,
            "Synthesis": 1900,
            "Conclusion": 1800
        }
        
        for section in entry.sections:
            if section.name in section_minimums:
                minimum = section_minimums[section.name]
                
                if section.word_count < minimum:
                    shortfall = minimum - section.word_count
                    
                    prompt = f"""Expand this section by approximately {shortfall} words while maintaining:
- The original argument and structure
- Orthodox theological voice
- Style mandates (four-space indentation, no em-dashes, theological capitalization)
- Natural flow and coherence

Current section ({section.word_count} words):
{section.content}

Provide expanded version (target: {minimum}+ words)."""
                    
                    expanded_content = self.llm_client.generate(
                        prompt=prompt,
                        model=model,
                        system_prompt="You are an Orthodox Christian theological scholar. Expand thoughtfully while maintaining quality and voice."
                    )
                    
                    section.content = expanded_content
        
        return entry
    
    def improve_flow(self, entry: Entry, model: str = "llama2") -> Entry:
        """
        Improve coherence and flow by adding cross-references and transitions
        
        Args:
            entry: Entry to improve
            model: LLM model to use
        
        Returns:
            Improved entry
        """
        # Add cross-references between sections
        for i, section in enumerate(entry.sections):
            if i > 0:  # Not the introduction
                prompt = f"""Improve the opening of this section to better connect with previous sections.
Add a transitional paragraph (using liturgical conjunctions: YET, AND, BUT, FOR, SO, BECAUSE, THEREFORE, THUS).
NO banned academic phrases ("Furthermore," "Moreover," "However," etc.).

Previous section: {entry.sections[i-1].name}
Current section: {section.name}

Current content:
{section.content}

Provide improved version with better flow and connections."""
                
                improved_content = self.llm_client.generate(
                    prompt=prompt,
                    model=model,
                    system_prompt="You are an Orthodox Christian theological scholar. Improve flow while maintaining liturgical voice."
                )
                
                section.content = improved_content
        
        return entry
    
    def rebalance_sections(self, entry: Entry, model: str = "llama2") -> Entry:
        """
        Rebalance section lengths to achieve proper distribution
        
        Args:
            entry: Entry to rebalance
            model: LLM model to use
        
        Returns:
            Rebalanced entry
        """
        # This combines expand_sections logic with potential condensing
        # For now, just call expand_sections since we have minimums only
        return self.expand_sections(entry, model)
    
    def strengthen_orthodox_voice(self, entry: Entry, model: str = "llama2") -> Entry:
        """
        Strengthen Orthodox distinctives and liturgical grounding
        
        Args:
            entry: Entry to strengthen
            model: LLM model to use
        
        Returns:
            Strengthened entry
        """
        for section in entry.sections:
            prompt = f"""Strengthen the Orthodox Christian voice in this section by:
- Increasing Orthodox-specific terminology and concepts
- Adding contrasts with Western theology (3+ minimum)
- Emphasizing liturgical connections and the Mysteries/Sacraments
- Using apocalyptic maximalist vocabulary (crushing, devastating, infinite, eternal, ontological, etc.)
- Proper theological capitalization

Current section:
{section.content}

Provide enhanced version with stronger Orthodox voice."""
            
            strengthened_content = self.llm_client.generate(
                prompt=prompt,
                model=model,
                system_prompt="You are an Orthodox Christian theological scholar. Strengthen Orthodox distinctives and liturgical grounding."
            )
            
            section.content = strengthened_content
        
        return entry
