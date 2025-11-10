"""
RESEARCH QUEUE GENERATOR (V2: Importer)
=======================================
Generate research_queue.json by importing from a full Bible text.

This script is upgraded from a sample generator to a powerful importer.
It reads a specified text file from your patristics_library,
parses it using regular expressions, and builds the 'research_queue.json'
file used by the 'db_builder.py'.

Usage:
    python generate_verse_database.py

Output:
    Creates/Overwrites research_queue.json with a comprehensive verse database.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import re
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Point this to the full Bible .txt file in your library
# (Assuming 'bible_web.txt' is in the 'patristics_library' folder)
BIBLE_TEXT_FILE = Path('patristics_library/bible_web.txt') 
OUTPUT_JSON_FILE = Path('research_queue.json') # This is the file db_builder.py expects

# This regex is designed to match a common format:
# BookName Chapter:Verse Text
# e.g., "Genesis 1:1 In the beginning God created..."
# It captures (BookName) (Chapter) (Verse) (Text)
# Adjust this regex if your bible_web.txt has a different format.
VERSE_REGEX = re.compile(
    r'^([\w\s]+?)\s+(\d+):(\d+)\s+(.*)$',
    re.MULTILINE
)


class ResearchVerseImporter:
    """
    Imports verses from a full Bible text file and generates
    the research_queue.json for the db_builder.
    """

    def __init__(self, bible_path: Path, output_path: Path):
        self.bible_path = bible_path
        self.output_path = output_path
        self.verses = []

        if not self.bible_path.exists():
            logger.error(f"FATAL: Bible text file not found at: {self.bible_path}")
            logger.error("Please ensure the BIBLE_TEXT_FILE path is correct.")
            logger.error("This script expects to find 'patristics_library/bible_web.txt'")
            sys.exit(1)

    def parse_bible_text(self):
        """
        Reads the entire Bible text file and parses it using regex.
        """
        logger.info(f"Reading Bible text from {self.bible_path}...")
        try:
            content = self.bible_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Could not read file: {e}")
            return

        logger.info("Parsing verses using regex...")
        matches = VERSE_REGEX.finditer(content)
        
        count = 0
        for match in matches:
            book, chapter, verse_num, text = match.groups()
            book = book.strip()
            text = text.strip()
            
            if not text:
                continue
                
            ref = f"{book} {chapter}:{verse_num}"
            
            self.verses.append({
                "ref": ref,
                "text": text,
                "original": "",  # Placeholder, as this requires a different source
                "orthodox_trans": text, # Default to the parsed text
                "patristic": "" # Placeholder, to be filled by agent or manually
            })
            count += 1

        if count == 0:
            logger.warning("No verses were matched. The VERSE_REGEX may be incorrect.")
            logger.warning(f"Please check the format of your {self.bible_path.name} file.")
        else:
            logger.info(f"Successfully parsed {count:,} verses.")

    def add_deuterocanon_samples(self):
        """
        Adds key deuterocanonical verses not always in standard texts.
        """
        logger.info("Adding key deuterocanonical verses...")
        deuterocanon = [
            {
                "ref": "Wisdom 11:20",
                "text": "You have arranged all things by measure and number and weight",
                "original": "πάντα μέτρῳ καὶ ἀριθμῷ καὶ σταθμῷ διέταξας",
                "orthodox_trans": "You have ordered all things in measure and number and weight",
                "patristic": "Mathematical order reflects divine Logos"
            },
            {
                "ref": "Wisdom 7:17-22",
                "text": "God gave me true knowledge of what exists, to know the structure of the world",
                "original": "ἔδωκεν γάρ μοι τῶν ὄντων γνῶσιν ἀψευδῆ",
                "orthodox_trans": "He gave me unerring knowledge of things that are",
                "patristic": "Scientific knowledge is gift from divine Wisdom"
            },
            {
                "ref": "Wisdom 13:5",
                "text": "From the greatness and beauty of created things comes a corresponding perception of their Creator",
                "original": "ἐκ γὰρ μεγέθους καὶ καλλονῆς κτισμάτων ἀναλόγως ὁ γενεσιουργὸς αὐτῶν θεωρεῖται",
                "orthodox_trans": "From the greatness and beauty of created things, their Creator is seen accordingly",
                "patristic": "Natural theology via analogy, but requires nous"
            },
            {
                "ref": "Sirach 42:21",
                "text": "He has set in order the magnificent works of his wisdom",
                "original": "διεκόσμησεν τὰ μεγαλεῖα τῆς σοφίας αὐτοῦ",
                "orthodox_trans": "He has set in order the glorious works of His wisdom",
                "patristic": "Cosmic order manifests divine Sophia"
            },
            {
                "ref": "Sirach 24:3",
                "text": "I came forth from the mouth of the Most High",
                "original": "ἐγὼ ἀπὸ στόματος ὑψίστου ἐξῆлθον",
                "orthodox_trans": "I came forth from the mouth of the Most High",
                "patristic": "Wisdom personified as hypostatic reality"
            },
        ]
        
        existing_refs = {v['ref'] for v in self.verses}
        for verse in deuterocanon:
            if verse['ref'] not in existing_refs:
                self.verses.append(verse)
                
        logger.info(f"Added {len(deuterocanon)} deuterocanonical verses.")

    def generate_queue(self) -> List[Dict]:
        """Generate complete research queue"""
        logger.info("Generating full research queue from Bible text...")
        self.parse_bible_text()
        self.add_deuterocanon_samples()
        return self.verses

    def save_to_file(self):
        """Save research queue to JSON file"""
        if self.output_path.exists():
            logger.warning(f"{self.output_path} already exists!")
            response = input("Overwrite? (yes/no): ").strip().lower()
            if response != 'yes':
                logger.info("Cancelled. Keeping existing file.")
                return

        logger.info(f"Saving to {self.output_path}...")

        try:
            with open(self.output_path, 'wb') as f:
                f.write(json.dumps(self.verses, indent=2).encode('utf-8'))

            logger.info(f"✓ Saved {len(self.verses)} verses to {self.output_path.resolve()}")
            logger.info(f"  File size: {self.output_path.stat().st_size / (1024*1024):.2f} MB")
        except Exception as e:
            logger.error(f"Failed to save verse database to {self.output_path.resolve()}: {e}")

    def run(self):
        """Execute full generation"""
        logger.info("="*80)
        logger.info("RESEARCH QUEUE (VERSE DATABASE) IMPORTER (V2)")
        logger.info("="*80)
        logger.info(f"Input Bible: {self.bible_path}")
        logger.info(f"Output JSON: {self.output_path}")
        logger.info("")

        self.generate_queue()
        self.save_to_file()

        logger.info("")
        logger.info("="*80)
        logger.info("GENERATION COMPLETE")
        logger.info("="*80)
        logger.info("")
        logger.info("Next step: Run the database builder to ingest this new queue:")
        logger.info("  python db_builder.py")
        logger.info("")


def main():
    """Main entry point"""
    importer = ResearchVerseImporter(
        bible_path=BIBLE_TEXT_FILE,
        output_path=OUTPUT_JSON_FILE
    )
    importer.run()


if __name__ == "__main__":
    main()