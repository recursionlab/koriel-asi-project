# tests/test_ethics.py
import sys, json, numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.train import load_cfg
from src.controller import Controller
from src.model import TinyByteLM
