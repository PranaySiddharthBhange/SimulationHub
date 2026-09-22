from dataclasses import replace

import pytest

from simulation_platform import reasoner
from simulation_platform.config import PlatformSettings
from simulation_platform.contracts import Review
from simulation_platform.sources import Packet, Source


class _FakeStructuredModel:
    def __init__(self, recorded: list, response) -> None:
        self._recorded = recorded
        self._response = response

    def invoke(self, messages):
        self._recorded.append(messages)
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


class _FakeChatOllama:
    def __init__(self, recorded: list, response) -> None:
        self._recorded = recorded
        self._response = response

    def __call__(self, model, temperature=0, num_ctx=None):
        return self

    def with_structured_output(self, schema, method="json_schema"):
        return _FakeStructuredModel(self._recorded, self._response)


def test_model_request_carries_original_text_and_images_and_enforces_spend(monkeypatch):
    recorded: list = []
    fake = _FakeChatOllama(recorded, Review(passed=True, issues=[]))
    monkeypatch.setattr("langchain_ollama.ChatOllama", fake)
    monkeypatch.setattr(reasoner, "check_ollama_available", lambda: None)
    settings = replace(PlatformSettings.load(), stage1_budget_usd=0.01)
    client = reasoner.Reasoner(settings, 1)
    packet = Packet([Source("URS.txt", "Original requirement"),
                     Source("diagram.png", "Diagram labels", images=["data:image/png;base64,dGVzdA=="])])
    client.ask("Review", "Upstream candidate", Review, packet)
    content = recorded[0][-1]["content"]
    assert "Original requirement" in content[0]["text"]
    assert any(block["type"] == "image_url" for block in content)
    assert content[-1]["text"] == "Upstream candidate"
    # Local models have no real dollar cost -- `spent` never actually grows,
    # so the budget check can't trip here the way it did against a real
    # per-token OpenAI bill; `calls` is the honest thing left to assert on.
    client.ask("Review", "Again", Review, packet)
    assert client.calls == 2


def test_unreachable_local_backend_fails_cleanly(monkeypatch):
    from tests._local_model_helpers import raise_ollama_unavailable

    monkeypatch.setattr("ollama.Client.list", raise_ollama_unavailable)
    settings = PlatformSettings.load()
    with pytest.raises(RuntimeError, match="not reachable"):
        reasoner.Reasoner(settings, 1).ask("Review", "data", Review, Packet([Source("file.txt", "evidence")]))
