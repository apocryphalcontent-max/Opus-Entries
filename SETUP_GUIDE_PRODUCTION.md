# Opus Maximus - Production Setup Guide
## The Best Local LLM Stack for Theological Content Generation

**Last Updated:** November 10, 2025
**Target:** Maximum quality theological content generation
**Difficulty:** Advanced (but worth it!)

---

## 🎯 Recommended Stack

After extensive research for theological content generation, here's the optimal stack:

### Primary LLM Models (Choose One)

**Tier 1: Best Quality (Recommended)**
1. **Qwen 2.5 72B Instruct** ⭐ TOP PICK
   - Best for long-form, sophisticated prose
   - Excellent citation handling
   - Strong reasoning capabilities
   - Size: ~40GB (Q4_K_M), ~50GB (Q5_K_M), ~60GB (Q6_K)
   - HuggingFace: `Qwen/Qwen2.5-72B-Instruct`

2. **Llama 3.1 70B Instruct**
   - Strong all-around performance
   - Good theological reasoning
   - Size: ~40GB (Q4_K_M), ~48GB (Q5_K_M)
   - HuggingFace: `meta-llama/Llama-3.1-70B-Instruct`

**Tier 2: Best Value (Good Alternative)**
3. **Qwen 2.5 32B Instruct**
   - 80% of 72B quality, 40% of size
   - Fits on 24GB VRAM
   - Size: ~18GB (Q4_K_M), ~22GB (Q5_K_M)
   - HuggingFace: `Qwen/Qwen2.5-32B-Instruct`

4. **Mistral Large 2 (123B)** - If you have 2x GPUs
   - Exceptional quality
   - Requires 80GB+ VRAM
   - HuggingFace: `mistralai/Mistral-Large-Instruct-2407`

### Inference Engines (Use Multiple)

**1. vLLM** - Production Workhorse ⭐
- **Speed**: 3-5x faster than llama.cpp
- **Features**: Continuous batching, PagedAttention
- **Best For**: Batch processing, production
- **Requirements**: CUDA GPU, 16GB+ VRAM

**2. llama.cpp** - Universal Fallback
- **Speed**: Good (optimized)
- **Features**: CPU support, low memory
- **Best For**: Development, testing, CPU-only
- **Requirements**: Any system

**3. ExLlamaV2** - VRAM Optimizer
- **Speed**: Very fast
- **Features**: 4-bit EXL2 quantization
- **Best For**: Large models on limited VRAM
- **Requirements**: CUDA GPU

**4. SGLang** - Structured Generation ⭐
- **Speed**: vLLM-based
- **Features**: Constrained decoding, regex patterns
- **Best For**: Citations, structured output
- **Requirements**: CUDA GPU

### Support Tools

1. **Text Generation WebUI** (oobabooga) - Testing/Development
2. **Ollama** - Model management
3. **Hugging Face Hub** - Model downloads
4. **LM Studio** - GUI for testing

---

## 💻 Hardware Requirements

### Optimal Setup (Recommended)

```
GPU:     NVIDIA RTX 4090 (24GB VRAM) or RTX 6000 Ada (48GB)
         OR: 2x RTX 4080 (16GB each) in NVLink
CPU:     AMD Ryzen 9 7950X or Intel i9-14900K
RAM:     64GB DDR5-6000
Storage: 2TB NVMe Gen4 SSD
PSU:     1200W+ (for 4090)
```

**Cost:** ~$4,000-$6,000

### Budget Setup (Minimum for 70B)

```
GPU:     NVIDIA RTX 4070 Ti (16GB VRAM) - Q4 quantization
CPU:     AMD Ryzen 7 7700X or Intel i7-14700K
RAM:     32GB DDR5
Storage: 1TB NVMe SSD
PSU:     850W
```

**Cost:** ~$2,500-$3,500

### Server Setup (Professional)

```
GPU:     2x NVIDIA A6000 (48GB each) or H100 (80GB)
CPU:     AMD EPYC 7763 or Xeon Platinum
RAM:     256GB ECC
Storage: 4TB NVMe RAID
```

**Cost:** ~$15,000-$40,000

### Model Size vs VRAM Guide

| Model Size | Q4_K_M | Q5_K_M | Q6_K | FP16 |
|------------|--------|--------|------|------|
| **32B** | 18GB | 22GB | 26GB | 64GB |
| **70B** | 40GB | 48GB | 56GB | 140GB |
| **72B** | 42GB | 50GB | 60GB | 144GB |

