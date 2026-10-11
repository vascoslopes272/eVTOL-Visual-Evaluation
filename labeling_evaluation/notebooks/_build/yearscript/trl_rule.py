"""Rule-based TRL from the evidence sentence(s): first matching rule wins. Written before it was scored against the author's review
(no tuning on the author's answers). No model involved.

 8  type certificate / certification granted
 7  piloted (crewed) flight of the aircraft
 5  flight or test of a sub-scale / scaled / model aircraft
 6  flight (incl. unmanned / tethered) of a prototype, demonstrator or full-scale aircraft, or flight with no scale given
 4  wind tunnel / simulation / bench / ground test only
 2  nothing above (concept, plan, announcement)
"""
import re

CERT = re.compile(r"(?:type certificat\w*|certification|certified).{0,60}(?:granted|received|obtained|awarded|achieved|issued)|(?:granted|received|obtained|awarded|achieved|issued).{0,60}(?:type certificat\w*|certification)", re.I)
PILOTED = re.compile(r"(?:first |maiden )?(?:piloted|crewed|manned) (?:flight|test|hover|take-?off)|(?:flown|flew|flight|tested) with (?:a |an )?(?:test )?pilot|pilot on board|pilot(?:ed)? (?:the|it|aircraft) in flight", re.I)
UNMAN = re.compile(r"\b(?:unmanned|uncrewed|tethered|remotely|remote[- ]control(?:led)?)\b", re.I)
SCALE = re.compile(r"sub-?scale|scaled|\d/\d scale|\b(?:quarter|half|third)[- ]scale|\bmodel (?:aircraft|vehicle)|\bscale model", re.I)
FLIGHT = re.compile(r"\b(?:fl(?:ight|ights|ew|own|ying|y)|hover(?:ed|ing)?|took off|take-?off|test campaign|maiden)\b", re.I)
GROUND = re.compile(r"wind[- ]tunnel|simulat\w+|bench|iron bird|static (?:test|thrust)|ground test|rig test", re.I)
FULL = re.compile(r"full[- ]?(?:scale|size)|prototype|demonstrator", re.I)


def rule_trl(quote: str) -> int:
    q = str(quote or "")
    if CERT.search(q):
        return 8
    if PILOTED.search(q) and not re.search(r"\bunmanned\b|\buncrewed\b", q, re.I):
        return 7
    if FLIGHT.search(q):
        return 5 if SCALE.search(q) else 6
    if GROUND.search(q):
        return 4
    return 2
