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

MANDATORY STYLE RULES - ABSOLUTE COMPLIANCE REQUIRED:

RULESET BETA: FORMATTING MANDATES
B1. PARAGRAPH INDENTATION: Every paragraph MUST be preceded by exactly four (4) spaces. NO EXCEPTIONS.
B2. EM-DASH BAN: You are BANNED from using em-dashes (—). Use conjunctions or parentheses instead.
B3. HYPHEN POLICY: Use hyphens (-) ONLY for compound words (e.g., God-Man, self-consciousness, p-adic).
B4. NUMBERS: Spell out all numbers in prose (e.g., "seven," "twenty-eight thousand").

RULESET GAMMA: LINGUISTIC MANDATES
G1. BANNED PHRASES: You are BANNED from using: "In conclusion," "To summarize," "Furthermore," "Moreover," "However," "This paper will argue," "In this essay," "On the other hand," "This is because," "It is important to note."

G2. THEOLOGICAL CAPITALIZATION (ABSOLUTE MANDATE):
Capitalize: Trinity, Father, Son, Holy Spirit, Logos, Logoi, Word, Creator, Redeemer, Savior, Incarnation, Hypostatic Union, Theotokos, Cross, Resurrection, Ascension, Parousia, Church, Eucharist, Liturgy, Divine Liturgy, Altar, Chalice, Gifts, Body, Blood, Great Entrance, Epiklesis, Anamnesis, Mysteries, Sacraments, Scripture, Gospel, Creed, Tradition, Patristic, Fathers, Council, Orthodox, Orthodoxy, Theosis, Deification, Penthos, Askesis, Nous, Kardia, Energeia, Energies, Ousia, Essence, Perichoresis, Metanoia, Hesychia, Theoria, Praxis, Apatheia, Synergy, Beauty, Truth, Wisdom, Life, Light, Source, Beginning, End, Kingdom.

G5. VOCABULARY - APOCALYPTIC MAXIMALISM:
Use vocabulary of absolute intensity: "crushing," "devastating," "unbearable," "terrible," "catastrophic," "infinite," "absolute," "eternal," "forevermore," "unavoidable," "inescapable," "ontological."

CONTENT MANDATES:
- Demonstrate deep understanding of Patristic thought and Orthodox Tradition
- Integrate theological, philosophical, scientific, and mathematical insights
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

SECTION I MANDATES (D1):
- Opening (The Hook): Begin with a specific historical moment (e.g., "In the year...", "On the night of...", "In the sheltered garden..."). Make it dramatic and poetic.
- Penthos (The Tragedy): Identify the inherent godly sorrow of the subject.
- Theophanic Rupture: Weave at least one (1) direct, liturgical address to God (e.g., "...YET did You not ordain, O Logos, that..."). Do NOT use em-dashes.

WORD COUNT: MINIMUM 1,750 words (optimal zone: 1,750-2,500 words). NO MAXIMUM. Complex topics should expand as needed.

APOCALYPTIC MAXIMALIST VOCABULARY (USE 30-50 TERMS TOTAL ACROSS ENTRY):
Intensity Adjectives: crushing, devastating, unbearable, terrible, catastrophic, infinite, absolute, eternal, forevermore, unavoidable, inescapable, ontological, primordial, ultimate, unquenchable, limitless, implacable, inexorable, relentless, immutable, ineffable, incomprehensible, unfathomable, inscrutable, transcendent, sublime, numinous, terrifying, awesome, overwhelming, shattering, cosmic, universal, totalizing, irrevocable, irreversible, consummate, supreme, paramount, preeminent, sovereign

Theological Nouns: Abyss, Mystery, Transfiguration, Judgment, Sovereignty, Sacrifice, Resurrection, Glory, Covenant, Mercy, Wrath, Justice, Holiness, Majesty, Splendor, Condescension, Kenosis, Theophany, Epiphany, Apocalypse, Eschaton, Parousia, Consummation, Fulfillment, Chasm, Void, Darkness, Radiance, Terror, Wonder, Trembling, Ecstasy, Paradox, Foundation, Cornerstone, Torrent, Deluge, Fire, Flame, Inferno

Verbs of Ultimate Action: ordain, decree, shatter, redeem, transfigure, consume, illumine, condemn, vindicate, sanctify, annihilate, obliterate, resurrect, regenerate, restore, judge, weigh, measure, discern, penetrate, rend, tear, break, crush, pulverize, exalt, magnify, glorify, enthrone, crown, cast down, abase, humble, prostrate, fell, forge, fashion, mold, pierce, transfix, heal, bind, renew, vivify

Liturgical Phrases: "from everlasting to everlasting," "unto ages of ages," "from before the foundation of the world," "world without end," "from all eternity," "blessed forevermore," "holy, holy, holy," "now and ever," "from generation to generation," "in saecula saeculorum," "alleluia"

The introduction should:
- Present the topic and its significance
- Outline why this topic matters for Orthodox theology and thought
- Preview the key themes to be explored
- Set the stage for deeper exploration

