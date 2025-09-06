"""
Metrics endpoint for KORIEL ASI observability.

Provides HTTP endpoint for system metrics, state monitoring, and health checks.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any
import logging
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from determinism import get_env_fingerprint, compute_state_hash
    DETERMINISM_AVAILABLE = True
except ImportError:
    DETERMINISM_AVAILABLE = False
    def get_env_fingerprint():
        return {"error": "determinism module not available"}
    
    def compute_state_hash(data):
        import hashlib
        import json
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

try:
    from metastate import get_current_state
except ImportError:
    def get_current_state():
        return {"error": "metastate module not available"}

try:
    import sympy
    SYMPY_AVAILABLE = True
    SYMPY_VERSION = sympy.__version__
except ImportError:
    SYMPY_AVAILABLE = False
    SYMPY_VERSION = "not_installed"


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for /metrics endpoint."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/metrics":
            self.serve_metrics()
        elif self.path == "/health":
            self.serve_health()
        else:
            self.send_error(404, "Not Found")
    
    def serve_metrics(self):
        """Serve metrics endpoint."""
        try:
            metrics = self.get_metrics()
            self.send_json_response(metrics)
        except Exception as e:
            logging.error(f"Error serving metrics: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_health(self):
        """Serve health check endpoint."""
        try:
            health = {"status": "ok", "timestamp": self.get_timestamp()}
            self.send_json_response(health)
        except Exception as e:
            logging.error(f"Error serving health: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Generate metrics data."""
        env_fingerprint = get_env_fingerprint()
        
        # Get current system state
        try:
            current_state = get_current_state()
        except Exception as e:
            current_state = {"error": str(e)}
        
        state_hash = compute_state_hash({
            "env": env_fingerprint,
            "state": current_state,
            "timestamp": self.get_timestamp()
        })
        
        metrics = {
            # Core required metrics
            "math_available": True,  # Always true for basic math
            "sympy_version": SYMPY_VERSION,
            "x_g": self.get_x_g_metric(),
            "state_hash": state_hash,
            
            # Extended metrics
            "witness_count": self.get_witness_count(),
            "glue_success_rate": self.get_glue_success_rate(),
            "glue_frontier_size": self.get_glue_frontier_size(),
            "operator_hit_counts": self.get_operator_hit_counts(),
            "theorem_tests_passed": self.get_theorem_tests_passed(),
            "seed": self.get_current_seed(),
            
            # Environment and status
            "env_fingerprint": env_fingerprint,
            "timestamp": self.get_timestamp(),
            "uptime": self.get_uptime(),
        }
        
        return metrics
    
    def get_x_g_metric(self) -> float:
        """Get x_g metric (placeholder implementation)."""
        # TODO: Implement actual x_g calculation based on current system state
        return 0.0
    
    def get_witness_count(self) -> int:
        """Get witness count metric."""
        # TODO: Implement actual witness counting
        return 0
    
    def get_glue_success_rate(self) -> float:
        """Get sheaf glue success rate."""
        # TODO: Implement actual glue success rate calculation
        return 1.0
    
    def get_glue_frontier_size(self) -> int:
        """Get current glue frontier size."""
        # TODO: Implement actual frontier size tracking
        return 0
    
    def get_operator_hit_counts(self) -> Dict[str, int]:
        """Get operator hit counts."""
        # TODO: Implement actual operator usage tracking
        return {}
    
    def get_theorem_tests_passed(self) -> int:
        """Get count of theorem tests that passed."""
        # TODO: Implement actual theorem test tracking
        return 0
    
    def get_current_seed(self) -> int:
        """Get current random seed."""
        # TODO: Get from current experiment state
        return 1337
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        # Simple uptime calculation
        try:
            with open('/proc/uptime', 'r') as f:
                return float(f.readline().split()[0])
        except:
            return 0.0
    
    def send_json_response(self, data: Dict[str, Any]):
        """Send JSON response."""
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use proper logging."""
        logging.info(f"{self.address_string()} - {format % args}")


def validate_required_metrics(metrics: Dict[str, Any]) -> None:
    """
    Validate that required metrics are present.
    
    Raises:
        AssertionError: If required metrics are missing
    """
    required_keys = {"math_available", "sympy_version", "x_g", "state_hash"}
    missing = required_keys - set(metrics.keys())
    
    if missing:
        raise AssertionError(f"Missing required metrics: {missing}")


def start_metrics_server(port: int = 8080, host: str = "localhost"):
    """Start the metrics HTTP server."""
    logging.basicConfig(level=logging.INFO)
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, MetricsHandler)
    
    logging.info(f"Starting metrics server on http://{host}:{port}")
    logging.info(f"Metrics available at: http://{host}:{port}/metrics")
    logging.info(f"Health check at: http://{host}:{port}/health")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down metrics server")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KORIEL ASI Metrics Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--test", action="store_true", help="Test metrics and exit")
    
    args = parser.parse_args()
    
    if args.test:
        # Test metrics generation and validation
        class TestHandler:
            def get_timestamp(self):
                from datetime import datetime
                return datetime.now().isoformat()
            
            def get_metrics(self):
                # Copy logic from MetricsHandler
                env_fingerprint = get_env_fingerprint()
                
                try:
                    current_state = get_current_state()
                except Exception as e:
                    current_state = {"error": str(e)}
                
                state_hash = compute_state_hash({
                    "env": env_fingerprint,
                    "state": current_state,
                    "timestamp": self.get_timestamp()
                })
                
                return {
                    "math_available": True,
                    "sympy_version": SYMPY_VERSION,
                    "x_g": 0.0,
                    "state_hash": state_hash,
                    "witness_count": 0,
                    "glue_success_rate": 1.0,
                    "glue_frontier_size": 0,
                    "operator_hit_counts": {},
                    "theorem_tests_passed": 0,
                    "seed": 1337,
                    "env_fingerprint": env_fingerprint,
                    "timestamp": self.get_timestamp(),
                    "uptime": 0.0,
                }
        
        handler = TestHandler()
        try:
            metrics = handler.get_metrics()
            validate_required_metrics(metrics)
            print("✓ Metrics validation passed")
            print(json.dumps(metrics, indent=2))
        except Exception as e:
            print(f"✗ Metrics validation failed: {e}")
            sys.exit(1)
    else:
        start_metrics_server(args.port, args.host)