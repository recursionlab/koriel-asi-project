def test_presence_import_and_behavior():
    from koriel.core.evaluation.presence import presence_certificate

    metrics = {"E": [1.0, 0.8, 0.7, 0.6], "rc": [0.1, 0.12, 0.2, 0.2], "ups_rate": 0.5}
    cfg = {"presence_window_frac": 0.25, "upsilon": {"rate_min": 0.0, "rate_max": 1.0}, "xi": {"eps_xi": 0.1}}

    status, cert = presence_certificate(metrics, cfg, ethics_viol=0, xi_hist=[0.0])
    assert isinstance(status, bool)

    # Legacy import path
    from src.presence import presence_certificate as legacy_presence  # type: ignore
    status2, cert2 = legacy_presence(metrics, cfg, ethics_viol=0, xi_hist=[0.0])
    assert status2 == status
