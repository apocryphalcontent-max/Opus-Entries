# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- (Optional) Ollama or compatible local LLM service

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/apocryphalcontent-max/Opus-Entries.git
cd Opus-Entries
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up Ollama for LLM generation:
```bash
# Install Ollama from https://ollama.ai
# Pull a model (e.g., llama2)
ollama pull llama2
```

## Configuration

The system uses `config.json` for configuration. Key settings include:

- **LLM Configuration**: Model selection and API endpoint
- **Entry Parameters**: Word count ranges and section definitions  
- **Quality Tiers**: Score thresholds for tier assignment
- **Validation Weights**: How different aspects are weighted in scoring

You can customize these settings by editing `config.json`.

## Verifying Installation

Run the test suite:
```bash
python tests/test_opus_entries.py
```

All tests should pass with ✓ marks.

## Usage

Generate your first entry:
```bash
python -m opus_entries.cli generate --topic "Your Topic Here"
```

The entry will be saved in the `output/` directory.

## Troubleshooting

### LLM Service Not Available
If you see "Warning: LLM service not available", the system will use fallback mode with placeholder content. To get full functionality:

1. Install Ollama from https://ollama.ai
2. Start the Ollama service
3. Pull a model: `ollama pull llama2`
4. Run the generate command again

### Import Errors
Make sure you're running commands from the repository root directory and have installed all dependencies.

### Permission Errors
If you get permission errors when installing packages, try:
```bash
pip install --user -r requirements.txt
```
