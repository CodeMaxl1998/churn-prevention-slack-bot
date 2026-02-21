import datetime as dt
from typing import List

def iso_utc_start_of_day(d: dt.date) -> str:
    return f"{d.isoformat()}T00:00:00Z"

def daterange(start: dt.date, end_inclusive: dt.date) -> List[dt.date]:
    days = []
    cur = start
    while cur <= end_inclusive:
        days.append(cur)
        cur += dt.timedelta(days=1)
    return days

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def fmt_int(n: float) -> str:
    return f"{int(round(n)):,}"

def fmt_money(n: float, currency: str = "EUR") -> str:
    return f"{currency} {n:,.2f}"

def fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"
