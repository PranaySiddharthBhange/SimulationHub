"""Recognized Modelica/SI unit strings -- a small allow-list, not a full
unit-algebra checker (see `tools/modelica/unit_validator.py`). Extend this
set as new domains are added; it never flags a real unit it simply hasn't
seen yet as more datasets are added, it only catches an obviously-wrong or
malformed unit string.

Magnetic-circuit units (Wb, T, H, A/m) added proactively -- checked
directly against `new direction.txt`'s Domain 3 vocabulary (coil, magnetic
flux, reluctance) rather than waiting for a live run to find the gap.
"""

RECOGNIZED_UNITS = {
    "", "1", "m", "m2", "m3", "m3/s", "s", "ms", "min", "h",
    "Pa", "kPa", "bar", "degC", "K", "ppm", "kg", "g", "kg/s", "kg/m3",
    "W", "kW", "J", "V", "A", "Ohm", "N", "rad", "deg", "%", "Hz",
    # Magnetic circuit (Level 3)
    "Wb", "T", "H", "A/m", "A.turn", "A.turn/Wb",
}
