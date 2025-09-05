#!/bin/bash

# repo_search.sh - Discover model, tokenizer, and orchestrator files in KORIEL ASI Project
# Usage: ./repo_search.sh [directory] > repo_search_report.json

SEARCH_DIR="${1:-.}"

echo "{"
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"repository\": \"koriel-asi-project\","
echo "  \"search_directory\": \"$SEARCH_DIR\","
echo "  \"scan_results\": {"

# Model files (.py files containing model definitions)
echo "    \"model_files\": ["
first=true
find "$SEARCH_DIR" -name "*.py" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -exec grep -l "class.*Model\|class.*Transformer\|class.*LM\|class.*Network\|def forward\|class.*Controller\|class.*RCCE" {} \; 2>/dev/null | sort | while IFS= read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "      {\"path\": \"$file\", \"size\": $(stat -c%s "$file" 2>/dev/null || echo 0), \"type\": \"python_model\"}"
done
echo ""
echo "    ],"

# Checkpoint files
echo "    \"checkpoint_files\": ["
first=true
find "$SEARCH_DIR" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \( \
    -name "*.pt" -o -name "*.pth" -o -name "*.pkl" -o -name "*.npz" -o \
    -name "*.h5" -o -name "*.safetensors" -o -name "*.bin" -o -name "*.ckpt" \
\) 2>/dev/null | sort | while IFS= read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "      {\"path\": \"$file\", \"size\": $(stat -c%s "$file" 2>/dev/null || echo 0), \"type\": \"checkpoint\"}"
done
echo ""
echo "    ],"

# Tokenizer files
echo "    \"tokenizer_files\": ["
first=true
find "$SEARCH_DIR" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \( \
    -name "*tokenizer*" -o -name "*vocab*" -o -name "*.model" \
\) 2>/dev/null | sort | while IFS= read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "      {\"path\": \"$file\", \"size\": $(stat -c%s "$file" 2>/dev/null || echo 0), \"type\": \"tokenizer\"}"
done
echo ""
echo "    ],"

# Controller/Orchestrator files
echo "    \"orchestrator_files\": ["
first=true
find "$SEARCH_DIR" -name "*.py" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -exec grep -l "controller\|orchestrator\|rcce\|consciousness\|train\|Controller\|RCCE" {} \; 2>/dev/null | sort | while IFS= read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "      {\"path\": \"$file\", \"size\": $(stat -c%s "$file" 2>/dev/null || echo 0), \"type\": \"orchestrator\"}"
done
echo ""
echo "    ],"

# Configuration files
echo "    \"config_files\": ["
first=true
find "$SEARCH_DIR" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \( \
    -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.toml" -o \
    -name "*.cfg" -o -name "*.ini" -o -name "config*" -o -name "*config*" \
\) 2>/dev/null | sort | while IFS= read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "      {\"path\": \"$file\", \"size\": $(stat -c%s "$file" 2>/dev/null || echo 0), \"type\": \"config\"}"
done
echo ""
echo "    ],"

# Data files
echo "    \"data_files\": ["
first=true
find "$SEARCH_DIR" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \( \
    -name "*.txt" -o -name "*.csv" -o -name "*.jsonl" -o \
    -path "*/data/*" -o -path "*/datasets/*" -o -path "*/conversations*" \
\) 2>/dev/null | head -20 | sort | while IFS= read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    echo -n "      {\"path\": \"$file\", \"size\": $(stat -c%s "$file" 2>/dev/null || echo 0), \"type\": \"data\"}"
done
echo ""
echo "    ]"

echo "  },"

# Summary statistics
model_count=$(find "$SEARCH_DIR" -name "*.py" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -exec grep -l "class.*Model\|class.*Transformer\|class.*LM\|class.*Network\|def forward\|class.*Controller\|class.*RCCE" {} \; 2>/dev/null | wc -l)
checkpoint_count=$(find "$SEARCH_DIR" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \( -name "*.pt" -o -name "*.pth" -o -name "*.pkl" -o -name "*.npz" -o -name "*.h5" -o -name "*.safetensors" -o -name "*.bin" -o -name "*.ckpt" \) 2>/dev/null | wc -l)
config_count=$(find "$SEARCH_DIR" -type f -not -path "*/env/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.toml" -o -name "*.cfg" -o -name "*.ini" -o -name "config*" -o -name "*config*" \) 2>/dev/null | wc -l)

echo "  \"summary\": {"
echo "    \"total_model_files\": $model_count,"
echo "    \"total_checkpoint_files\": $checkpoint_count,"
echo "    \"total_config_files\": $config_count,"
echo "    \"scan_completed\": true"
echo "  }"
echo "}"