#!/usr/bin/env python
"""
Artifact Validator for KORIEL ASI Project
Validates experiment artifacts against required schemas.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

try:
    from jsonschema import ValidationError, validate

    JSONSCHEMA_AVAILABLE = True
except Exception:
    JSONSCHEMA_AVAILABLE = False
    logger.warning("jsonschema not available, using basic validation")


def basic_validate_metadata(
    metadata: Dict[str, Any], schema: Dict[str, Any]
) -> List[str]:
    """Basic validation without jsonschema library"""
    errors = []

    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")

    # Check basic types
    properties = schema.get("properties", {})
    for field, field_schema in properties.items():
        if field in metadata:
            expected_type = field_schema.get("type")
            value = metadata[field]

            if expected_type == "string" and not isinstance(value, str):
                errors.append(
                    f"Field '{field}' should be string, got {type(value).__name__}"
                )
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(
                    f"Field '{field}' should be integer, got {type(value).__name__}"
                )
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(
                    f"Field '{field}' should be object, got {type(value).__name__}"
                )

    return errors


def validate_metadata(metadata_file: Path, schema_file: Path) -> Dict[str, Any]:
    """Validate metadata.json against schema"""

    if not metadata_file.exists():
        return {
            "valid": False,
            "errors": [f"Metadata file not found: {metadata_file}"],
            "file": str(metadata_file),
        }

    if not schema_file.exists():
        return {
            "valid": False,
            "errors": [f"Schema file not found: {schema_file}"],
            "file": str(metadata_file),
        }

    try:
        # Load metadata
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Load schema
        with open(schema_file, "r") as f:
            schema = json.load(f)

        # Validate
        if JSONSCHEMA_AVAILABLE:
            try:
                validate(instance=metadata, schema=schema)
                errors = []
            except ValidationError as e:
                errors = [str(e)]
        else:
            errors = basic_validate_metadata(metadata, schema)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "file": str(metadata_file),
            "schema": str(schema_file),
            "metadata": metadata,
        }

    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "errors": [f"Invalid JSON in {metadata_file}: {e}"],
            "file": str(metadata_file),
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {e}"],
            "file": str(metadata_file),
        }


def validate_results(results_file: Path) -> Dict[str, Any]:
    """Validate results.json structure"""

    if not results_file.exists():
        return {
            "valid": False,
            "errors": [f"Results file not found: {results_file}"],
            "file": str(results_file),
        }

    try:
        with open(results_file, "r") as f:
            results = json.load(f)

        errors = []

        # Check required fields
        required_fields = [
            "status",
            "demo_results",
            "validation",
            "artifacts_generated",
        ]
        for field in required_fields:
            if field not in results:
                errors.append(f"Missing required field: {field}")

        # Check status value
        if "status" in results and results["status"] not in ["success", "error"]:
            errors.append(f"Invalid status: {results['status']}")

        # Check artifacts list
        if "artifacts_generated" in results:
            expected_artifacts = ["metadata.json", "results.json", "logs.txt"]
            for artifact in expected_artifacts:
                if artifact not in results["artifacts_generated"]:
                    errors.append(f"Missing expected artifact: {artifact}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "file": str(results_file),
            "results": results,
        }

    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "errors": [f"Invalid JSON in {results_file}: {e}"],
            "file": str(results_file),
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {e}"],
            "file": str(results_file),
        }


def validate_logs(logs_file: Path) -> Dict[str, Any]:
    """Validate logs.txt existence and basic structure"""

    if not logs_file.exists():
        return {
            "valid": False,
            "errors": [f"Logs file not found: {logs_file}"],
            "file": str(logs_file),
        }

    try:
        with open(logs_file, "r") as f:
            content = f.read()

        errors = []

        # Basic checks
        if len(content.strip()) == 0:
            errors.append("Logs file is empty")

        # Check for basic log structure
        lines = content.split("\n")
        log_lines = [line for line in lines if line.strip()]

        if len(log_lines) < 3:
            errors.append("Logs file appears too short (less than 3 non-empty lines)")

        # Check for log levels
        has_info = any("INFO" in line for line in log_lines)
        if not has_info:
            errors.append("No INFO level logs found")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "file": str(logs_file),
            "line_count": len(log_lines),
            "total_lines": len(lines),
        }

    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Error reading logs: {e}"],
            "file": str(logs_file),
        }


def main():
    """Main validator entry point"""
    parser = argparse.ArgumentParser(
        description="Validate KORIEL ASI experiment artifacts"
    )
    parser.add_argument(
        "experiment_dir", help="Directory containing experiment artifacts"
    )
    parser.add_argument(
        "--schema",
        default=None,
        help="Path to metadata schema (default: tools/metadata_schema.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for validation report (default: stdout)",
    )

    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir)
    if not experiment_dir.exists():
        print(f"Error: Experiment directory not found: {experiment_dir}")
        sys.exit(1)

    # Determine schema path
    if args.schema:
        schema_file = Path(args.schema)
    else:
        # Look for schema relative to this script
        script_dir = Path(__file__).parent
        schema_file = script_dir / "metadata_schema.json"

    # Validate each artifact
    results = {
        "experiment_directory": str(experiment_dir),
        "validation_timestamp": str(Path()),  # Will be replaced with actual timestamp
        "overall_valid": True,
        "artifacts": {},
    }

    # Validate metadata.json
    metadata_file = experiment_dir / "metadata.json"
    metadata_result = validate_metadata(metadata_file, schema_file)
    results["artifacts"]["metadata"] = metadata_result
    if not metadata_result["valid"]:
        results["overall_valid"] = False

    # Validate results.json
    results_file = experiment_dir / "results.json"
    results_result = validate_results(results_file)
    results["artifacts"]["results"] = results_result
    if not results_result["valid"]:
        results["overall_valid"] = False

    # Validate logs.txt
    logs_file = experiment_dir / "logs.txt"
    logs_result = validate_logs(logs_file)
    results["artifacts"]["logs"] = logs_result
    if not logs_result["valid"]:
        results["overall_valid"] = False

    # Add timestamp
    from datetime import datetime

    results["validation_timestamp"] = datetime.now().isoformat()

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Validation report written to: {args.output}")
    else:
        print(json.dumps(results, indent=2))

    # Print summary
    print("\nValidation Summary:")
    print(f"Overall Valid: {results['overall_valid']}")
    for artifact_name, artifact_result in results["artifacts"].items():
        status = "✓" if artifact_result["valid"] else "✗"
        print(f"{status} {artifact_name}: {artifact_result['valid']}")
        if not artifact_result["valid"]:
            for error in artifact_result["errors"]:
                print(f"  - {error}")

    # Exit with appropriate code
    sys.exit(0 if results["overall_valid"] else 1)


if __name__ == "__main__":
    main()