**Recommendations:**
- **16GB VRAM**: 32B models Q4/Q5
- **24GB VRAM**: 72B Q4 or 32B Q6
- **48GB VRAM**: 72B Q6 (best quality)
- **80GB+ VRAM**: 123B+ models

---

## 📦 Installation - Production Stack

### Step 1: System Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install CUDA 12.1 (if not installed)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install cuda-12-1 -y

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify CUDA
nvidia-smi
nvcc --version

# Install build tools
sudo apt install -y build-essential cmake git python3-dev python3-pip python3-venv
```

### Step 2: Create Virtual Environment

```bash
cd /home/user/Opus-Entries
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### Step 3: Install vLLM (Fastest - Production) ⭐

```bash
# vLLM with CUDA 12.1
pip install vllm

# Test installation
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"
```

### Step 4: Install llama.cpp (Universal Backup)

```bash
# With CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

# Verify
python -c "from llama_cpp import Llama; print('llama.cpp ready')"
```

### Step 5: Install ExLlamaV2 (VRAM Optimizer)

```bash
# ExLlamaV2 for EXL2 quantization
pip install exllamav2

# Verify
python -c "from exllamav2 import ExLlamaV2; print('ExLlamaV2 ready')"
```

### Step 6: Install SGLang (Structured Generation) ⭐

```bash
# SGLang for constrained decoding
pip install "sglang[all]"

# Verify
python -c "import sglang; print(f'SGLang version: {sglang.__version__}')"
```

### Step 7: Install Support Tools

```bash
# Model management
pip install huggingface_hub[cli]

# Structured generation libraries
pip install outlines-core
pip install guidance

# Monitoring and optimization
pip install nvidia-ml-py3
pip install psutil
pip install gpustat

# Quality tools
pip install sentencepiece protobuf
pip install transformers accelerate
pip install bitsandbytes  # For quantization

# Development tools
pip install ipython jupyter
pip install rich tqdm

# All Opus dependencies
pip install -r requirements.txt
```

### Step 8: Configure HuggingFace

```bash
# Login to HuggingFace (for gated models like Llama)
huggingface-cli login
# Enter your token from https://huggingface.co/settings/tokens

# Set cache directory (optional, saves space)
export HF_HOME=/path/to/large/drive/huggingface
echo 'export HF_HOME=/path/to/large/drive/huggingface' >> ~/.bashrc
```

---

## 📥 Download Models

### Option A: Using HuggingFace Hub (Recommended)

```bash
# Create models directory
mkdir -p models

# Download Qwen 2.5 72B (GGUF) - Recommended ⭐
huggingface-cli download Qwen/Qwen2.5-72B-Instruct-GGUF \
  qwen2.5-72b-instruct-q5_k_m.gguf \
  --local-dir models/qwen2.5-72b \
  --local-dir-use-symlinks False

# Alternative: Llama 3.1 70B (GGUF)
huggingface-cli download bartowski/Meta-Llama-3.1-70B-Instruct-GGUF \
  Meta-Llama-3.1-70B-Instruct-Q5_K_M.gguf \
  --local-dir models/llama3.1-70b \
  --local-dir-use-symlinks False

# For 32B (budget option)
huggingface-cli download Qwen/Qwen2.5-32B-Instruct-GGUF \
  qwen2.5-32b-instruct-q5_k_m.gguf \
  --local-dir models/qwen2.5-32b \
  --local-dir-use-symlinks False
```

**Expected Download Times:**
- 72B Q5_K_M (~50GB): 30-120 minutes depending on connection
- 32B Q5_K_M (~22GB): 15-60 minutes

### Option B: Using Automated Script

I'll create a download script below.

---

## 🔧 Configuration

### Update Opus Config for Best Model

Edit `Opus/config/config.yaml`:

```yaml
# =============================================================================
# MODEL SETTINGS - Production with Qwen 2.5 72B
# =============================================================================
model:
  # Primary: vLLM for speed
  backend: "vllm"  # Options: vllm, llamacpp, exllamav2, sglang

  # Model path (GGUF for llama.cpp, HF for vLLM)
  path: "Qwen/Qwen2.5-72B-Instruct"  # HF model for vLLM
  # path: "models/qwen2.5-72b/qwen2.5-72b-instruct-q5_k_m.gguf"  # For llama.cpp

  # Context window
  n_ctx: 32768  # Qwen 2.5 supports 32k context

  # vLLM settings
  gpu_memory_utilization: 0.95  # Use 95% of VRAM
  max_model_len: 32768
  tensor_parallel_size: 1  # Set to 2 for multi-GPU

  # Generation settings
  temperature: 0.7
  top_p: 0.9
  top_k: 40
  max_tokens: 4096
  repetition_penalty: 1.1

  # Batch settings (for vLLM)
  max_num_seqs: 32  # Process up to 32 requests in parallel

# =============================================================================
# BACKEND-SPECIFIC SETTINGS
# =============================================================================
backends:
  vllm:
    quantization: "awq"  # Options: awq, gptq, None
    dtype: "auto"  # auto, float16, bfloat16
    trust_remote_code: true
    max_num_batched_tokens: 8192

  llamacpp:
    n_gpu_layers: -1  # All layers on GPU
    n_batch: 512
    n_threads: 16
    use_mlock: true

  exllamav2:
    max_seq_len: 32768
    compress_pos_emb: 1.0
    cache_8bit: true

  sglang:
    port: 30000
    constrained_json: true  # Enable JSON schema constraints
```

---

## 🚀 Performance Optimization

### NVIDIA GPU Optimization

```bash
# Set persistence mode (keeps driver loaded)
sudo nvidia-smi -pm 1

# Set power limit to maximum (for 4090)
sudo nvidia-smi -pl 450

# Set application clocks for consistent performance
sudo nvidia-smi -ac 9501,2520  # Memory,Graphics for 4090

# Enable MIG mode if using A100 (multi-instance GPU)
# sudo nvidia-smi -mig 1
```

### System Optimization

```bash
# Increase file descriptor limits
sudo sh -c 'echo "* soft nofile 65535" >> /etc/security/limits.conf'
sudo sh -c 'echo "* hard nofile 65535" >> /etc/security/limits.conf'

# Disable CPU throttling
sudo cpupower frequency-set -g performance

# Set swappiness (reduce swap usage)
sudo sysctl vm.swappiness=10
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf

# Increase shared memory (for vLLM)
sudo sh -c 'echo "kernel.shmmax=68719476736" >> /etc/sysctl.conf'
sudo sysctl -p
```

### vLLM Optimization

```bash
# Set environment variables
export VLLM_ATTENTION_BACKEND=FLASHINFER  # Fastest attention
export CUDA_VISIBLE_DEVICES=0  # Or 0,1 for multi-GPU
export VLLM_USE_MODELSCOPE=false

# Add to ~/.bashrc
echo 'export VLLM_ATTENTION_BACKEND=FLASHINFER' >> ~/.bashrc
```

---

## 🧪 Testing Your Setup

### Test 1: Verify GPU

```bash
python << EOF
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
EOF
```

### Test 2: Test vLLM

```bash
python << EOF
from vllm import LLM, SamplingParams

# Initialize (this may take 2-5 minutes for 72B model)
print("Loading model... (this may take a few minutes)")
llm = LLM(
    model="Qwen/Qwen2.5-72B-Instruct",
    gpu_memory_utilization=0.95,
    max_model_len=8192,  # Start small for testing
    tensor_parallel_size=1
)

# Generate
prompts = ["What is theosis in Orthodox theology?"]
sampling_params = SamplingParams(temperature=0.7, max_tokens=200)
outputs = llm.generate(prompts, sampling_params)

# Print result
for output in outputs:
    print("\n" + "="*70)
    print("GENERATED TEXT:")
    print("="*70)
    print(output.outputs[0].text)
    print("="*70)
EOF
```

Expected output should be a sophisticated theological response about theosis.

### Test 3: Test llama.cpp

```bash
python << EOF
from llama_cpp import Llama

print("Loading model...")
llm = Llama(
    model_path="models/qwen2.5-72b/qwen2.5-72b-instruct-q5_k_m.gguf",
    n_ctx=8192,
    n_gpu_layers=-1,
    verbose=False
)

print("Generating...")
output = llm("What is theosis in Orthodox theology?", max_tokens=200)
print("\n" + "="*70)
print(output['choices'][0]['text'])
print("="*70)
EOF
```