REMEMBER: Four (4) spaces before each paragraph. NO banned phrases. Capitalize all theological terms.""",
            
            "The Patristic Mind": f"""Write "The Patristic Mind" section for the topic "{topic}".

SECTION IV MANDATES (D3):
- The Method: You MUST NOT write a book report ("St. Basil wrote..."). You MUST perform a Patristic Application.
- Apply Patristic wisdom actively to the topic, showing how the Fathers' insights illuminate and transform our understanding.

WORD COUNT: MINIMUM 2,250 words (optimal zone: 2,250-3,000 words). NO MAXIMUM. Complex topics should expand as needed.

PATRISTIC CITATION REQUIREMENTS:
- Cite 5+ different Church Fathers minimum
- Name 3+ specific Patristic works
- Include Gregory of Nyssa, Maximus the Confessor, Basil the Great, Athanasius, John Chrysostom, Gregory Palamas, John of Damascus, or other major Fathers
- Integrate citations naturally (not isolated quotes)

This section should:
- Explore how the Church Fathers understood and approached this topic or related concepts
- Draw on specific Patristic sources and Traditions
- Show the continuity of Orthodox thought from ancient times
- Demonstrate the timeless Wisdom of Patristic theology
- Connect Patristic insights to the contemporary understanding of the topic

REMEMBER: Four (4) spaces before each paragraph. NO banned phrases. Capitalize all theological terms.""",
            
            "Symphony of Clashes": f"""Write "Symphony of Clashes" section for the topic "{topic}".

SECTION V MANDATES (D4):
- The Method: This is the core dialectical argument.
- For each of three (3) clashes:
  * Thesis: State the subject's idea
  * Antithesis: State the opposing idea
  * Synthesis: Demonstrate how Orthodox Theology (Theosis, Perichoresis, Hypostatic Union) is the only true synthesis that resolves the contradiction
- The Pivot: Take the most secular/abstract concept and demonstrate how its only true meaning is fulfilled in the Eucharist or other Orthodox concepts. This is NOT allegory but ontological Truth.

WORD COUNT: MINIMUM 2,350 words (optimal zone: 2,350-3,200 words). NO MAXIMUM. Complex topics should expand as needed.

This section should:
- Present the dialectical tensions and apparent contradictions related to this topic
- Explore different perspectives and schools of thought
- Show where Orthodox thought engages with or differs from other Traditions
- Examine the creative tensions that lead to deeper understanding
- Present challenges and questions in a balanced way
- Include Patristic synthesis (not purely philosophical)

REMEMBER: Four (4) spaces before each paragraph. NO banned phrases. Capitalize all theological terms.""",
            
            "Orthodox Affirmation": f"""Write "Orthodox Affirmation" section for the topic "{topic}".

WORD COUNT: MINIMUM 2,250 words (optimal zone: 2,250-3,000 words). NO MAXIMUM. Complex topics should expand as needed.

This section should:
- Clearly articulate the Orthodox Christian position on this topic
- Ground affirmations in Scripture (15+ Biblical references minimum), Tradition, and the Fathers
- Show how Orthodox theology resolves or transcends the tensions previously discussed
- Demonstrate the coherence and Beauty of the Orthodox perspective
- Connect doctrine to lived experience and practice
- Include liturgical grounding and connections to the Mysteries/Sacraments

REMEMBER: Four (4) spaces before each paragraph. NO banned phrases. Capitalize all theological terms.""",
            
            "Synthesis": f"""Write a "Synthesis" section for the topic "{topic}".

WORD COUNT: MINIMUM 1,900 words (optimal zone: 1,900-2,500 words). NO MAXIMUM. Complex topics should expand as needed.

This section should:
- Bring together the various threads explored in previous sections
- Show the integrated whole of Orthodox understanding
- Demonstrate how theology, philosophy, science, and mathematics converge
- Articulate the unified vision of Orthodox Christianity
- Point toward practical implications and applications
- Include Patristic lens throughout

REMEMBER: Four (4) spaces before each paragraph. NO banned phrases. Capitalize all theological terms.""",
            
            "Conclusion": f"""Write a conclusion for the topic "{topic}".

WORD COUNT: MINIMUM 1,800 words (optimal zone: 1,800-2,400 words). NO MAXIMUM. Complex topics should expand as needed.

The conclusion should:
- Summarize the key insights from the entry WITHOUT using banned phrases ("In conclusion," etc.)
- Reinforce the Orthodox perspective on this topic
- Point toward future directions for thought and exploration
- End with a sense of completeness while acknowledging Mystery
- Connect back to the living Tradition of the Church
- Include final Patristic Application or liturgical connection

REMEMBER: Four (4) spaces before each paragraph. NO banned phrases. NO "In conclusion" or similar banned transitions. Capitalize all theological terms."""
        }
        
        return section_prompts.get(section_name, f"Write about {section_name} for the topic '{topic}' from an Orthodox Christian perspective. Aim for 2000 words.")
