"""`naming.py` is shared by `generation/` and `validation/` -- tested
directly here, not just indirectly through generator fixtures.
"""

from __future__ import annotations

from simulation_platform.modelica_gen.naming import instance_name, legal_identifier


def test_instance_name_lowercases_leading_run() -> None:
    assert instance_name("TankDemo") == "tankDemo"
    assert instance_name("AHU01") == "ahu01"  # entirely uppercase/digits
    assert instance_name("CO2Sensor01") == "co2Sensor01"  # acronym-led, new word follows


def test_instance_name_never_equals_the_class_name() -> None:
    """Found live on a real dataset (see DECISIONS.md): a class already
    named lowercase (e.g. a real engineering entity called "source") made
    lowerCamel-casing a no-op, producing `source source;` -- identical
    tokens the real compiler can't disambiguate."""

    for already_lowercase in ("source", "start", "stop", "shut"):
        result = instance_name(already_lowercase)
        assert result != already_lowercase
        assert result == f"{already_lowercase}_instance"


def test_instance_name_empty_string_is_a_noop() -> None:
    assert instance_name("") == ""


def test_legal_identifier_replaces_illegal_characters() -> None:
    assert legal_identifier("Tank 1 (main)") == "Tank1main"
    assert legal_identifier("123abc") == "M123abc"
    assert legal_identifier("", fallback="X") == "X"
