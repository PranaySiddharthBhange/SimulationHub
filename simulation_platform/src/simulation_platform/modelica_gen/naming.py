"""Small deterministic naming helpers shared by `generation/` and
`validation/` -- kept out of either module so validation doesn't depend on
generation's internals to recompute the same instance name generation used.
"""

from __future__ import annotations

import re


def legal_identifier(name: str, fallback: str = "M") -> str:
    cleaned = "".join(ch if ch.isalnum() or ch == "_" else "" for ch in name)
    if not cleaned:
        return fallback
    if cleaned[0].isdigit():
        cleaned = fallback + cleaned
    return cleaned


def instance_name(class_name: str) -> str:
    """`part def Name` -> instance name, lowerCamel of the def name. Handles
    acronym-led names like "AHU01" (-> "ahu01", not "aHU01") the same way
    the SysML Agent's own `_instance_name` does, for the same reason.

    Guaranteed to never return `class_name` unchanged: when the source name
    is already all-lowercase (a real, legitimate case -- e.g. an engineering
    entity literally named "source" or "start"), lowerCamel-casing is a
    no-op, so `ClassName instanceName;` would declare `source source;` --
    identical tokens the real compiler can't disambiguate ("Expected
    source to be a class, but found component instead"), found live on a
    real dataset (see DECISIONS.md).
    """

    if not class_name:
        return class_name
    i = 0
    while i < len(class_name) and (class_name[i].isupper() or class_name[i].isdigit()):
        i += 1
    if i == 0:
        result = class_name
    elif i == len(class_name):
        result = class_name.lower()
    else:
        prefix_len = i - 1 if i > 1 and class_name[i - 1].isupper() else i
        result = class_name[:prefix_len].lower() + class_name[prefix_len:]

    return f"{result}_instance" if result == class_name else result


def readable_identifier(*parts: str, fallback: str) -> str:
    """Builds a real, lowerCamelCase Modelica identifier out of one or more
    pieces of free engineering text -- e.g. a requirement's own `subject`/
    `property` ("Tank 1", "diameter") -> "tank1Diameter" -- instead of a raw
    fact id like "REQ0001". Found live: a generated model opened in OMEdit's
    variable browser showed every parameter as "REQ0001", "REQ0002", ...
    -- structurally correct, but unreadable to a real engineer inspecting
    the model, since a requirement id carries no engineering meaning on its
    own.

    Preserves a word's own internal casing (e.g. "CO2" stays "CO2", not
    "Co2") -- only the FIRST letter of each non-leading word is forced to
    uppercase, everything else is left exactly as written. Falls back to
    `fallback` (the caller's own already-legal identifier, e.g. the raw
    fact id via `legal_identifier`) when every part is empty or has no
    alphanumeric content at all -- never silently returns something
    meaningless like a bare "P".
    """

    words: list[str] = []
    for part in parts:
        words.extend(re.findall(r"[A-Za-z0-9]+", part or ""))
    if not words:
        return fallback
    first, *rest = words
    identifier = first.lower() + "".join(w[:1].upper() + w[1:] for w in rest)
    return legal_identifier(identifier, fallback=fallback)
