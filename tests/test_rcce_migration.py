import numpy as np

def test_rcce_imports_and_basic_methods():
    # Import from new location
    from koriel.core.evaluation.rcce_controller import RCCEController

    c = RCCEController(d_model=16)

    # Build a minimal fake model_state
    model_state = {
        'activations': {'output': np.zeros((1, 16))},
        'attention_maps': {'layer_0': np.zeros((1, 1, 1))}
    }
    geom = {'curvature': 0.0, 'torsion': 0.0}

    signals = c.process_step(model_state, geom, loss=0.1)
    assert 'learning_rate_modifier' in signals

    # Import via shim path (old location)
    from rcce_minimal.src.controller import RCCEController as RCCEShim  # type: ignore

    s = RCCEShim(d_model=8)
    ms2 = {'activations': {'output': np.zeros((1, 8))}, 'attention_maps': {'layer_0': np.zeros((1, 1, 1))}}
    s.process_step(ms2, geom, loss=0.2)
