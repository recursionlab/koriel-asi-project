# KORIEL ASI Project Probe Scripts

This directory contains probe scripts for analyzing the KORIEL ASI Project repository structure and models.

## Scripts

### 1. `repo_search.sh`
Discovers and catalogs model, tokenizer, orchestrator, configuration, and data files in the repository.

**Usage:**
```bash
chmod +x repo_search.sh
./repo_search.sh . > repo_search_report.json
```

**Output:** JSON report containing:
- Model files (Python files with model/transformer/controller classes)
- Checkpoint files (.pt, .pth, .pkl, .npz, etc.)
- Tokenizer files (*tokenizer*, *vocab*, .model files)
- Orchestrator files (controller, RCCE, consciousness modules)
- Configuration files (.yaml, .json, config files)
- Data files (.txt, .csv, .jsonl, data directories)
- Summary statistics

### 2. `model_inspect.py`
Analyzes model files and generates detailed inspection reports.

**Usage:**
```bash
# Set up environment (first time only)
python3 -m venv env && source env/bin/activate
pip install --upgrade pip
pip install torch transformers sentencepiece tokenizers numpy

# Inspect a model checkpoint
python model_inspect.py --model-dir ./checkpoints/tinylm.pt --out model_report.json

# Inspect a model directory
python model_inspect.py --model-dir ./checkpoints --out checkpoints_report.json --verbose
```

**Features:**
- Supports PyTorch checkpoints (.pt, .pth)
- Handles custom pickle formats
- Analyzes Python source files
- Attempts HuggingFace transformers format loading
- Estimates parameter counts
- Memory-efficient loading with `low_cpu_mem_usage`
- Detailed error reporting

**Output:** JSON report containing:
- File information (size, type, modification time)
- Model architecture details
- Parameter counts
- Configuration parameters
- Loading success/failure status
- Error diagnostics

## Example Output

### Repository Search Results
The KORIEL ASI Project contains:
- **14 model files** including TinyByteLM, TinyByteTransformer, RCCE controllers
- **1 checkpoint file** (tinylm.pt - 1.83MB, 477,952 parameters)  
- **Multiple orchestrator files** for consciousness detection and training
- **Configuration files** (rcce.yaml, ethics_policy.json)
- **Data files** in conversations-pocket directory

### Model Inspection Results  
**tinylm.pt checkpoint analysis:**
- Format: PyTorch checkpoint
- Parameters: 477,952 total
- Architecture: TinyByteTransformer (256 vocab, 128 d_model, 4 heads, 2 layers)
- Contains: model_state_dict, model_config, rcce_state, training_args

## Notes

- Scripts automatically exclude virtual environments (env/, .venv/) and node_modules/
- `model_inspect.py` gracefully handles missing dependencies
- Both scripts use memory-efficient approaches for large files
- JSON output is structured for easy parsing and integration with other tools

## Dependencies

- **repo_search.sh**: Basic Unix tools (find, grep, stat)
- **model_inspect.py**: Python 3.7+, optional: torch, transformers, numpy