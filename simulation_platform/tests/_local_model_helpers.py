"""Local-model fork test helper: the equivalent of the original
`simulation_platform`'s `monkeypatch.delenv("OPENAI_API_KEY", raising=False)`
pattern for forcing the "LLM backend unavailable" boundary. This fork has
no API key to delete -- the equivalent boundary is a local Ollama server
that can't be reached, so this patches `ollama.Client.list` (what
`shared/local_models.py::check_ollama_available` calls) to raise.
"""

from __future__ import annotations


def raise_ollama_unavailable(self, *args, **kwargs):
    raise RuntimeError("simulated: local Ollama server is not reachable")
