"""
Entry generator for creating comprehensive Orthodox Christian perspective entries
"""
from typing import List, Optional
from .models import Entry, Section
from .config import Config
from .llm_client import LLMClient


class EntryGenerator:
    """Generator for comprehensive entries"""
    
    def __init__(self, config: Optional[Config] = None, llm_client: Optional[LLMClient] = None):
        """
        Initialize the entry generator
        
        Args:
            config: Configuration object (creates default if not provided)
            llm_client: LLM client (creates default if not provided)
        """
        self.config = config or Config()
        
        if llm_client:
            self.llm_client = llm_client
        else:
            llm_config = self.config.get_llm_config()
            self.llm_client = LLMClient(
                base_url=llm_config.get("base_url", "http://localhost:11434"),
                timeout=llm_config.get("timeout", 300)
            )
    
    def generate(self, topic: str, model: Optional[str] = None) -> Entry:
        """
        Generate a comprehensive entry on the given topic
        
        Args:
            topic: The topic to generate an entry for
            model: LLM model to use (uses default from config if not provided)
        
        Returns:
            Complete Entry object
        """
        if model is None:
            model = self.config.get("llm.default_model", "llama2")
        
        sections = []
        section_configs = self.config.get_section_configs()
        
        for section_config in section_configs:
            section_name = section_config["name"]
            section_content = self._generate_section(topic, section_name, model)
            sections.append(Section(name=section_name, content=section_content))
        
        entry = Entry(
            topic=topic,
            sections=sections,
            metadata={
                "model": model,
                "config_version": "0.1.0"
            }
        )
        
        return entry
    
    def _generate_section(self, topic: str, section_name: str, model: str) -> str:
        """
        Generate content for a specific section
        
        Args:
            topic: The entry topic
            section_name: The section to generate
            model: The LLM model to use
        
        Returns:
            Generated section content
        """
        system_prompt = self._get_system_prompt()
        prompt = self._build_section_prompt(topic, section_name)
        
        content = self.llm_client.generate(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt
        )
        
        return content
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are a scholar deeply versed in Orthodox Christian theology, patristics, philosophy, mathematics, and science. Your task is to write comprehensive, thoughtful entries that explore topics from an Orthodox Christian perspective.

Your writing should:
- Demonstrate deep understanding of Patristic thought and Orthodox tradition
- Integrate theological, philosophical, scientific, and mathematical insights
- Maintain academic rigor while being accessible
- Show how Orthodox Christianity engages with modern thought
- Be substantive and detailed (aim for 2000-2500 words per major section)
- Draw connections between different domains of knowledge
- Reflect the synthesis of faith and reason characteristic of Orthodox thought"""
    
    def _build_section_prompt(self, topic: str, section_name: str) -> str:
        """
        Build the prompt for generating a specific section
        
        Args:
            topic: The entry topic
            section_name: The section name
        
        Returns:
            Formatted prompt
        """
        section_prompts = {
            "Introduction": f"""Write an introduction to the topic "{topic}" from an Orthodox Christian perspective. 

The introduction should:
- Present the topic and its significance
- Outline why this topic matters for Orthodox theology and thought
- Preview the key themes to be explored
- Set the stage for deeper exploration

Aim for 1500-2000 words.""",
            
            "The Patristic Mind": f"""Write "The Patristic Mind" section for the topic "{topic}".

This section should:
- Explore how the Church Fathers understood and approached this topic or related concepts
- Draw on specific Patristic sources and traditions
- Show the continuity of Orthodox thought from ancient times
- Demonstrate the timeless wisdom of Patristic theology
- Connect Patristic insights to the contemporary understanding of the topic

Aim for 2000-2500 words with substantive theological depth.""",
            
            "Symphony of Clashes": f"""Write "Symphony of Clashes" section for the topic "{topic}".

This section should:
- Present the dialectical tensions and apparent contradictions related to this topic
- Explore different perspectives and schools of thought
- Show where Orthodox thought engages with or differs from other traditions
- Examine the creative tensions that lead to deeper understanding
- Present challenges and questions in a balanced way

Aim for 2000-2500 words that thoroughly explore these tensions.""",
            
            "Orthodox Affirmation": f"""Write "Orthodox Affirmation" section for the topic "{topic}".

This section should:
- Clearly articulate the Orthodox Christian position on this topic
- Ground affirmations in Scripture, Tradition, and the Fathers
- Show how Orthodox theology resolves or transcends the tensions previously discussed
- Demonstrate the coherence and beauty of the Orthodox perspective
- Connect doctrine to lived experience and practice

Aim for 2000-2500 words with clear theological articulation.""",
            
            "Synthesis": f"""Write a "Synthesis" section for the topic "{topic}".

This section should:
- Bring together the various threads explored in previous sections
- Show the integrated whole of Orthodox understanding
- Demonstrate how theology, philosophy, science, and mathematics converge
- Articulate the unified vision of Orthodox Christianity
- Point toward practical implications and applications

Aim for 1500-2000 words of integrative thinking.""",
            
            "Conclusion": f"""Write a conclusion for the topic "{topic}".

The conclusion should:
- Summarize the key insights from the entry
- Reinforce the Orthodox perspective on this topic
- Point toward future directions for thought and exploration
- End with a sense of completeness while acknowledging mystery
- Connect back to the living tradition of the Church

Aim for 1500-2000 words."""
        }
        
        return section_prompts.get(section_name, f"Write about {section_name} for the topic '{topic}' from an Orthodox Christian perspective. Aim for 2000 words.")
