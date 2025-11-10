"""
OPUS MAXIMUS DATABASE BUILDER (GPU-NATIVE)
==============================================
One-time database population with GPU-accelerated semantic search.

Creates and populates a persistent ChromaDB vector store with:
- Biblical verses (Semantic search)
- Patristic citations (Semantic search) - NOW INCLUDES PDFS
- Apocryphal verses (Semantic search)
- Dialectical opponents (Semantic search)

Run this ONCE before using the generator.

Author: Automated System for Orthodox Apologetics
Date: 2025-11-07
Version: GPU-NATIVE-V2 (PDF Ingestion + Semantic Chunking)
"""

import os
import sys
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict
import re

try:
    from sentence_transformers import SentenceTransformer
    from rich.console import Console
    from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn
    import orjson
    import torch
    import chromadb
    import pdfplumber  # NEW: For PDF ingestion
    import nltk        # NEW: For semantic chunking
    from nltk.tokenize import sent_tokenize
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# NEW: Download NLTK tokenizer models
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt')

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (db_builder) %(message)s',
    handlers=[
        logging.FileHandler('db_builder.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = Path('research_db_chroma')  # New path for ChromaDB
RESEARCH_QUEUE_PATH = Path('research_queue.json')
PATRISTIC_TEXTS_DIR = Path('patristic_texts') # User confirmed this is the location

# Check for CUDA and set device
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
if DEVICE == 'cpu':
    logger.warning("CUDA not available. Falling back to CPU. This will be very slow.")
    console.print("[yellow]⚠ CUDA not available. Using CPU (will be very slow)[/yellow]")
else:
    logger.info(f"CUDA available. Using device: {DEVICE} for embeddings.")
    console.print(f"[green]✓ CUDA available. Using device: {DEVICE}[/green]")


class ResearchDatabaseBuilder:
    """Handles one-time creation and population of ChromaDB vector store"""

    def __init__(self, db_path: Path):
        if db_path.exists():
            logger.warning(f"{db_path} already exists. Deleting to rebuild from scratch.")
            import shutil
            shutil.rmtree(db_path)

        # Initialize ChromaDB persistent client
        console.print("[cyan]Initializing ChromaDB persistent client...[/cyan]")
        self.client = chromadb.PersistentClient(path=str(db_path))

        # Initialize SentenceTransformer on GPU
        console.print("[cyan]Loading sentence transformer model onto GPU...[/cyan]")
        self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5', device=DEVICE)

        # Create collections
        self.patristic_collection = self.client.get_or_create_collection(
            name="patristic_citations"
        )
        self.biblical_collection = self.client.get_or_create_collection(
            name="biblical_verses"
        )
        self.apocryphal_collection = self.client.get_or_create_collection(
            name="apocryphal_verses"
        )
        self.opponent_collection = self.client.get_or_create_collection(
            name="dialectical_opponents"
        )

        console.print("[green]✓ ChromaDB and embedding model initialized[/green]")

    def _batch_generator(self, data: List, batch_size: int):
        """Generate batches for efficient GPU processing"""
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    def import_research_queue(self, queue_path: Path):
        """
        Import biblical verses from research queue JSON and add to ChromaDB
        """
        if not queue_path.exists():
            console.print(f"\n[yellow]⚠ Research queue not found: {queue_path}[/yellow]")
            console.print("\n[cyan]Options:[/cyan]")
            console.print("  1. Generate sample research_queue.json automatically")
            console.print("  2. Skip biblical verse import (database will work but with limited verses)")
            console.print("  3. Exit and create research_queue.json manually")

            choice = input("\nChoice (1/2/3): ").strip()

            if choice == '1':
                logger.info("Generating research_queue.json automatically...")
                self._generate_sample_research_queue(queue_path)
            elif choice == '2':
                logger.warning("Skipping biblical verse import")
                console.print("[yellow]Note: Semantic search will work, but biblical verse search will be limited[/yellow]")
                return
            else:
                console.print("[red]Please create research_queue.json and re-run this script[/red]")
                console.print(f"[cyan]Run: python research_queue_generator.py[/cyan]")
                sys.exit(0)

        logger.info(f"Loading research queue from {queue_path}...")
        try:
            with open(queue_path, 'rb') as f:
                queue = orjson.loads(f.read())
            console.print(f"[cyan]Loaded {len(queue)} biblical verses[/cyan]")

            batch_size = 32  # Adjust based on VRAM
            total_batches = (len(queue) + batch_size - 1) // batch_size

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Embedding Biblical Verses...", total=total_batches)

                for batch in self._batch_generator(queue, batch_size):
                    texts = [item.get('text', '') for item in batch if item.get('text')]
                    if not texts:
                        progress.advance(task)
                        continue

                    embeddings = self.embedding_model.encode(texts, convert_to_tensor=True, device=DEVICE)

                    documents = []
                    metadatas = []
                    ids = []

                    for i, item in enumerate(batch):
                        if item.get('text'):
                            documents.append(item['text'])
                            metadatas.append({
                                "reference": item.get('ref', ''),
                                "original_language": item.get('original', ''),
                                "orthodox_translation": item.get('orthodox_trans', ''),
                                "patristic_commentary": item.get('patristic', '')
                            })
                            ids.append(f"biblical_{item.get('ref', 'unknown').replace(':', '_').replace(' ', '_')}")

                    if documents:
                        self.biblical_collection.add(
                            embeddings=embeddings.cpu().numpy().tolist(),
                            documents=documents,
                            metadatas=metadatas,
                            ids=ids
                        )

                    progress.advance(task)

            console.print(f"[green]✓ Successfully embedded and stored {len(queue):,} biblical verses[/green]")

        except Exception as e:
            logger.error(f"Error importing research queue: {e}", exc_info=True)

    def _generate_sample_research_queue(self, queue_path: Path):
        """Generate minimal sample research queue if none exists"""
        logger.info("Generating sample research_queue.json...")
        try:
            from research_queue_generator import ResearchQueueGenerator
            generator = ResearchQueueGenerator(queue_path)
            generator.run()
        except ImportError:
            # Fallback minimal queue
            minimal_queue = [
                {"ref": "Genesis 1:1", "text": "In the beginning God created the heavens and the earth",
                 "original": "בְּרֵאשִׁית בָּרָא אֱלֹהִים", "orthodox_trans": "In the beginning, God created",
                 "patristic": "Basil notes temporal beginning implies creation ex nihilo"},
                {"ref": "John 1:1", "text": "In the beginning was the Word, and the Word was with God",
                 "original": "Ἐν ἀρχῇ ἦν ὁ Λόγος", "orthodox_trans": "In the beginning was the Logos",
                 "patristic": "Athanasius: Logos is eternally begotten"},
            ]
            with open(queue_path, 'w', encoding='utf-8') as f:
                json.dump(minimal_queue, f, ensure_ascii=False, indent=2)
            logger.info(f"Created minimal research_queue.json with {len(minimal_queue)} verses")

    # NEW: Helper function to extract text from any file type
    def _extract_text_from_file(self, filepath: Path) -> str:
        """Extracts raw text from .txt, .md, or .pdf files."""
        content = ""
        try:
            if filepath.suffix in ['.txt', '.md']:
                content = filepath.read_text(encoding='utf-8', errors='replace')
            elif filepath.suffix == '.pdf':
                with pdfplumber.open(filepath) as pdf:
                    all_text = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            all_text.append(page_text)
                    content = "\n".join(all_text)
            
            # Basic cleaning
            content = re.sub(r'\s+', ' ', content).strip()
            # Re-introduce paragraph breaks
            content = content.replace('  ', '\n\n') 
            
            return content
        
        except Exception as e:
            logger.error(f"Error extracting text from {filepath.name}: {e}", exc_info=True)
            return "" # Return empty string on failure

    def import_patristic_texts(self, patristic_dir: Path):
        """
        Import patristic texts, chunk, generate embeddings on GPU, and store in ChromaDB
        NOW INCLUDES PDFS AND SEMANTIC CHUNKING
        """
        if not patristic_dir.exists():
            logger.warning(f"{patristic_dir} does not exist. Creating directory...")
            patristic_dir.mkdir(parents=True)
            console.print(f"[yellow]Please add .txt, .md, or .pdf patristic text files to {patristic_dir}[/yellow]")
            return

        # UPDATED: Now globs for .pdf files as well
        text_files = list(patristic_dir.glob('*.txt')) + \
                     list(patristic_dir.glob('*.md')) + \
                     list(patristic_dir.glob('*.pdf'))
                     
        if not text_files:
            logger.warning(f"No .txt, .md, or .pdf files found in {patristic_dir}. Skipping.")
            return

        console.print(f"[cyan]Found {len(text_files)} patristic text files (including PDFs)[/cyan]")

        all_chunks_data = []  # Process in batches
        failed_files = []
        successful_count = 0

        for filepath in text_files:
            logger.info(f"Processing: {filepath.name}")
            try:
                # UPDATED: Use new extraction helper
                content = self._extract_text_from_file(filepath)
                if not content:
                    logger.warning(f"  No content extracted from {filepath.name}. Skipping.")
                    failed_files.append((filepath.name, "No content extracted"))
                    continue

                father_name, work_title = self._extract_metadata(filepath, content)
                
                # UPDATED: Use new semantic chunking function
                chunks = self._chunk_text_semantic(content, chunk_size=250, overlap_sentences=2)
                logger.info(f"  Created {len(chunks)} semantic chunks from {filepath.name}")

                for i, chunk in enumerate(chunks):
                    all_chunks_data.append({
                        "text": chunk,
                        "metadata": {
                            "father_name": father_name,
                            "work_title": work_title,
                            "citation_ref": f"{work_title} §{i+1}",
                            "topic": self._extract_topic(chunk)
                        },
                        "id": f"patristic_{filepath.stem}_{i}"
                    })

                successful_count += 1

            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}", exc_info=True)
                failed_files.append((filepath.name, str(e)))

        if not all_chunks_data:
            logger.warning("No patristic chunks generated.")
            return

        # Batch embed all chunks on GPU
        console.print(f"[cyan]Embedding {len(all_chunks_data)} patristic chunks on GPU...[/cyan]")

        batch_size = 32
        total_batches = (len(all_chunks_data) + batch_size - 1) // batch_size

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Embedding Patristic Chunks...", total=total_batches)

            for batch in self._batch_generator(all_chunks_data, batch_size):
                texts = [item['text'] for item in batch]
                embeddings = self.embedding_model.encode(texts, convert_to_tensor=True, device=DEVICE)

                self.patristic_collection.add(
                    embeddings=embeddings.cpu().numpy().tolist(),
                    documents=texts,
                    metadatas=[item['metadata'] for item in batch],
                    ids=[item['id'] for item in batch]
                )

                progress.advance(task)

        console.print(f"[green]✓ Successfully imported {len(all_chunks_data)} patristic citations[/green]")

    def _extract_metadata(self, filepath: Path, content: str) -> tuple:
        """Extract father name and work title from filename and content"""
        # Try to guess from filename (e.g., "basil_hexaemeron.txt")
        name_parts = filepath.stem.replace('_', ' ').title().split()
        father_name = ' '.join(name_parts[:2]) if len(name_parts) >= 2 else name_parts[0] if name_parts else "Unknown"
        work_title = ' '.join(name_parts[2:]) if len(name_parts) > 2 else filepath.stem

        # Try to extract from content (e.g., "# Title" or "Title\n\nby Father")
        title_match = re.search(r'^(?:#\s+)?(.+?)\n\n(?:by\s+)?(St\.|Saint)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', content, re.M | re.I)
        if title_match:
            work_title = title_match.group(1).strip()
            father_name = (title_match.group(2) or "").strip() + " " + (title_match.group(3) or "").strip()
            father_name = father_name.strip()

        return father_name, work_title

    # REPLACED: Old chunker
    # def _chunk_text(self, text: str, chunk_size: int = 300) -> List[str]:
    #     ...
        
    # NEW: Semantic chunker based on paragraphs and sentences
    def _chunk_text_semantic(self, text: str, chunk_size: int = 250, overlap_sentences: int = 2) -> List[str]:
        """
        Splits text into semantic chunks.
        1. Splits by paragraph.
        2. If paragraph is too long, splits by sentence.
        3. Re-combines sentences/paragraphs into chunks near chunk_size.
        4. Adds an overlap of sentences between chunks.
        """
        chunks = []
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        semantic_units = [] # Store paragraphs or groups of sentences
        
        # Max words for a single paragraph before splitting it
        max_para_words = int(chunk_size * 1.5) 

        for para in paragraphs:
            para = para.strip()
            if not para or para.startswith('#'):
                continue
                
            para_word_count = len(para.split())
            
            if para_word_count > max_para_words:
                # This paragraph is too long, split it into sentences
                sentences = sent_tokenize(para)
                current_sentence_chunk = []
                current_sentence_word_count = 0
                
                for sentence in sentences:
                    sentence_word_count = len(sentence.split())
                    
                    if current_sentence_word_count + sentence_word_count <= max_para_words:
                        current_sentence_chunk.append(sentence)
                        current_sentence_word_count += sentence_word_count
                    else:
                        if current_sentence_chunk:
                            semantic_units.append(" ".join(current_sentence_chunk))
                        current_sentence_chunk = [sentence]
                        current_sentence_word_count = sentence_word_count
                
                if current_sentence_chunk:
                    semantic_units.append(" ".join(current_sentence_chunk))
            
            elif para_word_count > 10: # Ignore very short paragraphs
                # Paragraph is a good semantic unit
                semantic_units.append(para)

        # Now, combine semantic units into chunks of target size
        current_chunk_words = []
        current_chunk_word_count = 0
        
        for i, unit in enumerate(semantic_units):
            unit_word_count = len(unit.split())
            
            if current_chunk_word_count + unit_word_count <= chunk_size:
                current_chunk_words.append(unit)
                current_chunk_word_count += unit_word_count
            else:
                # Finalize the current chunk
                if current_chunk_words:
                    chunks.append("\n\n".join(current_chunk_words))
                
                # Start new chunk, adding overlap
                # Overlap: Take the last semantic unit (or last few sentences)
                overlap_text = []
                if current_chunk_words:
                    last_unit_sentences = sent_tokenize(current_chunk_words[-1])
                    overlap_sentences_actual = min(len(last_unit_sentences), overlap_sentences)
                    if overlap_sentences_actual > 0:
                        overlap_text = last_unit_sentences[-overlap_sentences_actual:]
                
                current_chunk_words = overlap_text + [unit]
                current_chunk_word_count = len(" ".join(current_chunk_words).split())

        if current_chunk_words:
            chunks.append("\n\n".join(current_chunk_words))

        return chunks

    def _extract_topic(self, chunk: str) -> str:
        """Extract primary topic from chunk text"""
        topics = {
            'creation': ['creation', 'genesis', 'beginning', 'cosmos', 'made'],
            'incarnation': ['incarnation', 'christ', 'incarnate', 'word became flesh', 'logos'],
            'trinity': ['trinity', 'father', 'son', 'spirit', 'triune', 'homoousios'],
            'theosis': ['theosis', 'deification', 'divinization', 'become god'],
            'liturgy': ['liturgy', 'eucharist', 'sacrament', 'worship', 'altar', 'mysteries'],
            'scripture': ['scripture', 'gospel', 'bible', 'revelation', 'prophet'],
            'anthropology': ['man', 'human', 'soul', 'person', 'nature', 'nous', 'kardia'],
            'epistemology': ['knowledge', 'nous', 'reason', 'intellect', 'perceive'],
            'soteriology': ['salvation', 'redemption', 'atonement', 'cross', 'saved'],
            'ecclesiology': ['church', 'ekklesia', 'body', 'assembly', 'bishop'],
            'asceticism': ['ascetic', 'prayer', 'fasting', 'hesychia', 'apatheia', 'passion']
        }

        chunk_lower = chunk.lower()
        topic_counts = defaultdict(int)
        for topic, keywords in topics.items():
            for kw in keywords:
                if kw in chunk_lower:
                    topic_counts[topic] += 1

        if not topic_counts:
            return 'general'
        
        # Return the topic with the most keyword hits
        return max(topic_counts, key=topic_counts.get)

    def populate_apocryphal_verses(self):
        """Populate apocryphal verses and embed them"""
        console.print("[cyan]Populating and embedding apocryphal verses...[/cyan]")

        apocryphal_verses = [
            ('Wisdom 11:20', 'You have arranged all things by measure and number and weight', 'mathematics creation'),
            ('Wisdom 7:17-22', 'God gave me unerring knowledge of what exists, to know the structure of the world', 'science knowledge'),
            ('Wisdom 13:5', 'From the greatness and beauty of created things comes a corresponding perception of their Creator', 'natural_theology'),
            ('Sirach 42:21', 'He has set in order the magnificent works of his wisdom', 'cosmic_order'),
            ('Sirach 24:3', 'I came forth from the mouth of the Most High', 'wisdom_personified'),
            ('2 Esdras 7:30', 'Then the earth shall give up those who sleep in it', 'eschatology'),
            ('Tobit 12:12', 'I am Raphael, one of the seven holy angels', 'angelology'),
            ('Baruch 3:37', 'Afterwards he appeared on earth and lived with humankind', 'incarnation'),
            ('Wisdom 7:25-26', 'She is a breath of the power of God, a pure emanation of the glory of the Almighty', 'sophia divine'),
            ('Sirach 1:4', 'Wisdom was created before all other things', 'sophia preexistence'),
        ]

        texts = [v[1] for v in apocryphal_verses]
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=True, device=DEVICE)

        self.apocryphal_collection.add(
            embeddings=embeddings.cpu().numpy().tolist(),
            documents=texts,
            metadatas=[{"reference": v[0], "theme": v[2]} for v in apocryphal_verses],
            ids=[f"apocryphal_{v[0].replace(' ', '_').replace(':', '_')}" for v in apocryphal_verses]
        )

        console.print(f"[green]✓ Populated {len(apocryphal_verses)} apocryphal verses[/green]")

    def populate_dialectical_opponents(self):
        """Populate dialectical opponents and embed their key positions"""
        console.print("[cyan]Populating and embedding dialectical opponents...[/cyan]")

        opponents = [
            ('Richard Dawkins', 'Darwin Mendel Pascal', 'critic', ['selfish gene', 'blind watchmaker', 'God delusion'], 'Epistemological'),
            ('Daniel Dennett', 'Darwin Mendel', 'reductionist', ['Darwins dangerous idea', 'consciousness explained'], 'Anthropological'),
            ('Sam Harris', 'Pascal', 'critic', ['End of faith', 'moral landscape', 'free will skeptic'], 'Epistemological'),
            ('Friedrich Nietzsche', 'Pascal Kierkegaard', 'critic', ['God is dead', 'will to power', 'ubermensch'], 'Existential'),
            ('Bertrand Russell', 'Anselm Aquinas', 'critic', ['Why I am not a Christian', 'logical positivism'], 'Logical'),
            ('David Hume', 'Anselm Aquinas', 'skeptic', ['miracles impossible', 'problem of induction'], 'Epistemological'),
            ('Karl Marx', 'Pascal', 'materialist', ['religion as opium', 'historical materialism'], 'Sociological'),
            ('Sigmund Freud', 'Pascal', 'reductionist', ['illusion of religion', 'Oedipus complex'], 'Psychological'),
        ]

        # Embed the key positions
        texts = [f"{o[0]}: {', '.join(o[3])}" for o in opponents]
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=True, device=DEVICE)

        self.opponent_collection.add(
            embeddings=embeddings.cpu().numpy().tolist(),
            documents=texts,
            metadatas=[{
                "opponent_name": o[0],
                "primary_subject": o[1],
                "relation_type": o[2],
                "key_positions": json.dumps(o[3]),  # Store as JSON string
                "category": o[4]
            } for o in opponents],
            ids=[f"opponent_{o[0].replace(' ', '_')}" for o in opponents]
        )

        console.print(f"[green]✓ Populated {len(opponents)} dialectical opponents[/green]")

    def build_database(self):
        """Execute full database build"""
        console.print("\n" + "="*80)
        console.print("[bold cyan]OPUS MAXIMUS GPU DATABASE BUILDER (V2)[/bold cyan]")
        console.print("="*80 + "\n")

        self.import_research_queue(RESEARCH_QUEUE_PATH)
        self.import_patristic_texts(PATRISTIC_TEXTS_DIR)
        self.populate_apocryphal_verses()
        self.populate_dialectical_opponents()

        console.print("\n" + "="*80)
        console.print("[bold green]DATABASE BUILD COMPLETE[/bold green]")
        console.print("="*80 + "\n")
        self._print_statistics()

    def _print_statistics(self):
        """Print database statistics"""
        console.print(f"[cyan]ChromaDB Statistics:[/cyan]")
        console.print(f"  Database path: {DB_PATH}")
        console.print(f"  Patristic citations:   {self.patristic_collection.count():,}")
        console.print(f"  Biblical verses:       {self.biblical_collection.count():,}")
        console.print(f"  Apocryphal verses:     {self.apocryphal_collection.count():,}")
        console.print(f"  Dialectical opponents: {self.opponent_collection.count():,}")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("  1. Download a GGUF model for local inference")
        console.print("  2. Place model in ./models/ directory")
        console.print("  3. Run: streamlit run dashboard.py")
        console.print("     OR")
        console.print("  4. Run: python run_codex_generation.py --model-path <path/to/model.gguf>")


def main():
    builder = ResearchDatabaseBuilder(DB_PATH)
    builder.build_database()


if __name__ == "__main__":
    main()