import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Tuple

from app.reporting.ads_client import AggregateRow
from app.reporting.utils import safe_div

@dataclass
class KPI:
    impressions: int
    streamed_impressions: int
    clicks: int
    spend: float
    ctr: float
    e_cpcl: float

def aggregate_kpis(rows: List[AggregateRow]) -> KPI:
    imps = 0
    simps = 0
    clicks = 0
    spend = 0.0
    for r in rows:
        imps += int(r.stats.get("IMPRESSIONS", 0))
        simps += int(r.stats.get("STREAMED_IMPRESSIONS", 0))
        clicks += int(r.stats.get("CLICKS", 0))
        spend += float(r.stats.get("SPEND", 0.0))
    ctr = safe_div(clicks, imps)
    e_cpcl = safe_div(spend, clicks)
    return KPI(impressions=imps, streamed_impressions=simps, clicks=clicks, spend=spend, ctr=ctr, e_cpcl=e_cpcl)

def top_entities(rows: List[AggregateRow], metric: str, n: int = 8) -> List[Tuple[str, float]]:
    agg: Dict[str, float] = {}
    name_by_id: Dict[str, str] = {}
    for r in rows:
        key = r.entity_id
        name_by_id[key] = r.entity_name
        agg[key] = agg.get(key, 0.0) + float(r.stats.get(metric, 0.0))
    ranked = sorted(agg.items(), key=lambda x: x[1], reverse=True)[:n]
    return [(name_by_id[k], v) for k, v in ranked]

def daily_series(rows: List[AggregateRow], metric: str) -> List[Tuple[dt.date, float]]:
    by_day: Dict[dt.date, float] = {}
    for r in rows:
        d = dt.datetime.strptime(r.start_time, "%Y-%m-%dT%H:%M:%SZ").date()
        by_day[d] = by_day.get(d, 0.0) + float(r.stats.get(metric, 0.0))
    return sorted(by_day.items(), key=lambda x: x[0])
