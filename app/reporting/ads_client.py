import datetime as dt
import math
import random
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.reporting.utils import clamp, daterange, iso_utc_start_of_day, safe_div

@dataclass
class AggregateRow:
    entity_type: str
    entity_id: str
    entity_name: str
    entity_status: str
    start_time: str
    end_time: str
    stats: Dict[str, float]
    parent_entity: Optional[Dict[str, Any]] = None

@dataclass
class AggregateReport:
    report_start: str
    report_end: str
    granularity: str
    entity_type: str
    rows: List[AggregateRow]
    continuation_token: Optional[str] = None
    warnings: Optional[List[str]] = None

class MockSpotifyAdsApi:
    def get_aggregate_report_by_ad_account_id(
        self,
        ad_account_id: str,
        entity_type: str,
        fields: List[str],
        report_start: str,
        report_end: str,
        granularity: str = "DAY",
        include_parent_entity: bool = False,
        limit: int = 50,
        continuation_token: Optional[str] = None,
    ) -> AggregateReport:
        start_date = dt.datetime.strptime(report_start, "%Y-%m-%dT%H:%M:%SZ").date()
        end_date = dt.datetime.strptime(report_end, "%Y-%m-%dT%H:%M:%SZ").date()
        days = daterange(start_date, end_date)

        num_entities = {"CAMPAIGN": 6, "AD_SET": 10, "AD": 20, "AD_ACCOUNT": 1}.get(entity_type, 6)
        entities = []
        for i in range(num_entities):
            entities.append({
                "id": str(uuid.uuid4()),
                "name": f"{entity_type.title().replace('_',' ')} {i+1}",
                "status": "ACTIVE" if i % 7 != 0 else "PAUSED",
            })

        weights = [1.0 / (i + 1) ** 1.15 for i in range(num_entities)]
        wsum = sum(weights)
        weights = [w / wsum for w in weights]

        rows: List[AggregateRow] = []
        base_imps_per_day = random.randint(250_000, 900_000)
        base_ctr = random.uniform(0.002, 0.012)
        base_cpm = random.uniform(6.0, 18.0)
        streamed_share = random.uniform(0.65, 0.95)

        for day_idx, day in enumerate(days):
            trend = 1.0 + 0.15 * math.sin(day_idx / 6.0)
            noise = random.uniform(0.85, 1.15)
            day_imps = int(base_imps_per_day * trend * noise)

            for ent_idx, ent in enumerate(entities):
                ent_factor = weights[ent_idx] * random.uniform(0.7, 1.3)
                imps = max(0, int(day_imps * ent_factor))

                streamed_imps = int(imps * streamed_share)
                clicks = int(imps * clamp(base_ctr * random.uniform(0.7, 1.4), 0.0005, 0.03))
                spend = (imps / 1000.0) * clamp(base_cpm * random.uniform(0.75, 1.35), 2.0, 40.0)

                completes = int(streamed_imps * random.uniform(0.12, 0.45))
                completion_rate = safe_div(completes, streamed_imps)

                ctr = safe_div(clicks, imps)
                e_cpcl = safe_div(spend, clicks)

                stats: Dict[str, float] = {}
                for f in fields:
                    if f == "IMPRESSIONS":
                        stats[f] = imps
                    elif f == "STREAMED_IMPRESSIONS":
                        stats[f] = streamed_imps
                    elif f == "CLICKS":
                        stats[f] = clicks
                    elif f == "SPEND":
                        stats[f] = spend
                    elif f == "CTR":
                        stats[f] = ctr
                    elif f == "COMPLETES":
                        stats[f] = completes
                    elif f == "COMPLETION_RATE":
                        stats[f] = completion_rate
                    elif f == "E_CPCL":
                        stats[f] = e_cpcl
                    else:
                        stats[f] = 0.0

                parent = None
                if include_parent_entity and entity_type in ("AD", "AD_SET"):
                    parent = {"entity_type": "CAMPAIGN", "entity_id": str(uuid.uuid4()), "entity_name": "Parent Campaign"}

                rows.append(
                    AggregateRow(
                        entity_type=entity_type,
                        entity_id=ent["id"],
                        entity_name=ent["name"],
                        entity_status=ent["status"],
                        start_time=iso_utc_start_of_day(day),
                        end_time=iso_utc_start_of_day(day + dt.timedelta(days=1)),
                        stats=stats,
                        parent_entity=parent,
                    )
                )

        return AggregateReport(
            report_start=report_start,
            report_end=report_end,
            granularity=granularity,
            entity_type=entity_type,
            rows=rows[: limit * len(days)],
            continuation_token=None,
            warnings=[],
        )
