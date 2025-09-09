"""Shim: re-export RCCEController from koriel.core.evaluation for legacy imports."""
import sys
import os
# Add the main src directory to path to find koriel module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from koriel.core.evaluation.rcce_controller import RCCEController
