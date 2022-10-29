import json
import re
import subprocess
from datetime import datetime, timezone

import dateutil.parser

output = "transits.json"
nowUTC = datetime.now(timezone.utc)
nowLOC = nowUTC.astimezone()
webpage = "https://horoscopes.astro-seek.com/current-planets-astrology-transits-planetary-positions"


def symbols(string):
    string = (
        string.replace("Sun", "☉")
        .replace("Node", "☊")
        .replace("Mercury", "☿")
        .replace("Venus", "♀")
        .replace("Mars", "♂")
        .replace("Jupiter", "♃")
        .replace("Saturn", "♄")
        .replace("Uranus", "♅")
        .replace("Neptune", "♆")
        .replace("Pluto", "♇")
        .replace("Chiron", "⚷")
        .replace("Lilith", "⚸")
        .replace("Moon", "☾")
    )
    string = (
        string.replace("Aries", "♈")
        .replace("Taurus", "♉")
        .replace("Gemini", "♊")
        .replace("Cancer", "♋")
        .replace("Leo", "♌")
        .replace("Virgo", "♍")
        .replace("Libra", "♎")
        .replace("Scorpio", "♏")
        .replace("Sagittarius", "♐")
        .replace("Capricorn", "♑")
        .replace("Aquarius", "♒")
        .replace("Pisces", "♓")
    )
    return string


def dateConv(utc):
    """convert time"""
    utc = re.sub(r"\(UT|\)|,", "", utc)
    utc_time = dateutil.parser.parse(utc)
    return utc_time.astimezone().replace(microsecond=0)


subprocess = subprocess.Popen(f"w3m {webpage}", shell=True, stdout=subprocess.PIPE)
subprocess_return = subprocess.stdout.read().decode("utf-8")

positionsRaw = subprocess_return.split("[symbols-me]")
date = re.search(
    r"\w+ \d+\, \d+\, \d+\:\d+ \(UT\/GMT\)", positionsRaw[0], re.IGNORECASE
)
positionsRaw = positionsRaw[0].split("[OK]\n")
updated = dateConv(date.group()).strftime("%YY%mM%dD%Hh%Mm")

positions = re.sub(r"\n \n", r"|", positionsRaw[1])
positions = re.sub(r"\nR\n", r"Rx|", positions)
positions = re.sub(r"\|$", "", positions)
positions = positions.split("|")

current = []
for planets in positions:
    pla = {}
    planets = planets.split("\n")
    planets[0] = re.sub(r"([A-Z][^A-Z]+)[A-Z][^A-Z \(\)]+", r"\1", planets[0])
    pla.update(
        {
            "pl": symbols(planets[0]),
            "sg": symbols(planets[1]),
            "gr": planets[2],
        }
    )
    if "Rx" in planets[3]:
        pla.update({"rx": True})
    else:
        pla.update({"rx": False})
    current.append(pla)

transits = {}
transits.update({"date": str(updated), "planets": current, "source": webpage})

with open(output, "w", encoding="utf8") as json_file:
    json.dump(
        transits,
        json_file,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        indent=3,
        default=str,
    )
