import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from qrft import QRFTAgent


def test_retrieve_success():
    agent = QRFTAgent()
    agent.state.current_query = "autopoiesis"
    response = agent._execute_action("retrieve", agent.state.current_query)
    assert "autopoiesis maintains organization" in response
    assert any(f.predicate == "retrieved_info" for f in agent.state.facts)


def test_retrieve_failure_no_result():
    agent = QRFTAgent()
    agent.state.current_query = "nonexistent topic"
    response = agent._execute_action("retrieve", agent.state.current_query)
    assert "Insufficient evidence for" in response
    assert any(g.gap_type == "retrieval_failure" for g in agent.state.gaps)


def test_retrieve_failure_error(monkeypatch):
    agent = QRFTAgent()

    def boom(query: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(agent, "_search_corpus", boom)
    agent.state.current_query = "anything"
    response = agent._execute_action("retrieve", agent.state.current_query)
    assert "Retrieval error" in response
    assert any(g.gap_type == "retrieval_error" for g in agent.state.gaps)
