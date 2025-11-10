"""
OPUS MAXIMUS - COMMAND CENTER
===============================
A Streamlit web dashboard to launch and monitor
the Opus Maximus Agentic Generator.

Usage:
    streamlit run dashboard.py

Author: Automated System for Orthodox Apologetics
Date: 2025-11-07
Version: GPU-NATIVE
"""

import streamlit as st
import subprocess
import os
from pathlib import Path
import sys
import time

# --- Configuration ---
GENERATOR_SCRIPT = "opus_maximus_master_generator.py"
OUTPUT_DIR = "GENERATED_ENTRIES_MASTER"
MODEL_DIR = "./models"  # Assumes models are in a './models' subdirectory

# --- Page Setup ---
st.set_page_config(
    page_title="Opus Maximus Command Center",
    page_icon="☦️",
    layout="wide"
)

st.title("☦️ Opus Maximus Command Center")
st.caption("The Ultimate Fully Automated Apocalyptic Hexaemeron Generation System (GPU-Native)")

# --- Sidebar: System Info ---
st.sidebar.header("⚙️ System Information")

try:
    import torch
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        st.sidebar.success(f"✅ CUDA Available")
        st.sidebar.info(f"**GPU**: {gpu_name}")
        st.sidebar.info(f"**VRAM**: {gpu_memory:.1f} GB")
    else:
        st.sidebar.error("❌ CUDA Not Available")
        st.sidebar.warning("Generation will be VERY slow on CPU")
except ImportError:
    st.sidebar.warning("⚠️ PyTorch not installed")

# --- Model Selection ---
st.sidebar.header("🤖 Model Configuration")

if not Path(MODEL_DIR).exists():
    st.sidebar.error(f"Model directory not found: {MODEL_DIR}")
    st.sidebar.info(f"Please create a '{MODEL_DIR}' directory and place your .gguf models inside it.")
    Path(MODEL_DIR).mkdir(exist_ok=True, parents=True)
    st.stop()

models = list(Path(MODEL_DIR).glob("*.gguf"))
if not models:
    st.sidebar.error(f"No .gguf models found in {MODEL_DIR}")
    st.sidebar.info("Please download a GGUF model and place it in the './models' folder.")
    st.sidebar.markdown("""
    **Recommended for RTX 4090:**
    - Qwen2.5-Coder-14B-Instruct Q8 (~15GB)
    - Qwen2.5-Coder-32B-Instruct Q4 (~18GB)

    Download from Hugging Face: https://huggingface.co/models?search=gguf
    """)
    st.stop()

model_names = [m.name for m in models]
selected_model = st.sidebar.selectbox("Select GGUF Model", model_names)
model_path = Path(MODEL_DIR) / selected_model

# Model info
if selected_model:
    model_size = (Path(MODEL_DIR) / selected_model).stat().st_size / (1024**3)
    st.sidebar.info(f"**Size**: {model_size:.1f} GB")

# GPU layers configuration
n_gpu_layers = st.sidebar.number_input(
    "GPU Layers (n_gpu_layers)",
    min_value=-1,
    max_value=100,
    value=-1,
    help="Number of layers to offload to GPU. -1 for all layers, 0 for none."
)

# Context window
n_ctx = st.sidebar.selectbox(
    "Context Window",
    [4096, 8192, 16384],
    index=1,
    help="Maximum context length for the model"
)

# --- Main Content ---
st.header("🚀 Launch New Generation")

# Tab layout
tab1, tab2, tab3 = st.tabs(["Single Entry", "Batch Generation", "View Entries"])