### Test 4: Benchmark Speed

I'll create a benchmark script below.

---

## 📊 Expected Performance

### Generation Speed (Qwen 2.5 72B Q5_K_M)

| Hardware | Backend | Tokens/sec | Time for 2000 tokens |
|----------|---------|------------|---------------------|
| RTX 4090 24GB | vLLM | 25-35 | 60-80 seconds |
| RTX 4090 24GB | llama.cpp | 8-12 | 170-250 seconds |
| RTX 4080 16GB | vLLM Q4 | 20-28 | 70-100 seconds |
| 2x RTX 4090 | vLLM TP2 | 40-55 | 35-50 seconds |
| RTX 4070 Ti | ExLlamaV2 | 15-22 | 90-135 seconds |

### Entry Generation Time Estimates

With **RTX 4090 + vLLM + Qwen 2.5 72B**:

| Component | Tokens | Time (est.) |
|-----------|--------|-------------|
| Blueprint | 2000 | 1-2 min |
| Section 1-2 | 1500 each | 1-2 min each |
| Section 3-4 | 2000 each | 1.5-2.5 min each |
| Section 5-6 | 2500 each | 2-3 min each |
| **Total per entry** | ~12,000 | **15-25 minutes** ⭐ |

**Batch estimates:**
- 10 entries: 3-4 hours
- 100 entries: 1.5-2 days
- 1,000 entries: 2-3 weeks
- 12,000 entries: 6-9 months (24/7)

---

## 🛠️ Troubleshooting

### Issue: "CUDA out of memory"

```bash
# Solution 1: Reduce context window
# In config.yaml: n_ctx: 16384 → 8192

# Solution 2: Use Q4 quantization instead of Q5
# Download Q4 model instead

# Solution 3: Enable CPU offloading
# In config.yaml: gpu_memory_utilization: 0.95 → 0.85
```

### Issue: vLLM fails to load

```bash
# Check CUDA version
nvcc --version
python -c "import torch; print(torch.version.cuda)"

# Reinstall vLLM for your CUDA version
pip uninstall vllm
pip install vllm  # Will auto-detect CUDA
```

### Issue: Slow generation

```bash
# Check GPU utilization
watch -n 1 nvidia-smi

# Should show:
# - GPU utilization: 95-100%
# - Memory usage: 95%+ of VRAM
# - Temperature: <85°C

# If low utilization, check:
python -c "import torch; print(f'Using: {torch.cuda.get_device_name(0)}')"
```

---

## 📈 Next Steps

1. **Run Benchmark Suite** (see scripts below)
2. **Generate Test Entry** with optimal settings
3. **Fine-tune Prompts** for your model
4. **Start Production Batch** with monitoring

---

## 🎓 Advanced: Multi-GPU Setup

If you have 2+ GPUs:

```yaml
# In config.yaml
model:
  backend: "vllm"
  tensor_parallel_size: 2  # Use 2 GPUs

# Set which GPUs to use
# export CUDA_VISIBLE_DEVICES=0,1
```

This will split the model across GPUs for ~1.8x speedup.

---

## 💰 Cost Analysis

### One-time Hardware Investment

| Setup | Cost | Capability |
|-------|------|-----------|
| RTX 4070 Ti + PC | $2,500 | 32B models, slower 72B |
| RTX 4090 + PC | $4,500 | 72B models, optimal |
| 2x RTX 4090 + PC | $7,500 | 72B fast, or 123B |
| Server (A6000) | $15,000+ | Professional |

### Operating Costs (24/7)

| GPU | Power | $/month | $/year |
|-----|-------|---------|--------|
| RTX 4070 Ti | ~300W | $30 | $360 |
| RTX 4090 | ~450W | $45 | $540 |
| 2x RTX 4090 | ~900W | $90 | $1,080 |

**Total for 12,000 entries (6-9 months):**
- Hardware: $2,500-$7,500
- Electricity: $270-$810
- **Total: $2,770-$8,310**

**vs Cloud API:**
- OpenAI GPT-4: ~$15,000-$25,000
- Claude Opus: ~$20,000-$35,000

**ROI:** Break-even after ~500-1,000 entries vs API costs

---

**This setup will give you the absolute best local generation capabilities for theological content!**

Next: Install scripts and enhanced backends →
