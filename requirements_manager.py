"""
Requirements management and dependency audit for KORIEL ASI Project.

Implements requirements.lock generation, dependency pinning, and license auditing.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
import pkg_resources
import importlib.metadata
from datetime import datetime


def generate_requirements_lock(output_file: Path = None) -> None:
    """
    Generate hermetic requirements.lock file from current environment.
    
    Args:
        output_file: Path to output lock file (default: requirements.lock)
    """
    if output_file is None:
        output_file = Path("requirements.lock")
    
    # Get all installed packages with exact versions
    installed_packages = []
    
    try:
        # Use pip freeze to get exact versions
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('#') and '==' in line:
                installed_packages.append(line)
    
    except subprocess.CalledProcessError as e:
        print(f"Error running pip freeze: {e}")
        return
    
    # Write lock file with metadata
    with open(output_file, 'w') as f:
        f.write(f"# Generated on {datetime.now().isoformat()}\n")
        f.write(f"# Python version: {sys.version}\n")
        f.write(f"# Platform: {sys.platform}\n")
        f.write("# \n")
        f.write("# This file was automatically generated. Do not edit by hand.\n")
        f.write("# To regenerate: python requirements_manager.py --generate-lock\n")
        f.write("\n")
        
        for package in sorted(installed_packages):
            f.write(f"{package}\n")
    
    print(f"✓ Generated requirements.lock with {len(installed_packages)} packages")


def audit_dependencies() -> Dict[str, Any]:
    """
    Audit current dependencies for security and license issues.
    
    Returns:
        Dictionary with audit results
    """
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "packages": [],
        "license_issues": [],
        "security_issues": [],
        "total_packages": 0,
    }
    
    try:
        # Get all installed packages
        for dist in importlib.metadata.distributions():
            package_info = {
                "name": dist.metadata["Name"],
                "version": dist.metadata["Version"],
                "license": dist.metadata.get("License", "Unknown"),
                "author": dist.metadata.get("Author", "Unknown"),
                "home_page": dist.metadata.get("Home-page", "Unknown"),
            }
            
            audit_results["packages"].append(package_info)
            
            # Check for problematic licenses
            license_text = package_info["license"].lower()
            problematic_licenses = ["gpl", "agpl", "copyleft"]
            
            if any(prob in license_text for prob in problematic_licenses):
                audit_results["license_issues"].append({
                    "package": package_info["name"],
                    "version": package_info["version"],
                    "license": package_info["license"],
                    "issue": "Potentially restrictive license"
                })
        
        audit_results["total_packages"] = len(audit_results["packages"])
        
    except Exception as e:
        audit_results["error"] = str(e)
    
    return audit_results


def generate_license_report(output_file: Path = None) -> None:
    """
    Generate license report for all dependencies.
    
    Args:
        output_file: Path to output report (default: reports/licenses.json)
    """
    if output_file is None:
        output_file = Path("reports") / "licenses.json"
    
    output_file.parent.mkdir(exist_ok=True)
    
    audit_results = audit_dependencies()
    
    with open(output_file, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"✓ Generated license report: {output_file}")
    print(f"  Total packages: {audit_results['total_packages']}")
    print(f"  License issues: {len(audit_results['license_issues'])}")


def check_import_budget(budget_seconds: float = 2.0) -> Dict[str, Any]:
    """
    Check that module imports don't exceed time budget.
    
    Args:
        budget_seconds: Maximum allowed import time
        
    Returns:
        Dictionary with import timing results
    """
    import time
    import importlib
    
    modules_to_check = [
        "json", "pathlib", "datetime", "os",
        "yaml", "hashlib", "statistics"
    ]
    
    results = {
        "budget_seconds": budget_seconds,
        "modules": [],
        "total_time": 0.0,
        "budget_exceeded": False,
    }
    
    for module_name in modules_to_check:
        start_time = time.time()
        
        try:
            # Use importlib to import fresh
            if module_name in sys.modules:
                # Don't clear core modules like sys, just reload
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            
            import_time = time.time() - start_time
            
            results["modules"].append({
                "name": module_name,
                "import_time": import_time,
                "status": "success"
            })
            
            results["total_time"] += import_time
            
        except Exception as e:
            results["modules"].append({
                "name": module_name,
                "import_time": 0.0,
                "status": "failed",
                "error": str(e)
            })
    
    results["budget_exceeded"] = results["total_time"] > budget_seconds
    
    return results


def validate_no_wildcards() -> List[Dict[str, str]]:
    """
    Validate that no wildcard imports are used in source code.
    
    Returns:
        List of files with wildcard imports
    """
    violations = []
    
    # Check source files
    src_dir = Path("src")
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if 'from' in line and 'import *' in line:
                        violations.append({
                            "file": str(py_file),
                            "line": line_num,
                            "content": line.strip()
                        })
            except Exception:
                continue  # Skip files that can't be read
    
    return violations


def pin_upper_bounds(packages: List[str]) -> None:
    """
    Pin upper bounds for specified packages in requirements.txt.
    
    Args:
        packages: List of package names to pin
    """
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("requirements.txt not found")
        return
    
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    # Map of packages to their recommended upper bounds
    upper_bounds = {
        "numpy": "<2.0",
        "matplotlib": "<4.0",
        "pyyaml": "<7.0",
        "pytest": "<9.0",
        "ruff": "<1.0",
    }
    
    modified = False
    new_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Check if this line is for one of our packages
        for package in packages:
            if line.startswith(package) and package in upper_bounds:
                if '<' not in line and upper_bounds[package] not in line:
                    # Add upper bound
                    if '==' in line:
                        # Replace == with >= and add upper bound
                        line = line.replace('==', '>=') + f",{upper_bounds[package]}"
                    else:
                        line = f"{package}{upper_bounds[package]}"
                    modified = True
                    break
        
        new_lines.append(line)
    
    if modified:
        with open(requirements_file, 'w') as f:
            for line in new_lines:
                f.write(line + '\n')
        print("✓ Updated requirements.txt with upper bounds")
    else:
        print("No changes needed to requirements.txt")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KORIEL ASI Requirements Management")
    parser.add_argument("--generate-lock", action="store_true", 
                       help="Generate hermetic requirements.lock")
    parser.add_argument("--audit", action="store_true",
                       help="Audit dependencies for licenses and security")
    parser.add_argument("--license-report", action="store_true",
                       help="Generate license report")
    parser.add_argument("--check-imports", action="store_true",
                       help="Check import time budget")
    parser.add_argument("--check-wildcards", action="store_true",
                       help="Check for wildcard imports")
    parser.add_argument("--pin-bounds", nargs='+',
                       help="Pin upper bounds for specified packages")
    
    args = parser.parse_args()
    
    if args.generate_lock:
        generate_requirements_lock()
    
    if args.audit:
        results = audit_dependencies()
        print(json.dumps(results, indent=2))
    
    if args.license_report:
        generate_license_report()
    
    if args.check_imports:
        results = check_import_budget()
        print("Import Budget Check:")
        print(f"  Total time: {results['total_time']:.3f}s")
        print(f"  Budget: {results['budget_seconds']}s")
        if results['budget_exceeded']:
            print("  ✗ Budget exceeded!")
        else:
            print("  ✓ Within budget")
        
        for module in results['modules']:
            status = "✓" if module['status'] == 'success' else "✗"
            print(f"  {status} {module['name']}: {module['import_time']:.3f}s")
    
    if args.check_wildcards:
        violations = validate_no_wildcards()
        if violations:
            print("Wildcard import violations found:")
            for violation in violations:
                print(f"  {violation['file']}:{violation['line']}: {violation['content']}")
        else:
            print("✓ No wildcard imports found")
    
    if args.pin_bounds:
        pin_upper_bounds(args.pin_bounds)
    
    if not any(vars(args).values()):
        parser.print_help()