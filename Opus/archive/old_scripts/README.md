OPUS MAXIMUS MASTER GENERATOR (GPU-NATIVE)

Date: 2025-11-07
Status: GPU-Native Agentic Architecture
Target Hardware: NVIDIA RTX 3090/4090 (16GB+ VRAM)

I. PROJECT AMBITION & OVERVIEW

This is the Ultimate Fully Automated Apocalyptic Hexaemeron Generation System.

Its ambition is to be a fully autonomous engine that researches, selects, and generates a 12,000-entry codex. It uses a local LLM to conduct critical thinking and automate the entire process, selecting one entry after another based on a set standard of criteria (e.g., priority tiers from generate_entry_queue.py) until all spots are populated.

The output must be of the "golden" corpus quality, adhering to the non-negotiable Absolute Rulesets specified in this document.

System Architecture

The architecture is a closed-loop, GPU-native agentic foundry.

[Master Orchestrator (run_codex_generation.py - PLANNED)]
    1. Selects next entry from 12,000-entry queue
    2. Invokes OpusMaximusAgenticGenerator
    3. Receives (Success/Failure) -> Logs -> Repeats
              |
              V
[OpusMaximusAgenticGenerator (opus_maximus_master_generator.py)]
    (LangGraph State Machine)
    1.  -> Generate Blueprint (Queries Research DB)
    2.  -> Generate Section 1 (I. Strategic Role)
    3.  -> Validate Section 1 (Rules B, G)
        |    (Loop 3x on fail) -> Correct Section
    4.  -> Generate Section 2 (II. Classification)
    5.  -> Validate Section 2
        |    ... (Loop for all 6 sections) ...
    6.  -> Assemble Entry
    7.  -> Validate Full Entry (Rules A, D, Uniqueness)
        |    (Loop on fail) -> Expand Entry (if word count low)
    8.  -> (SUCCESS) -> Save to GENERATED_ENTRIES_MASTER
              |
              V
[Supporting Subsystems (GPU-Accelerated)]
    - LLM: `llama-cpp-python` (Local GGUF Model)
    - "Brain": `ChromaDB` (Patristic Library Embeddings)
    - "Memory": `faiss-gpu` (Uniqueness Check)
    - "Eye": `Streamlit` (Dashboard for Monitoring)


This architecture provides a ~5-10x speedup over the previous API-based model, eliminates network latency, and enables a robust, self-correcting generation loop.

II. ABSOLUTE RULESETS (The "Voice")

This system's output is defined by a non-negotiable set of rules. The agentic generator (opus_maximus_master_generator.py) is designed to self-correct until its output validates against these rules.

RULESET ALPHA: Structural Mandates

A1. Six-Section Structure (MANDATORY)
Every entry MUST contain exactly six sections:

I. Strategic Role: Why this subject matters for Orthodox apologetics.

II. Classification: Preparatory/Orthodox/Adversarial designation.

III. Primary Works: 3-4 actual works with bibliographic data.

IV. The Patristic Mind: 3 Church Fathers engaging the subject.

V. Symphony of Clashes: 3 dialectical engagements.

VI. Orthodox Affirmation: Eucharistic culmination + doxological cascade.

A2. Word Count Requirements (MANDATORY)

Minimum: 10,000 words

Target: 12,000-15,000 words

Implementation Note: This mandate MUST be added to the LangGraph validation loop in opus_maximus_master_generator.py as a final check after assemble_entry.

RULESET BETA: Formatting Mandates

B1. Four-Space Paragraph Indentation (ABSOLUTE)
Every paragraph MUST begin with exactly 4 spaces. No exceptions.

B2. Em-Dash Ban (ABSOLUTE)
The em-dash (—) is BANNED. It is a visual break that interrupts the "doxological chaining" (see G4). Use grammatical workarounds (e.g., parentheses, commas, or rephrasing).

B3. Hyphen Policy (CONDITIONAL)
Hyphens allowed ONLY for compound words (e.g., self-consciousness, God-Man, p-adic, twenty-four, first-century).

B4. Numbers in Prose
Spell out ALL numbers (e.g., "seven," "five hundred," "twenty-eight thousand"). Exception: Dates (e.g., "In the year 2012...") and direct bibliographic citations.

B5. Banned Academic Prose
These transitions are BANNED as they are weak and break the liturgical rhythm: "In conclusion," "Furthermore," "Moreover," "However," "This paper argues," "On the other hand."

RULESET GAMMA: Linguistic Mandates

G1. Liturgical Conjunctions (MANDATORY CAPITALIZATION)
AND, YET, BUT must be capitalized when used structurally. This is not for emphasis, but to serve as the "joints" for doxological chaining, linking vast clauses into a single, breathless theological sentence.

G2. Theological Capitalization
These terms MUST be capitalized as they refer to ultimate realities, not mere concepts.

Godhead: Trinity, Father, Son, Holy Spirit, Logos, Creator, Savior

Christology: Incarnation, Hypostatic Union, Theotokos, Cross, Resurrection

