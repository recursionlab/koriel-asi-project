"""Test CLI functionality."""

import subprocess
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestCLI:
    """Test the command-line interface."""
    
    def test_cli_status(self):
        """Test CLI status command."""
        result = subprocess.run([
            sys.executable, 'koriel-run', 'status'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Koriel ASI System Status' in result.stdout
        
    def test_cli_dry_run(self):
        """Test CLI dry run mode."""
        result = subprocess.run([
            sys.executable, 'koriel-run', 'run', '--dry-run'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'DRY RUN MODE' in result.stdout
        
    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run([
            sys.executable, 'koriel-run', '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Koriel ASI' in result.stdout
        
    def test_cli_experiment_safety(self):
        """Test that experiments require explicit flag."""
        result = subprocess.run([
            sys.executable, 'koriel-run', 'experiment', '--name', 'test'
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        assert 'require explicit --allow-experiments' in result.stdout