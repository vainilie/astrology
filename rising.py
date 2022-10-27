import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone

import dateutil.parser
from ndicts.ndicts import NestedDict

output = "rising.json"
nowUTC = datetime.now(timezone.utc)
nowLOC = nowUTC.astimezone()
webpage = "https://cafeastrology.com/scorpio_horoscopes.html"


def dateConv(utc):
    """convert time"""
    utc_time = dateutil.parser.parse(utc)
    return utc_time.astimezone().replace(microsecond=0)


subprocess = subprocess.Popen(f"w3m {webpage}", shell=True, stdout=subprocess.PIPE)
subprocess_return = subprocess.stdout.read().decode("utf-8")

positionsRaw = subprocess_return.split(
    "Scorpio Ascendant from 20 to 30 degrees Scorpio:"
)
positionsRaw = re.split(r"5 hours \(Eastern\)", positionsRaw[1])
positionsRaw = re.split(
    "Get your unique Personalized Horoscope for the year ahead—over 100 pages",
    positionsRaw[1],
)
positionsRaw = re.sub(r"(\w+ \d+, \d{4}) \(", r"&&& \1 (", positionsRaw[0])
positionsRaw = positionsRaw.split("&&&")
rising = []
for x in positionsRaw:
    entry = {}
    if len(x) < 5:
        pass
    else:
        x = x.split("\n")
        date = x[0].strip()
        date = date.split("(")
        about = date[1].split(")")
        aspect = about[1].strip()
        about = about[0].strip()
        date = dateConv(date[0])
        content = " ".join(x[1:])
        content = re.sub(r" +", " ", content).strip()
        entry.update({"date": date, "text": content, "info": about, "aspects": aspect})
        rising.append(entry)

rising.sort(key=lambda x: x["date"])
day = defaultdict(list)
nd = NestedDict()

for entry in rising:
    date = entry["date"]
    y = date.strftime("%Y")
    m = date.strftime("%y%m")
    w = date.strftime("%y%W")
    d = date.strftime("%y%m%d")
    day[d].append(entry)
    nd[y, m, w, d] = day[d]


with open(output, "w", encoding="utf8") as json_file:
    json.dump(
        nd.to_dict(),
        json_file,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        indent=3,
        default=str,
    )
