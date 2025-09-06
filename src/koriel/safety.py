"""Safety module for resource monitoring and experiment gating."""

import os
import time
import psutil
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ResourceLimits:
    """Resource limits for safe execution."""
    max_execution_time: int = 300  # seconds
    max_memory_mb: int = 1024      # megabytes
    max_output_files: int = 10     # number of files
    max_output_size_mb: int = 100  # megabytes
    
@dataclass
class SafetyConfig:
    """Safety configuration for experiments."""
    allow_self_modification: bool = False
    allow_file_creation: bool = True
    allow_network_access: bool = False
    require_confirmation: bool = True

class ResourceMonitor:
    """Monitor system resources during execution."""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.start_time = None
        self.initial_memory = None
        self.process = psutil.Process()
        
    def start_monitoring(self):
        """Start resource monitoring."""
        self.start_time = time.time()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
    def check_limits(self) -> Dict[str, Any]:
        """Check if any resource limits are exceeded."""
        if self.start_time is None:
            return {'status': 'not_started'}
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        violations = []
        
        # Check time limit
        if elapsed_time > self.limits.max_execution_time:
            violations.append(f"Time limit exceeded: {elapsed_time:.1f}s > {self.limits.max_execution_time}s")
            
        # Check memory limit
        if current_memory > self.limits.max_memory_mb:
            violations.append(f"Memory limit exceeded: {current_memory:.1f}MB > {self.limits.max_memory_mb}MB")
            
        return {
            'status': 'violation' if violations else 'ok',
            'elapsed_time': elapsed_time,
            'current_memory_mb': current_memory,
            'violations': violations
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        if self.start_time is None:
            return {'status': 'not_started'}
            
        elapsed_time = time.time() - self.start_time
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()
        
        return {
            'elapsed_time': elapsed_time,
            'memory_mb': memory_info.rss / 1024 / 1024,
            'memory_peak_mb': memory_info.peak_wss / 1024 / 1024 if hasattr(memory_info, 'peak_wss') else None,
            'cpu_percent': cpu_percent,
            'num_threads': self.process.num_threads()
        }

class ExperimentSafetyGate:
    """Safety gate for experiment execution."""
    
    def __init__(self):
        self.experiment_configs = {}
        
    def load_experiment_config(self, experiment_path: Path) -> Dict[str, Any]:
        """Load experiment configuration with safety settings."""
        config_path = experiment_path.with_suffix('.yaml')
        
        if not config_path.exists():
            # Default safety config for experiments without explicit config
            return {
                'safety': {
                    'max_execution_time': 300,
                    'max_memory_mb': 1024,
                    'max_output_files': 5,
                    'max_output_size_mb': 50
                },
                'resources': {
                    'cpu_intensive': True,
                    'memory_intensive': True,
                    'disk_intensive': False
                },
                'permissions': {
                    'allow_self_modification': False,
                    'allow_file_creation': True,
                    'allow_network_access': False
                },
                'warnings': [
                    "No experiment config found - using default safety limits",
                    "Monitor resource usage during execution"
                ]
            }
            
        # Load from YAML file
        from .io import load_config
        return load_config(config_path)
        
    def check_safety_requirements(self, experiment_config: Dict[str, Any], 
                                 allow_experiments: bool = False) -> Dict[str, Any]:
        """Check if experiment meets safety requirements."""
        if not allow_experiments:
            return {
                'allowed': False,
                'reason': 'Experiments require explicit --allow-experiments flag for safety'
            }
            
        safety_config = experiment_config.get('safety', {})
        resource_config = experiment_config.get('resources', {})
        warnings = experiment_config.get('warnings', [])
        
        # Check if this is a high-risk experiment
        high_risk_indicators = [
            resource_config.get('cpu_intensive', False),
            resource_config.get('memory_intensive', False),
            safety_config.get('max_execution_time', 0) > 600,  # > 10 minutes
            safety_config.get('max_memory_mb', 0) > 2048,      # > 2GB
        ]
        
        risk_level = 'high' if any(high_risk_indicators) else 'medium'
        
        return {
            'allowed': True,
            'risk_level': risk_level,
            'warnings': warnings,
            'safety_config': safety_config,
            'resource_config': resource_config
        }
        
    def create_resource_monitor(self, experiment_config: Dict[str, Any]) -> ResourceMonitor:
        """Create resource monitor from experiment config."""
        safety_config = experiment_config.get('safety', {})
        
        limits = ResourceLimits(
            max_execution_time=safety_config.get('max_execution_time', 300),
            max_memory_mb=safety_config.get('max_memory_mb', 1024),
            max_output_files=safety_config.get('max_output_files', 10),
            max_output_size_mb=safety_config.get('max_output_size_mb', 100)
        )
        
        return ResourceMonitor(limits)

def check_system_resources() -> Dict[str, Any]:
    """Check current system resource availability."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_count = psutil.cpu_count()
    
    return {
        'memory_total_gb': memory.total / 1024 / 1024 / 1024,
        'memory_available_gb': memory.available / 1024 / 1024 / 1024,
        'memory_percent_used': memory.percent,
        'disk_total_gb': disk.total / 1024 / 1024 / 1024,
        'disk_free_gb': disk.free / 1024 / 1024 / 1024,
        'disk_percent_used': (disk.used / disk.total) * 100,
        'cpu_count': cpu_count,
        'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
    }