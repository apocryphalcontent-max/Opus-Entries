#!/bin/bash
#
# OPUS MAXIMUS - Production Setup Script
# ======================================
# Automated setup for the best local LLM stack
#

set -e  # Exit on error

echo "============================================================================"
echo "OPUS MAXIMUS - Production Setup"
echo "============================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

print_section() {
    echo ""
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_warning "$1 is not installed"
        return 1
    fi
}

# ============================================================================
# STEP 1: Check Prerequisites
# ============================================================================

print_section "Step 1: Checking Prerequisites"

# Check Python
if ! check_command python3; then
    print_error "Python 3 is required. Install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python version: $PYTHON_VERSION"

# Check pip
if ! check_command pip3; then
    print_error "pip3 is required"
    exit 1
fi

# Check CUDA (optional but recommended)
if check_command nvcc; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $5}' | cut -d',' -f1)
    print_success "CUDA version: $CUDA_VERSION"
    HAS_CUDA=1
else
    print_warning "CUDA not found. GPU acceleration will not be available."
    print_warning "For best performance, install CUDA toolkit from:"
    print_warning "https://developer.nvidia.com/cuda-downloads"
    HAS_CUDA=0
fi

# Check GPU
if check_command nvidia-smi; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)
    print_success "GPU: $GPU_INFO"
else
    print_warning "No NVIDIA GPU detected. Using CPU mode."
fi

# Check disk space
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
print_success "Available disk space: ${AVAILABLE_SPACE}GB"

if [ "$AVAILABLE_SPACE" -lt 100 ]; then
    print_warning "Low disk space. Recommended: 100GB+ for models and cache"
fi

# ============================================================================
# STEP 2: Create Virtual Environment
# ============================================================================

print_section "Step 2: Setting Up Virtual Environment"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_success "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_success "pip upgraded"

# ============================================================================
# STEP 3: Install Core Dependencies
# ============================================================================

print_section "Step 3: Installing Core Dependencies"

print_success "Installing base requirements..."
pip install -r requirements.txt

print_success "Core dependencies installed"

# ============================================================================
# STEP 4: Install LLM Backends
# ============================================================================

print_section "Step 4: Installing LLM Backends"

# Ask which backends to install
echo "Which backends would you like to install?"
echo ""
echo "  1. llama.cpp (Universal, CPU/GPU)"
echo "  2. vLLM (Fastest, GPU only) ⭐ RECOMMENDED"
echo "  3. ExLlamaV2 (VRAM efficient, GPU only)"
echo "  4. SGLang (Structured generation, GPU only)"
echo "  5. ALL (Install everything)"
echo ""
read -p "Enter choice (1-5) [2]: " BACKEND_CHOICE
BACKEND_CHOICE=${BACKEND_CHOICE:-2}

install_llamacpp=0
install_vllm=0
install_exllama=0
install_sglang=0

case $BACKEND_CHOICE in
    1) install_llamacpp=1 ;;
    2) install_vllm=1 ;;
    3) install_exllama=1 ;;
    4) install_sglang=1 ;;
    5) install_llamacpp=1; install_vllm=1; install_exllama=1; install_sglang=1 ;;
    *) print_error "Invalid choice"; exit 1 ;;
esac

# Install llama.cpp
if [ $install_llamacpp -eq 1 ]; then
    print_success "Installing llama.cpp..."

    if [ $HAS_CUDA -eq 1 ]; then
        CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
    else
        pip install llama-cpp-python
    fi

    print_success "llama.cpp installed"
fi

# Install vLLM
if [ $install_vllm -eq 1 ]; then
    if [ $HAS_CUDA -eq 0 ]; then
        print_warning "vLLM requires CUDA. Skipping..."
    else
        print_success "Installing vLLM..."
        pip install vllm
        print_success "vLLM installed"
    fi
fi

# Install ExLlamaV2
if [ $install_exllama -eq 1 ]; then
    if [ $HAS_CUDA -eq 0 ]; then
        print_warning "ExLlamaV2 requires CUDA. Skipping..."
    else
        print_success "Installing ExLlamaV2..."
        pip install exllamav2
        print_success "ExLlamaV2 installed"
    fi
fi

# Install SGLang
if [ $install_sglang -eq 1 ]; then
    if [ $HAS_CUDA -eq 0 ]; then
        print_warning "SGLang requires CUDA. Skipping..."
    else
        print_success "Installing SGLang..."
        pip install "sglang[all]"
        print_success "SGLang installed"
    fi
fi

# ============================================================================
# STEP 5: Install Support Tools
# ============================================================================

