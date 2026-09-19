"""Domain skill: Room CO2 Ventilation Control. Appended to a reasoning
prompt (not called as a function) -- see `new direction.txt` §11, Domain 2.

Scope note, taken directly from the spec: "HVAC is not in the domain
scope." This is deliberately narrow to the single closed feedback loop
the PRD tests (L2: "Closed-loop feedback: disturbance, sensor, control
law, actuator acting back on the process") -- not a general HVAC/thermal
comfort/duct-network modeling skill. Do not let a reasoning stage expand
this into full air-handling-unit design, chiller plants, or thermal
comfort; those are out of scope for this problem class.
"""

SKILL = """\
DOMAIN: Room CO2 Ventilation Control (single-zone closed-loop feedback control)

SCOPE BOUNDARY: this is about ONE feedback loop -- a room's CO2 \
concentration, a disturbance that raises it, a sensor that measures it, a \
control law that reacts to it, and an actuator that lowers it by \
increasing outdoor-air exchange. It is explicitly NOT a general HVAC \
system model: do not introduce thermal comfort, heating/cooling coils, \
chiller plants, or a full duct network unless the problem statement \
itself describes one. If in doubt, model the smallest system that closes \
the loop: room -> sensor -> controller -> actuator -> room.

CORE PHYSICS
A room (zone) is treated as a single well-mixed air volume. CO2 \
concentration in that volume rises due to a disturbance -- almost always \
occupancy (people exhale CO2 at a roughly per-person rate) -- and falls due \
to ventilation: outdoor air (with a much lower, roughly constant CO2 \
concentration) is exchanged with the room's air at some airflow rate, \
diluting the room's concentration. This is a mass balance on CO2: the rate \
of change of room CO2 mass equals the generation rate (from occupancy) \
minus the net removal rate (proportional to airflow rate times the \
concentration difference between room air and incoming outdoor air). \
Increasing airflow (via a fan or an opening damper) increases removal; it \
does not change the generation rate.

ROLES TO DISTINGUISH
- The process (the room/zone): a single dynamic state, CO2 concentration, \
governed by the mass-balance equation above.
- The disturbance (occupancy or another CO2 source): an input to the \
process the controller cannot directly command, only react to.
- The sensor (a CO2 sensor): measures the process state, generally with \
some real response characteristic (a sensor is not usually instantaneous \
and perfect -- if the problem states a response time or accuracy, that \
belongs on the sensor, not the room).
- The control law (a controller, e.g. proportional/PI, an on/off \
hysteresis controller, or a staged/discrete controller): compares the \
measured CO2 against a setpoint or threshold and computes a commanded \
ventilation rate or fan/damper position.
- The actuator (a fan, a damper, or both together): acts on the process by \
changing the actual airflow rate, which feeds back into the room's mass \
balance -- this is the "actuator acting back on the process" the closed \
loop requires; a model where the actuator's commanded position never \
actually changes the room's dynamics is not a closed loop, just an open \
one dressed up to look closed.

WORKED EXAMPLE
Room CO2 rises above a threshold because occupancy increased. The CO2 \
sensor reports the rising concentration. The controller — say, a simple \
proportional law — computes a higher required outdoor-air fraction (or \
fan speed) roughly proportional to how far CO2 is above setpoint. The fan \
speeds up (or a damper opens further), raising the room's actual outdoor- \
air exchange rate. That higher airflow increases the CO2 removal term in \
the room's own mass balance, so its concentration falls back toward \
setpoint over time -- at which point the controller relaxes its command. \
The correct behavior to check in simulation is exactly this: does an \
occupancy step cause CO2 to rise, does the controller visibly react by \
commanding more ventilation, and does that in turn bring CO2 back down --
not merely "does the model produce some numbers without error."

WHAT THIS IMPLIES FOR MODELING
A faithful model needs: (1) a real CO2 mass-balance differential equation \
on the room, driven by a real occupancy/generation input, not a frozen \
constant; (2) a control law that reads the room's own state (through a \
sensor with a defined causality, not by reaching into the room directly) \
and produces a real actuator command; (3) the actuator's command must \
actually appear as a term in the room's own balance equation (e.g. the \
airflow rate used in the removal term is the SAME variable the actuator \
sets) -- if the loop isn't wired end-to-end like this, "closed-loop \
feedback" hasn't actually been modeled, only asserted.
"""
