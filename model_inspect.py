#!/usr/bin/env python3
"""
model_inspect.py - Inspect models and generate detailed reports for KORIEL ASI Project
Usage: python model_inspect.py --model-dir <path> --out <report.json>
"""

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

def safe_import(module_name: str, package: Optional[str] = None):
    """Safely import a module, returning None if not available"""
    try:
        if package:
            return __import__(module_name, fromlist=[package])
        else:
            return __import__(module_name)
    except ImportError:
        return None

# Try to import optional dependencies
torch = safe_import('torch')
transformers = safe_import('transformers')
numpy = safe_import('numpy')

def get_file_info(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Get basic file information"""
    path = Path(filepath)
    if not path.exists():
        return {"exists": False}
    
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified_time": stat.st_mtime,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "extension": path.suffix.lower()
    }

def estimate_params_from_numpy(weights: Dict[str, Any]) -> int:
    """Estimate parameter count from numpy arrays"""
    if not numpy:
        return 0
    
    total_params = 0
    for key, value in weights.items():
        if hasattr(value, 'shape') and hasattr(value, 'size'):
            if isinstance(value, numpy.ndarray):
                total_params += value.size
            elif hasattr(value, 'numel'):  # PyTorch tensor
                total_params += value.numel()
    return total_params

def inspect_pytorch_checkpoint(model_path: Path) -> Dict[str, Any]:
    """Inspect PyTorch checkpoint file"""
    if not torch:
        return {"error": "PyTorch not available"}
    
    try:
        # Load with map_location to avoid GPU requirements
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        
        result = {
            "format": "pytorch",
            "checkpoint_keys": list(checkpoint.keys()) if isinstance(checkpoint, dict) else ["<tensor>"],
            "loading_successful": True
        }
        
        # Analyze contents
        if isinstance(checkpoint, dict):
            # Look for common keys
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
                result["model_state_dict_keys"] = list(state_dict.keys()) if isinstance(state_dict, dict) else []
                result["parameter_count"] = sum(v.numel() for v in state_dict.values() if hasattr(v, 'numel'))
            
            if 'model_config' in checkpoint:
                result["model_config"] = checkpoint['model_config']
            
            if 'optimizer_state_dict' in checkpoint:
                result["has_optimizer_state"] = True
            
            # Try to estimate total parameters
            total_params = 0
            for key, value in checkpoint.items():
                if hasattr(value, 'numel'):
                    total_params += value.numel()
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(v, 'numel'):
                            total_params += v.numel()
            result["estimated_total_parameters"] = total_params
            
        return result
        
    except Exception as e:
        return {
            "format": "pytorch",
            "loading_successful": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def inspect_numpy_pickle(model_path: Path) -> Dict[str, Any]:
    """Inspect numpy/pickle file"""
    try:
        import pickle
        
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
        
        result = {
            "format": "pickle",
            "loading_successful": True,
            "data_type": type(data).__name__
        }
        
        if isinstance(data, dict):
            result["keys"] = list(data.keys())
            result["parameter_count"] = estimate_params_from_numpy(data)
        elif hasattr(data, '__dict__'):
            result["attributes"] = list(vars(data).keys())
            result["parameter_count"] = estimate_params_from_numpy(vars(data))
        
        return result
        
    except Exception as e:
        return {
            "format": "pickle", 
            "loading_successful": False,
            "error": str(e)
        }

def inspect_custom_model_file(model_path: Path) -> Dict[str, Any]:
    """Inspect custom model Python file"""
    result = {
        "format": "python_source",
        "analysis": {}
    }
    
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic analysis
        lines = content.split('\n')
        result["analysis"] = {
            "total_lines": len(lines),
            "non_empty_lines": len([l for l in lines if l.strip()]),
            "has_class_definitions": "class " in content,
            "has_forward_method": "def forward" in content,
            "imports": []
        }
        
        # Extract imports
        import_lines = [l.strip() for l in lines if l.strip().startswith(('import ', 'from '))]
        result["analysis"]["imports"] = import_lines[:20]  # Limit to first 20
        
        # Extract class definitions
        class_definitions = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('class ') and ':' in stripped:
                class_definitions.append(stripped)
        result["analysis"]["class_definitions"] = class_definitions
        
        # Look for model architectures
        model_indicators = [
            "TinyByteLM", "TinyByteTransformer", "Controller", "RCCE", 
            "Model", "Network", "Transformer"
        ]
        found_indicators = [ind for ind in model_indicators if ind in content]
        result["analysis"]["model_indicators"] = found_indicators
        
        return result
        
    except Exception as e:
        return {
            "format": "python_source",
            "loading_successful": False,
            "error": str(e)
        }

def inspect_transformers_model(model_path: Path) -> Dict[str, Any]:
    """Try to load as HuggingFace transformers model"""
    if not transformers:
        return {"error": "transformers library not available"}
    
    try:
        # Try loading config first
        config = transformers.AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        
        result = {
            "format": "huggingface_transformers",
            "config": config.to_dict() if hasattr(config, 'to_dict') else str(config),
            "loading_successful": True
        }
        
        # Try to estimate parameters from config
        if hasattr(config, 'num_parameters'):
            result["parameter_count"] = config.num_parameters
        
        return result
        
    except Exception as e:
        return {
            "format": "huggingface_transformers",
            "loading_successful": False,
            "error": str(e)
        }

def inspect_model_directory(model_dir: Path) -> Dict[str, Any]:
    """Comprehensive model directory inspection"""
    if not model_dir.exists():
        return {"error": f"Directory {model_dir} does not exist"}
    
    result = {
        "directory_info": get_file_info(model_dir),
        "files": {},
        "analysis": {}
    }
    
    # List all files
    all_files = list(model_dir.rglob('*')) if model_dir.is_dir() else [model_dir]
    
    # Categorize files
    model_files = []
    config_files = []
    checkpoint_files = []
    
    for file_path in all_files:
        if file_path.is_file():
            file_info = get_file_info(file_path)
            relative_path = file_path.relative_to(model_dir)
            result["files"][str(relative_path)] = file_info
            
            # Categorize
            ext = file_path.suffix.lower()
            name = file_path.name.lower()
            
            if ext in ['.pt', '.pth', '.bin', '.safetensors', '.ckpt']:
                checkpoint_files.append(file_path)
            elif ext in ['.json', '.yaml', '.yml'] or 'config' in name:
                config_files.append(file_path)
            elif ext == '.py':
                model_files.append(file_path)
    
    result["analysis"]["checkpoint_files"] = len(checkpoint_files)
    result["analysis"]["config_files"] = len(config_files)
    result["analysis"]["python_files"] = len(model_files)
    
    # Inspect main files
    inspections = {}
    
    # Try to find and inspect main model file
    main_checkpoint = None
    if checkpoint_files:
        # Prefer .pt files, then others
        pt_files = [f for f in checkpoint_files if f.suffix.lower() in ['.pt', '.pth']]
        main_checkpoint = pt_files[0] if pt_files else checkpoint_files[0]
    
    if main_checkpoint:
        if main_checkpoint.suffix.lower() in ['.pt', '.pth']:
            inspections["main_checkpoint"] = inspect_pytorch_checkpoint(main_checkpoint)
        elif main_checkpoint.suffix.lower() in ['.pkl']:
            inspections["main_checkpoint"] = inspect_numpy_pickle(main_checkpoint)
    
    # Try HuggingFace format
    if model_dir.is_dir():
        hf_inspection = inspect_transformers_model(model_dir)
        if hf_inspection.get("loading_successful"):
            inspections["huggingface"] = hf_inspection
    
    # Inspect Python model files
    for py_file in model_files[:3]:  # Limit to first 3
        key = f"python_file_{py_file.name}"
        inspections[key] = inspect_custom_model_file(py_file)
    
    result["inspections"] = inspections
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description='Inspect model files and generate detailed reports'
    )
    parser.add_argument(
        '--model-dir', 
        type=str, 
        required=True,
        help='Path to model directory or file'
    )
    parser.add_argument(
        '--out', 
        type=str, 
        default='model_report.json',
        help='Output JSON report file'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Print verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Inspecting model: {args.model_dir}")
        print(f"Output file: {args.out}")
    
    # Perform inspection
    model_path = Path(args.model_dir)
    
    try:
        if model_path.is_file():
            # Single file inspection
            file_info = get_file_info(model_path)
            
            if model_path.suffix.lower() in ['.pt', '.pth']:
                inspection = inspect_pytorch_checkpoint(model_path)
            elif model_path.suffix.lower() in ['.pkl']:
                inspection = inspect_numpy_pickle(model_path) 
            elif model_path.suffix.lower() == '.py':
                inspection = inspect_custom_model_file(model_path)
            else:
                inspection = {"error": f"Unsupported file type: {model_path.suffix}"}
            
            result = {
                "timestamp": time.time(),
                "model_path": str(model_path),
                "inspection_type": "single_file",
                "file_info": file_info,
                "inspection": inspection
            }
        else:
            # Directory inspection
            result = {
                "timestamp": time.time(),
                "model_path": str(model_path),
                "inspection_type": "directory",
                **inspect_model_directory(model_path)
            }
        
        # Add metadata
        result["inspector_info"] = {
            "torch_available": torch is not None,
            "transformers_available": transformers is not None,
            "numpy_available": numpy is not None,
            "python_version": sys.version,
        }
        
        # Write output
        with open(args.out, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        if args.verbose:
            print(f"Report saved to: {args.out}")
            if "inspections" in result:
                for key, inspection in result["inspections"].items():
                    if inspection.get("loading_successful"):
                        print(f"✓ {key}: Successfully inspected")
                        if "parameter_count" in inspection:
                            params = inspection["parameter_count"]
                            print(f"  Parameters: {params:,}")
                    else:
                        print(f"✗ {key}: Failed - {inspection.get('error', 'Unknown error')}")
        
        return 0
        
    except Exception as e:
        error_result = {
            "timestamp": time.time(),
            "model_path": str(model_path),
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        
        with open(args.out, 'w') as f:
            json.dump(error_result, f, indent=2, default=str)
        
        print(f"Error during inspection: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())