print_section "Step 5: Installing Support Tools"

print_success "Installing HuggingFace Hub..."
pip install huggingface_hub[cli]

print_success "Installing monitoring tools..."
pip install nvidia-ml-py3 psutil gpustat

print_success "Installing development tools..."
pip install ipython rich

print_success "Support tools installed"

# ============================================================================
# STEP 6: Setup Directories
# ============================================================================

print_section "Step 6: Setting Up Directories"

mkdir -p models
mkdir -p .cache
mkdir -p .checkpoints
mkdir -p GENERATED_ENTRIES_MASTER
mkdir -p logs

print_success "Directories created"

# ============================================================================
# STEP 7: Configure HuggingFace
# ============================================================================

print_section "Step 7: HuggingFace Configuration"

echo "Do you want to login to HuggingFace? (Required for gated models like Llama)"
echo "You can get your token from: https://huggingface.co/settings/tokens"
echo ""
read -p "Login now? (y/n) [n]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    huggingface-cli login
    print_success "HuggingFace login complete"
else
    print_warning "Skipping HuggingFace login (you can run 'huggingface-cli login' later)"
fi

# ============================================================================
# STEP 8: Download Models (Optional)
# ============================================================================

print_section "Step 8: Model Download (Optional)"

echo "Would you like to download a model now?"
echo ""
echo "Recommended models:"
echo "  1. Qwen 2.5 72B Q5 (50GB, best quality) ⭐"
echo "  2. Qwen 2.5 32B Q5 (22GB, good quality, fits 24GB VRAM)"
echo "  3. Qwen 2.5 14B Q5 (10GB, budget option)"
echo "  4. Skip (download later)"
echo ""
read -p "Enter choice (1-4) [4]: " MODEL_CHOICE
MODEL_CHOICE=${MODEL_CHOICE:-4}

case $MODEL_CHOICE in
    1) python scripts/download_models.py --model qwen2.5-72b-q5 ;;
    2) python scripts/download_models.py --model qwen2.5-32b-q5 ;;
    3) python scripts/download_models.py --model qwen2.5-14b-q5 ;;
    4) print_success "Skipping model download" ;;
    *) print_warning "Invalid choice, skipping" ;;
esac

# ============================================================================
# STEP 9: GPU Optimization (Optional)
# ============================================================================

if [ $HAS_CUDA -eq 1 ]; then
    print_section "Step 9: GPU Optimization (Optional)"

    echo "Would you like to optimize GPU settings for best performance?"
    read -p "(Requires sudo, may affect other GPU applications) (y/n) [n]: " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_success "Setting persistence mode..."
        sudo nvidia-smi -pm 1

        print_success "Setting power limit to maximum..."
        # Get max power limit
        MAX_POWER=$(nvidia-smi --query-gpu=power.max_limit --format=csv,noheader,nounits | head -1)
        sudo nvidia-smi -pl $MAX_POWER

        print_success "GPU optimized"
    else
        print_success "Skipping GPU optimization"
    fi
fi

# ============================================================================
# STEP 10: Configuration
# ============================================================================

print_section "Step 10: Configuration"

# Check if config exists
if [ ! -f "Opus/config/config.yaml" ]; then
    print_error "Configuration file not found!"
    print_warning "Expected: Opus/config/config.yaml"
else
    print_success "Configuration file found"

    echo ""
    echo "Edit Opus/config/config.yaml to configure your model:"
    echo ""
    echo "  model:"
    echo "    backend: \"vllm\"  # or llamacpp, exllamav2, sglang"
    echo "    path: \"models/qwen2.5-72b/qwen2.5-72b-instruct-q5_k_m.gguf\""
    echo "    n_ctx: 32768"
    echo ""
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_section "Setup Complete!"

echo "✓ Virtual environment: venv/"
echo "✓ Dependencies installed"
echo "✓ Directories created"
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Download a model (if not done):"
echo "     python scripts/download_models.py --list"
echo "     python scripts/download_models.py --model qwen2.5-72b-q5"
echo ""
echo "  3. Configure your model:"
echo "     Edit Opus/config/config.yaml"
echo ""
echo "  4. Test the system:"
echo "     python opus_cli.py generate --subject \"Theosis\""
echo ""
echo "  5. Benchmark performance:"
echo "     python scripts/benchmark_models.py --quick"
echo ""
echo "  6. Read the production guide:"
echo "     cat SETUP_GUIDE_PRODUCTION.md"
echo ""

print_success "Setup complete! Enjoy generating theological content!"

echo ""
echo "============================================================================"