Ecclesiology: Church, Eucharist, Liturgy, Altar, Chalice, Body, Blood

Soteriology: Theosis, Penthos, Nous, Kardia, Energeia, Metanoia

Core Concepts: Beauty, Truth, Wisdom, Life, Light, Source, Kingdom

G3. NOT...BUT Engine (MANDATORY)
This is the primary dialectical engine of the system. Arguments must be built via "NOT...BUT" structures to correct a surface-level understanding and reveal a deeper, Orthodox truth.

Example: "NOT as observer of ancient battlefield BUT as witness to Israel's condition..."

Example: "NOT in its function as consolation BUT in its character as lynchpin..."

G4. Sentence Algorithm ("Doxological Chaining") (MANDATORY)
Sentences MUST be extremely long and complex, ideally 40+ words on average. They follow a chaining algorithm:
[clause] AND [clause] YET [transcendent clause] BUT [ultimate truth] because [theological ground] AND [further development]...

G5. Theological Term Density (MANDATORY)
MUST use 3+ theological terms (Greek, Syriac, Hebrew) per paragraph to ensure theological saturation.

Greek (Core): nous, kardia, logoi, Logos, theosis, energeia, ousia, nepsis, hesychia, phos, penthos, ekklesia, perichoresis, hypostasis, metanoia, anamnesis, epiklesis.

Syriac (Selective): qnoma, ihidayutha, madbha, ruha, memra, shekhinah, raza.

Hebrew (Selective): kavod, hokmah, ruach, dabar, hesed, emet, shalom.

RULESET DELTA: Content Mandates

D1. Section I (Strategic Role): Must begin with a specific, evocative opening pattern:

Historical Moment: "In the year two thousand twelve..." (e.g., Peter Scholze)

Conceptual Crisis: "In the valley where bones lay scattered..." (e.g., Resurrection of the Dead)

Personal Encounter: "On the night of November 23, 1654..." (e.g., Blaise Pascal)

D2. Section IV (Patristic Mind):

MUST engage three distinct Church Fathers.

MUST cite specific (real or semantically generated) works.

MUST be an engagement (applying their thought), not a book report.

D3. Section V (Symphony of Clashes):

MUST feature three dialectical engagements.

MUST follow the Thesis, Antithesis, Orthodox Synthesis structure.

D4. Section VI (Orthodox Affirmation):

1. Opening Prayer: First paragraph MUST be a liturgical invocation (e.g., "—O Christ our God...").

2. Eucharistic Culmination: MUST contain the exact trigger phrase: "AND NOW, in this Liturgy, at this Altar..."

3. Doxological Cascade: The final paragraph MUST be a single, overwhelmingly long sentence using the "From...to..." transfiguration structure (e.g., "From monastery garden to paradise regained...").

III. INSTALLATION (GPU-NATIVE)

System Requirements:

NVIDIA GPU: RTX 3090, RTX 4090, or better (16GB+ VRAM recommended)

CUDA: 11.8 or 12.x

Python: 3.9, 3.10, or 3.11

RAM: 32GB system RAM

Step 1: Install PyTorch with CUDA

# This command is for CUDA 11.8. Adjust if you use a different version.
pip install torch==2.0.1+cu118 --extra-index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)


Verify:

python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
# Should print: CUDA Available: True


Step 2: Install llama-cpp-python with CUDA

This is the most critical step.

Windows (Recommended - Pre-built wheel):

pip install llama-cpp-python --prefer-binary --extra-index-url=[https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu118](https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu118)


Linux:

CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python==0.2.27


Verify:

python -c "from llama_cpp import Llama; print('llama-cpp-python OK')"


Step 3: Install Remaining Dependencies

pip install -r requirements.txt


Verify FAISS GPU:

python -c "import faiss; print(f'FAISS GPU: {hasattr(faiss, \"GpuIndexFlatIP\")}')"
# Should print: FAISS GPU: True


Step 4: Download a GGUF Model

Create a directory named models/ in the root of the project. Download a GGUF model and place it inside.

Recommended Models for RTX 4090 (24GB VRAM):

Qwen2.5-Coder-14B-Instruct Q8 (~15GB) - Fast and fits comfortably.

Qwen2.5-Coder-32B-Instruct Q4 (~18GB) - Balanced quality/speed.

Llama-3.1-70B-Instruct Q4 (~40GB) - Highest quality, but will require CPU offloading.

IV. USAGE

Step 1: Build the Research Database (Run Once)

Place all your patristic texts (.txt, .md, and .pdf files) into the patristics_library/ folder.
Then, run the database builder:

python db_builder.py


This will:

Find all texts in patristics_library/ (Note: You must add PDF support to db_builder.py to ingest .pdf files).

Find research_queue.json (or generate a sample).

Generate GPU-accelerated embeddings for all texts.

Create the persistent research_db_chroma/ vector database.

Step 2: Run the Command Center (Recommended)

The easiest way to run the system is via the Streamlit dashboard.