# --- Tab 1: Single Entry ---
with tab1:
    with st.form(key="generation_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            subject = st.text_input("Subject", "The Book of Revelation")
        with col2:
            tier = st.selectbox("Tier", ["S+", "S", "A", "B", "C"], index=0)
        with col3:
            category = st.selectbox("Category", [
                "Biblical", "Patristic", "Theology", "Mathematics",
                "Physics", "Philosophy", "Science", "Literature", "History"
            ], index=0)

        submit_button = st.form_submit_button(label="🔥 Generate Single Opus")

        if submit_button:
            if not subject.strip():
                st.error("Please enter a subject")
            else:
                st.info(f"Starting single generation for: **{subject}** (Tier {tier})")

                # Build command
                command = [
                    sys.executable,
                    GENERATOR_SCRIPT,
                    "--mode", "single",
                    "--subject", subject,
                    "--tier", tier,
                    "--category", category,
                    "--model-path", str(model_path),
                    "--n-gpu-layers", str(n_gpu_layers),
                    "--n-ctx", str(n_ctx)
                ]

                # Show command
                with st.expander("View Command"):
                    st.code(" ".join(command), language="bash")

                # Execute
                log_container = st.empty()
                log_text = ""

                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        bufsize=1
                    )

                    # Stream output
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            log_text += line
                            log_container.code(log_text, language="bash")

                    process.stdout.close()
                    process.wait()

                    if process.returncode == 0:
                        st.success(f"✅ Generation for '{subject}' completed successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ Generation failed. Return Code: {process.returncode}")

                except FileNotFoundError:
                    st.error(f"Error: The script '{GENERATOR_SCRIPT}' was not found.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

# --- Tab 2: Batch Generation ---
with tab2:
    st.markdown("### Batch Generation")

    batch_file = st.file_uploader("Upload Batch JSON File", type=["json"])

    if batch_file is not None:
        import json
        batch_data = json.load(batch_file)
        st.write(f"Loaded {len(batch_data)} entries")
        st.json(batch_data[:3])  # Show first 3

        if st.button("🚀 Start Batch Generation"):
            # Save uploaded file
            batch_path = Path("temp_batch.json")
            with open(batch_path, 'w') as f:
                json.dump(batch_data, f, indent=2)

            command = [
                sys.executable,
                GENERATOR_SCRIPT,
                "--mode", "batch",
                "--batch-file", str(batch_path),
                "--model-path", str(model_path),
                "--n-gpu-layers", str(n_gpu_layers),
                "--n-ctx", str(n_ctx)
            ]

            st.info(f"Starting batch generation for {len(batch_data)} entries...")

            log_container = st.empty()
            log_text = ""

            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1
                )

                for line in iter(process.stdout.readline, ''):
                    if line:
                        log_text += line
                        log_container.code(log_text, language="bash")

                process.stdout.close()
                process.wait()

                if process.returncode == 0:
                    st.success("✅ Batch generation completed!")
                    st.balloons()
                else:
                    st.error(f"❌ Batch generation failed. Return Code: {process.returncode}")

            except Exception as e:
                st.error(f"Error: {e}")

# --- Tab 3: View Entries ---
with tab3:
    st.markdown("### Generated Entries")

    # Ensure output directory exists
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    try:
        entry_files = list(Path(OUTPUT_DIR).rglob("*.md"))
    except Exception as e:
        st.error(f"Error scanning output directory: {e}")
        entry_files = []

    if not entry_files:
        st.info("No entries generated yet.")
    else:
        # Sort by modification time to show newest first
        try:
            entry_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            entry_names = [f"{f.parent.name} / {f.name}" for f in entry_files]

            selected_entry_display = st.selectbox(
                "Select Entry to View",
                entry_names
            )

            if selected_entry_display:
                # Find the corresponding file path
                selected_index = entry_names.index(selected_entry_display)
                entry_path = entry_files[selected_index]

                st.divider()
                st.subheader(f"📖 {entry_path.parent.name} / {entry_path.name}")

                try:
                    content = entry_path.read_text(encoding='utf-8')

                    # Show metadata if available
                    metadata_path = entry_path.with_suffix('.json')
                    if metadata_path.exists():
                        with st.expander("View Metadata"):
                            import json
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            st.json(metadata)

                    # Show content
                    st.markdown(content)

                    # Download button
                    st.download_button(
                        label="⬇️ Download Entry",
                        data=content,
                        file_name=entry_path.name,
                        mime="text/markdown"
                    )

                except Exception as e:
                    st.error(f"Could not read file: {e}")

        except Exception as e:
            st.error(f"Error sorting or displaying files: {e}")

# --- Footer ---
st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Opus Maximus GPU-Native**

*Version*: 2025-11-07
*Architecture*: LangGraph + ChromaDB + llama-cpp-python
*Designed for*: NVIDIA RTX 4090

**Glory to God for all things.**
""")

# --- Database Status ---
st.sidebar.header("📊 Database Status")
chroma_db_path = Path("research_db_chroma")
if chroma_db_path.exists():
    st.sidebar.success("✅ ChromaDB found")
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(chroma_db_path))
        collections = client.list_collections()
        st.sidebar.info(f"**Collections**: {len(collections)}")
        for col in collections:
            st.sidebar.text(f"  • {col.name}: {col.count()}")
    except Exception as e:
        st.sidebar.warning(f"⚠️ Could not read DB: {e}")
else:
    st.sidebar.error("❌ ChromaDB not found")
    st.sidebar.warning("Run: python db_builder.py")
