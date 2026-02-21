import datetime as dt
from typing import Any, Dict, List, Tuple

from slack_sdk import WebClient

from app.reporting.ads_client import MockSpotifyAdsApi
from app.reporting.metrics import aggregate_kpis, daily_series, top_entities
from app.reporting.pdf import build_pdf_report
from app.reporting.utils import fmt_int, fmt_money, fmt_pct, iso_utc_start_of_day

DEFAULT_FIELDS = ["IMPRESSIONS", "STREAMED_IMPRESSIONS", "CLICKS", "SPEND", "CTR", "E_CPCL"]

mock_ads_api = MockSpotifyAdsApi()

def compute_kpi_and_report(case: Dict[str, Any], days_back: int = 30):
    start_date = dt.date.today() - dt.timedelta(days=days_back)
    end_date = dt.date.today() - dt.timedelta(days=1)
    entity_type = "AD_SET"
    fields = DEFAULT_FIELDS

    report = mock_ads_api.get_aggregate_report_by_ad_account_id(
        ad_account_id=case["ad_account_id"],
        entity_type=entity_type,
        fields=fields,
        report_start=iso_utc_start_of_day(start_date),
        report_end=iso_utc_start_of_day(end_date),
        granularity="DAY",
        include_parent_entity=False,
        limit=50,
    )

    kpi = aggregate_kpis(report.rows)

    case["kpi"] = {
        "impressions": kpi.impressions,
        "streamed_impressions": kpi.streamed_impressions,
        "clicks": kpi.clicks,
        "ctr": kpi.ctr,
        "spend": kpi.spend,
        "e_cpcl": kpi.e_cpcl,
        "range": f"{start_date} → {end_date}",
    }

    return report, kpi, start_date, end_date, entity_type

def generate_and_upload_finance_snapshot(client: WebClient, case: Dict[str, Any]):
    report, kpi, start_date, end_date, entity_type = compute_kpi_and_report(case, days_back=30)

    pdf_bytes = build_pdf_report(
        ad_account_id=case["ad_account_id"],
        entity_type=entity_type,
        report_start=report.report_start,
        report_end=report.report_end,
        kpi=kpi,
        top_by_spend=top_entities(report.rows, "SPEND", n=5),
        top_by_imps=top_entities(report.rows, "IMPRESSIONS", n=5),
        series_imps=daily_series(report.rows, "IMPRESSIONS"),
        series_spend=daily_series(report.rows, "SPEND"),
        case_id=case["case_id"],
        account_name=case.get("account_name", ""),
        title_override="Spotify Advertising — Finance Snapshot",
    )

    filename = f"finance_snapshot_{case['case_id']}_{start_date}_{end_date}.pdf"

    client.files_upload_v2(
        channel=case["channel_id"],
        thread_ts=case["thread_ts"],
        filename=filename,
        title=f"Finance Snapshot — Case {case['case_id']}",
        file=pdf_bytes,
        initial_comment=(
            f":bar_chart: *Finance snapshot* for <@{case['approver_user_id']}>.\n"
            f"Range: {start_date} → {end_date}\n"
            f"Spend: *{fmt_money(kpi.spend)}* • Impressions: *{fmt_int(kpi.impressions)}* • "
            f"CTR: *{fmt_pct(kpi.ctr)}* • E-CPCL: *{fmt_money(kpi.e_cpcl)}*"
        ),
    )