streamlit run dashboard.py


Access at: http://localhost:8501

From the dashboard, you can:

Select your GGUF model.

Set the number of GPU layers to offload (-1 for all).

Generate single entries.

Launch batch generations.

Monitor logs in real-time.

View, read, and download completed entries.

Step 3: Run from Command-Line (Advanced)

Single Entry:

python opus_maximus_master_generator.py \
    --mode single \
    --subject "The Book of Revelation" \
    --tier S+ \
    --category Biblical \
    --model-path ./models/Qwen2.5-Coder-14B-Instruct-Q8.gguf


Batch:

python opus_maximus_master_generator.py \
    --mode batch \
    --batch-file sample_batch.json \
    --model-path ./models/Qwen2.5-Coder-14B-Instruct-Q8.gguf


V. KEY PROJECT FILES

README.md: (This file) The single, correct source of truth.

opus_maximus_master_generator.py: (The Worker) The core LangGraph agentic generator. Builds a single entry.

db_builder.py: (The Librarian) The setup script for the ChromaDB vector database. Run this once and anytime you add new patristic texts.

dashboard.py: (The Cockpit) The Streamlit web UI for launching and monitoring the generator.

requirements.txt: The correct list of Python dependencies for the GPU-native stack.

generate_entry_queue.py: (The 12,000-Entry Plan) Utility to create the master generation plan.

patristics_library/: (The "Brain") Folder containing all .txt, .md, and .pdf files of the Church Fathers. This is the engine's knowledge.

OPUS_MAXIMUS_INDIVIDUALIZED/: (The "Soul") Folder containing the "golden" corpus entries that define the target quality and "voice."

research_db_chroma/: (Generated Folder) The persistent ChromaDB vector database.

GENERATED_ENTRIES_MASTER/: (Generated Folder) The final output directory for all approved entries.

VI. AGENTIC WORKFLOW (LangGraph)

The opus_maximus_master_generator.py script is not a simple script; it is a LangGraph state machine. This is how it thinks:

generate_blueprint: Creates the 6-section plan. Critically, it performs a semantic search on the core_thesis to find relevant patristic citations before writing begins.

generate_section: Generates one section at a time (e.g., "I. Strategic Role"). It injects the specific research (citations, verses) relevant only to that section.

validate_section: Checks the output of the single section against Ruleset BETA (4-space indent, no em-dashes) and Ruleset GAMMA (Capitalization, NOT...BUT).

decide_after_validation:

If FAIL: Routes to correct_section.

If PASS: Routes to advance_section.

If FAIL (3x): Aborts the entire entry.

correct_section: (The self-correction loop) The agent is re-invoked with a new prompt, telling it exactly which rules it broke (e.g., "You used an em-dash. Rewrite this section without it.") It then routes back to validate_section.

advance_section: Approves the section, adds it to the list, and loops back to generate_section for the next section.

assemble_entry: (After Section VI passes) Stitches all 6 approved sections into one file.

END: The entry is complete.
(Note: A future step, validate_total_word_count, is needed here to meet Rule A2).

VII. SEMANTIC RESEARCH SYSTEM

This is the "critical thinking" component. The engine does not just write; it researches.

Blueprint Thesis: The agent first generates a core_thesis for the subject (e.g., "For Gregor Mendel, the monastery garden was a temple where discovering the logoi of genetics became a liturgical act.").

Semantic Embedding: This thesis is converted into a vector embedding by sentence-transformers.

Vector Search: The agent queries the ChromaDB (research_db_chroma/) to find the top 10 most semantically similar chunks from the patristics_library/.

Intelligent Injection:

It will find matches for "monastery," "garden," "temple," and "logoi."

It will retrieve chunks from St. Maximus the Confessor (on logoi), St. Basil the Great (on creation/gardens), etc.

These specific citations are then injected directly into the prompt for Section IV: The Patristic Mind, ensuring the patristic engagement is deeply relevant and not generic.

VIII. TROUBLESHOOTING

Issue: CUDA Not Available

Symptom: CUDA not available. Falling back to CPU.

Solution: Your PyTorch installation does not match your CUDA version. Reinstall PyTorch using the exact command from Step 1.

Issue: llama-cpp-python Not Using GPU

Symptom: Model loads, but inference is extremely slow (10+ seconds per response).

Solution: The llama-cpp-python build did not include CUDA support. Reinstall it using the exact command from Step 2.

Issue: Out of VRAM

Symptom: CUDA error: out of memory

Solution:

Use a smaller GGUF model (e.g., 14B instead of 32B).

Use a model with smaller quantization (e.g., Q4 instead of Q8).

In dashboard.py or on the command line, reduce n_gpu_layers (e.g., to 30 instead of -1) to offload some layers to system RAM.

Issue: ChromaDB Permission Error

Symptom: PermissionError: [Errno 13] Permission denied: 'research_db_chroma'

Solution: Delete the research_db_chroma/ directory and re-run python db_builder.py.

Glory to God for all things.