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
    date = utc_time.astimezone().replace(microsecond=0)
    date = date
    return date


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
        date1 = dateConv(date[0].strip())
        date = about.split("to")
        date_start = dateConv(date[0].strip())
        date_end = dateConv(date[1].strip())
        content = " ".join(x[1:])
        content = re.sub(r" +", " ", content).strip()
        entry.update(
            {
                "date": date1,
                "text": content,
                "date-st": date_start,
                "date-end": date_end,
                "_date": date1.strftime("%YY%mM%dD%Hh%Mm"),
                "_start": date_start.strftime("%YY%mM%dD%Hh%Mm"),
                "_end": date_end.strftime("%YY%mM%dD%Hh%Mm"),
                "aspects": aspect,
            }
        )

        rising.append(entry)

rising.sort(key=lambda x: x["date"])
month = defaultdict(list)
nd = NestedDict()

for idx, entry in enumerate(rising):
    date = entry["date-st"]
    y = int(date.strftime("%Y"))
    m = int(date.strftime("%Y%m"))

    date1 = entry["date-end"]
    y1 = int(date1.strftime("%Y"))
    m1 = int(date1.strftime("%Y%m"))
    if int(m) != int(m1):
        if int(y) != int(y1):
            mx = int(str(m)[4:])
            my = int(str(m1)[4:])
            while int(mx) <= int(12):
                month[int(str(y) + str(mx))].append(entry)
                nd[y, int(str(y) + str(mx))] = month[int(str(y) + str(mx))]
                mx += 1
            while my >= 1:
                month[int(str(y1) + str(my))].append(entry)
                nd[y1, int(str(y1) + str(my))] = month[int(str(y1) + str(my))]
                my -= 1
        else:
            mx = int(m1)
            while mx >= int(m):
                month[mx].append(entry)
                nd[y, mx] = month[mx]
                mx -= 1
    else:
        month[m].append(entry)
        nd[y, m] = month[m]
    print(f"\n---{idx}---\n")
    print(entry)

final = nd.to_dict()
with open(output, "w", encoding="utf8") as json_file:
    json.dump(
        final,
        json_file,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        indent=3,
        default=str,
    )
