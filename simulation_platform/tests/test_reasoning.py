from dataclasses import replace
from types import SimpleNamespace

import pytest

from simulation_platform import reasoning
from simulation_platform.config import PlatformSettings
from simulation_platform.contracts import Review
from simulation_platform.sources import Packet, Source


def test_model_request_carries_original_text_and_images_and_enforces_spend(monkeypatch):
    recorded = []
    def parse(**kwargs):
        recorded.append(kwargs)
        return SimpleNamespace(status="completed", output_parsed=Review(passed=True, issues=[]),
                               usage=SimpleNamespace(input_tokens=1000, output_tokens=1000))
    monkeypatch.setattr(reasoning, "OpenAI", lambda **kwargs: SimpleNamespace(responses=SimpleNamespace(parse=parse)))
    settings = replace(PlatformSettings.load(), openai_api_key="test-not-a-real-key", stage1_budget_usd=0.01,
                       price_per_1k_input_usd=0.01, price_per_1k_output_usd=0.01)
    client = reasoning.Reasoner(settings, 1)
    packet = Packet([Source("URS.txt", "Original requirement"),
                     Source("diagram.png", "Diagram labels", images=["data:image/png;base64,dGVzdA=="])])
    client.ask("Review", "Upstream candidate", Review, packet)
    assert recorded[0]["store"] is False
    content = recorded[0]["input"][0]["content"]
    assert "Original requirement" in content[0]["text"]
    assert any(block["type"] == "input_image" for block in content)
    assert content[-1]["text"] == "Upstream candidate"
    with pytest.raises(RuntimeError, match="budget exhausted"):
        client.ask("Review", "Again", Review, packet)
    assert len(recorded) == 1


def test_incomplete_generation_is_not_published(monkeypatch):
    monkeypatch.setattr(reasoning, "OpenAI", lambda **kwargs: SimpleNamespace(responses=SimpleNamespace(
        parse=lambda **kwargs: SimpleNamespace(status="incomplete", output_parsed=None, usage=None))))
    settings = replace(PlatformSettings.load(), openai_api_key="test-not-a-real-key")
    with pytest.raises(RuntimeError, match="no complete"):
        reasoning.Reasoner(settings, 1).ask("Review", "data", Review, Packet([Source("file.txt", "evidence")]))
