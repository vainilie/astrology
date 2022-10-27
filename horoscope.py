import json
import re
from datetime import datetime, timezone
import dateutil.parser

output = "horoscope.json"
nowUTC = datetime.now(timezone.utc)
n = nowUTC.astimezone()

aq_tomorrow = "https://cafeastrology.com/aquariusdailyhoroscopetom.html"
aq_today = "https://cafeastrology.com/aquariusdailyhoroscope.html"
aq_yesterday = "https://cafeastrology.com/aquariusdailyhoroscopey.html"
aq_aftertom = (
    "https://cafeastrology.com/aquarius-daily-horoscope-day-after-tomorrow.html"
)

sc_tomorrow = "https://cafeastrology.com/scorpiodailyhoroscopetom.html"
sc_today = "https://cafeastrology.com/scorpiodailyhoroscope.html"
sc_yesterday = "https://cafeastrology.com/scorpiodailyhoroscopey.html"
sc_aftertom = (
    "https://cafeastrology.com/scorpio-daily-horoscope-day-after-tomorrow.html"
)


def dateConv(utc):
    """convert time"""
    utc_time = dateutil.parser.parse(utc)
    return utc_time.astimezone().replace(microsecond=0)


def get_month(s, split1):
    s_month = s.split(split1)
    s_month = s_month[1].split("More:")
    s_month = s_month[0].replace("\n\n", "|").replace("\n", " ").split("|")
    s_month = "\n".join(s_month)
    return s_month


def get_todayall(s):
    array = {}
    all_today = s.replace("All Zodiac SignsAll Zodiac Signs", "")
    all_today_date = re.search(r"[\w,]* \d+, \d{4}", all_today).group()
    all_today_date = dateConv(all_today_date)
    array.update({"date": all_today_date})
    all_today_sts = re.search(
        r"^.*Creativity: \w+ ~ Love: \w+ ~ Business: \w+", all_today, re.M
    )
    array.update({"stats": all_today_sts.group()})
    all_today = all_today.split((all_today_sts).group())
    all_today = re.sub(r"[\s]+", " ", all_today[0])
    all_today = all_today.split("• ")
    all_today = "\n• ".join(all_today[1:])
    all_today = "• " + all_today
    array.update({"text": all_today})
    return array


def get_today(s, split1):
    array = {}
    s_today = s.split(split1)
    s_date = re.search(r"[\w,]* \d+, \d{4}", s_today[0]).group()
    s_date = dateConv(s_date)
    array.update({"date": s_date})
    s_stat = re.search(
        r"^.*Creativity: \w+ ~ Love: \w+ ~ Business: \w+", s_today[1], re.M
    )
    array.update({"stats": s_stat.group()})
    s_today = s_today[1].split(s_stat.group())
    s_today = re.sub(r"\n", " ", s_today[0])
    array.update({"text": s_today})
    return array


def get_web(web):
    import subprocess

    subprocess = subprocess.Popen(f"w3m {web}", shell=True, stdout=subprocess.PIPE)
    subprocess_return = subprocess.stdout.read().decode("utf-8")
    aquario = subprocess_return.split("glyphtitle]")
    aquarius = re.split("━+", aquario[1])
    return aquarius


aquarius = get_web(aq_today)
aq_month = get_month(aquarius[2], "for Aquarius:")
aq_year = get_month(aquarius[3], "[svg]")
aq_love = get_month(aquarius[4], "[svg]")
aq_today = get_today(aquarius[0], "[svg]")
all_today = get_todayall(aquarius[1])


aquarius1 = get_web(aq_tomorrow)
aquarius1 = re.split(r"The Astrology of Tomorrow – All Signs", aquarius1[0])
aq_tomorrow = get_today(aquarius1[0], "[svg]")
all_tomorrow = get_todayall(aquarius1[1])

aquarius2 = get_web(aq_yesterday)
aquarius2 = re.split(r"The Astrology of Yesterday – All Signs", aquarius2[0])
aq_yesterday = get_today(aquarius2[0], "[svg]")
all_yesterday = get_todayall(aquarius2[1])

aquarius3 = get_web(aq_aftertom)
aquarius3 = re.split(
    r"The Astrology of the Day After Tomorrow – All Signs", aquarius3[0]
)
aq_aftert = get_today(aquarius3[0], "[svg]")
all_aftert = get_todayall(aquarius3[1])

####

scorpio = get_web(sc_today)
sc_month = get_month(scorpio[0], "for Scorpio:")
sc_year = get_month(scorpio[1], "[svg]")
sc_love = get_month(scorpio[2], "Scorpio Love HoroscopeScorpio Love Horoscope")
sc_today = get_today(scorpio[0], "[svg]")

scorpio1 = get_web(sc_tomorrow)
scorpio1 = re.split("The Astrology of Tomorrow – All Signs", scorpio1[0])
sc_tomorrow = get_today(scorpio[0], "[svg]")

scorpio2 = get_web(sc_yesterday)
scorpio2 = re.split("The Astrology of Yesterday – All Signs", scorpio2[0])
sc_yesterday = get_today(scorpio2[0], "[svg]")

scorpio3 = get_web(sc_aftertom)
scorpio3 = re.split(
    "The Astrology of the Day After Tomorrow – – All Signs", scorpio3[0]
)
sc_aftert = get_today(scorpio3[0], "[svg]")

horoscope = {}
sco = {}
forall = {}
aqua = {}
sco.update(
    {
        "today": sc_today,
        "tomorrow": sc_tomorrow,
        "after": sc_aftert,
        "yesterday": sc_yesterday,
        "month": sc_month,
        "year": sc_year,
        "love": sc_love,
    }
)

aqua.update(
    {
        "today": aq_today,
        "tomorrow": aq_tomorrow,
        "after": aq_aftert,
        "yesterday": aq_yesterday,
        "month": aq_month,
        "year": aq_year,
        "love": sc_love,
    }
)
forall.update(
    {
        "today": all_today,
        "tomorrow": all_tomorrow,
        "after": all_aftert,
        "yesterday": all_yesterday,
    }
)

horoscope.update({"all": forall, "scorpio": sco, "aquarius": aqua})

with open(output, "w", encoding="utf8") as json_file:
    json.dump(
        horoscope,
        json_file,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        indent=3,
        default=str,
    )
