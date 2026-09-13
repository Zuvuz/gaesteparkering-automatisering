import re
from datetime import datetime, timedelta


def parse_message(text, now=None):
    if now is None:
        now = datetime.now()

    match = re.match(r"^(.+?)\s+kommer\b(.*)$", text.strip(), re.IGNORECASE)
    if not match:
        return None

    name = match.group(1).strip().lower()
    rest = match.group(2).strip()

    times = re.findall(r"kl\.?\s*(\d{1,2})(?::(\d{2}))?", rest, re.IGNORECASE)
    dates = re.findall(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?", rest)

    if "i morgen" in rest.lower():
        base_date = (now + timedelta(days=1)).date()
    elif "i dag" in rest.lower():
        base_date = now.date()
    else:
        base_date = None

    def make_date(day, month, year_str):
        day, month = int(day), int(month)
        if year_str:
            year = int(year_str)
            if year < 100:
                year += 2000
        else:
            year = now.year
        d = datetime(year, month, day)
        if not year_str and d.date() < now.date():
            d = datetime(year + 1, month, day)
        return d

    def with_time(base_dt, hour, minute_str):
        return base_dt.replace(hour=int(hour), minute=int(minute_str) if minute_str else 0, second=0, microsecond=0)

    if len(dates) == 2 and len(times) == 2:
        start = with_time(make_date(*dates[0]), *times[0])
        end = with_time(make_date(*dates[1]), *times[1])
    elif base_date is not None and len(times) == 2:
        day_dt = datetime.combine(base_date, datetime.min.time())
        start = with_time(day_dt, *times[0])
        end = with_time(day_dt, *times[1])
    elif base_date is not None and len(times) == 1:
        day_dt = datetime.combine(base_date, datetime.min.time())
        start = with_time(day_dt, *times[0])
        end = None
    elif len(times) == 1 and not dates and base_date is None:
        start = with_time(now, *times[0])
        end = None
    else:
        return None

    return {"name": name, "start": start, "end": end}


if __name__ == "__main__":
    print(parse_message("Mor kommer kl 13"))
    print(parse_message("Mor kommer i morgen kl 10 til kl 20"))
    print(parse_message("Mor kommer den 15/9 kl 14 til 18/9 kl 10"))
    print(parse_message("noget der ikke giver mening"))
