"""
Sitrep (Situation Report) trends tracking for KORIEL ASI Project.

Implements append-only JSON lines format for tracking metrics over time
and generates markdown reports.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import statistics


def append_sitrep_entry(data: Dict[str, Any], sitrep_file: Path = None) -> None:
    """
    Append a new entry to the sitrep trends file.
    
    Args:
        data: Metrics data to append
        sitrep_file: Path to sitrep file (default: logs/sitrep_trends.jsonl)
    """
    if sitrep_file is None:
        sitrep_file = Path("logs") / "sitrep_trends.jsonl"
    
    # Ensure logs directory exists
    sitrep_file.parent.mkdir(exist_ok=True)
    
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
    
    # Append to file (one JSON object per line)
    with open(sitrep_file, "a") as f:
        f.write(json.dumps(data) + "\n")


def load_sitrep_entries(sitrep_file: Path = None) -> List[Dict[str, Any]]:
    """
    Load all sitrep entries from the trends file.
    
    Args:
        sitrep_file: Path to sitrep file (default: logs/sitrep_trends.jsonl)
        
    Returns:
        List of sitrep entries
    """
    if sitrep_file is None:
        sitrep_file = Path("logs") / "sitrep_trends.jsonl"
    
    if not sitrep_file.exists():
        return []
    
    entries = []
    with open(sitrep_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # Skip malformed lines
    
    return entries


def compute_rolling_medians(entries: List[Dict[str, Any]], window: int = 10) -> Dict[str, float]:
    """
    Compute rolling medians for key metrics.
    
    Args:
        entries: List of sitrep entries
        window: Window size for rolling calculation
        
    Returns:
        Dictionary of metric name to rolling median
    """
    if len(entries) < window:
        return {}
    
    recent_entries = entries[-window:]
    medians = {}
    
    # Extract numeric metrics
    numeric_fields = [
        "smoke_duration", "glue_success_rate", "contradiction_density",
        "x_g", "witness_count", "glue_frontier_size", "theorem_tests_passed"
    ]
    
    for field in numeric_fields:
        values = []
        for entry in recent_entries:
            if field in entry and isinstance(entry[field], (int, float)):
                values.append(entry[field])
        
        if values:
            medians[f"{field}_rolling_median"] = statistics.median(values)
    
    return medians


def generate_sitrep_markdown(output_file: Path = None) -> str:
    """
    Generate markdown sitrep report from trends data.
    
    Args:
        output_file: Path to save markdown report (default: logs/sitrep_report.md)
        
    Returns:
        Markdown content as string
    """
    if output_file is None:
        output_file = Path("logs") / "sitrep_report.md"
    
    entries = load_sitrep_entries()
    
    if not entries:
        content = "# KORIEL ASI Sitrep Report\n\nNo trend data available.\n"
    else:
        latest = entries[-1]
        rolling_medians = compute_rolling_medians(entries)
        
        content = f"""# KORIEL ASI Sitrep Report

Generated: {datetime.now().isoformat()}
Total entries: {len(entries)}

## Latest Metrics

**Timestamp:** {latest.get('timestamp', 'unknown')}
**State Hash:** `{latest.get('state_hash', 'unavailable')}`

| Metric | Value |
|--------|-------|
| X_g | {latest.get('x_g', 'N/A')} |
| Witness Count | {latest.get('witness_count', 'N/A')} |
| Glue Success Rate | {latest.get('glue_success_rate', 'N/A')} |
| Glue Frontier Size | {latest.get('glue_frontier_size', 'N/A')} |
| Theorem Tests Passed | {latest.get('theorem_tests_passed', 'N/A')} |

## Rolling Medians (Last 10 Entries)

"""
        
        if rolling_medians:
            content += "| Metric | Rolling Median |\n|--------|----------------|\n"
            for metric, value in rolling_medians.items():
                content += f"| {metric} | {value:.4f} |\n"
        else:
            content += "Insufficient data for rolling medians calculation.\n"
        
        content += f"""

## Trends Summary

- **Entries tracked:** {len(entries)}
- **First entry:** {entries[0].get('timestamp', 'unknown')}
- **Latest entry:** {latest.get('timestamp', 'unknown')}

## Environment

"""
        
        env_fingerprint = latest.get('env_fingerprint', {})
        if isinstance(env_fingerprint, dict):
            content += "| Variable | Value |\n|----------|-------|\n"
            for key, value in env_fingerprint.items():
                content += f"| {key} | {value} |\n"
        else:
            content += "Environment fingerprint not available.\n"
    
    # Save to file
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w") as f:
        f.write(content)
    
    return content


def track_experiment_metrics(metrics: Dict[str, Any]) -> None:
    """
    Track experiment metrics in sitrep trends.
    
    Args:
        metrics: Metrics dictionary from experiment
    """
    # Extract key metrics for trending
    trend_entry = {
        "timestamp": datetime.now().isoformat(),
        "x_g": metrics.get("x_g", 0.0),
        "witness_count": metrics.get("witness_count", 0),
        "glue_success_rate": metrics.get("glue_success_rate", 0.0),
        "glue_frontier_size": metrics.get("glue_frontier_size", 0),
        "theorem_tests_passed": metrics.get("theorem_tests_passed", 0),
        "state_hash": metrics.get("state_hash", ""),
        "env_fingerprint": metrics.get("env_fingerprint", {}),
    }
    
    # Add computed metrics
    if "smoke_duration" in metrics:
        trend_entry["smoke_duration"] = metrics["smoke_duration"]
    
    if "contradiction_density" in metrics:
        trend_entry["contradiction_density"] = metrics["contradiction_density"]
    
    append_sitrep_entry(trend_entry)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KORIEL ASI Sitrep Trends")
    parser.add_argument("--generate-report", action="store_true", 
                       help="Generate markdown sitrep report")
    parser.add_argument("--add-test-data", action="store_true",
                       help="Add test data to trends")
    parser.add_argument("--show-latest", action="store_true",
                       help="Show latest sitrep entry")
    
    args = parser.parse_args()
    
    if args.add_test_data:
        # Add some test data
        import time
        for i in range(5):
            test_data = {
                "x_g": 0.1 + i * 0.05,
                "witness_count": i * 2,
                "glue_success_rate": 0.8 + i * 0.02,
                "glue_frontier_size": 10 + i,
                "theorem_tests_passed": i * 3,
                "smoke_duration": 1.0 + i * 0.1,
                "contradiction_density": 0.01 + i * 0.001,
                "state_hash": f"test_hash_{i:04d}",
                "env_fingerprint": {"test": "data"}
            }
            append_sitrep_entry(test_data)
            time.sleep(0.1)  # Small delay for different timestamps
        print("✓ Added test data to sitrep trends")
    
    if args.show_latest:
        entries = load_sitrep_entries()
        if entries:
            print("Latest sitrep entry:")
            print(json.dumps(entries[-1], indent=2))
        else:
            print("No sitrep entries found")
    
    if args.generate_report:
        content = generate_sitrep_markdown()
        print("✓ Generated sitrep report at logs/sitrep_report.md")
        print("\n" + "="*50)
        print(content)