import io
from typing import Any, List, Optional, Tuple
import datetime as dt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from app.reporting.metrics import KPI
from app.reporting.utils import fmt_int, fmt_money, fmt_pct

def build_pdf_report(
    *,
    ad_account_id: str,
    entity_type: str,
    report_start: str,
    report_end: str,
    kpi: KPI,
    top_by_spend: List[Tuple[str, float]],
    top_by_imps: List[Tuple[str, float]],
    series_imps: List[Tuple[dt.date, float]],
    series_spend: List[Tuple[dt.date, float]],
    case_id: Optional[str] = None,
    account_name: str = "",
    title_override: Optional[str] = None,
) -> bytes:
    styles = getSampleStyleSheet()
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.6 * cm,
        bottomMargin=2.0 * cm,
        title="Ad Account Value Overview",
        author="Churn Prevention Bot",
    )

    story: List[Any] = []

    header = title_override or "Spotify Advertising — Account Value Overview"
    meta = f"{report_start[:10]} → {report_end[:10]} • Breakdown: {entity_type}"
    acct = f"Ad Account: {ad_account_id}"
    if account_name:
        acct += f" ({account_name})"
    if case_id:
        acct += f" • Case: {case_id}"

    story.append(Paragraph(header, styles["Title"]))
    story.append(Paragraph(meta, styles["Normal"]))
    story.append(Paragraph(acct, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    bullets = [
        f"Delivered <b>{fmt_int(kpi.impressions)}</b> impressions and <b>{fmt_int(kpi.streamed_impressions)}</b> streamed impressions in the selected period.",
        f"Generated <b>{fmt_int(kpi.clicks)}</b> clicks at <b>{fmt_pct(kpi.ctr)}</b> CTR with total spend of <b>{fmt_money(kpi.spend)}</b>.",
        f"Effective cost-per-click (E-CPCL): <b>{fmt_money(kpi.e_cpcl)}</b> — efficiency benchmark for renewal discussion.",
        "Concentration is high across top entities — optimizing allocation can preserve outcomes while improving efficiency.",
    ]
    story.append(Paragraph("<br/>".join([f"• {b}" for b in bullets]), styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Key Metrics", styles["Heading2"]))
    kpi_data = [
        ["Impressions", "Streamed Impressions", "Clicks", "CTR", "Spend", "E-CPCL"],
        [
            fmt_int(kpi.impressions),
            fmt_int(kpi.streamed_impressions),
            fmt_int(kpi.clicks),
            fmt_pct(kpi.ctr),
            fmt_money(kpi.spend),
            fmt_money(kpi.e_cpcl),
        ],
    ]
    t = Table(kpi_data, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Top Entities (Spend)", styles["Heading2"]))
    spend_table = [["Entity", "Spend"]] + [[name, fmt_money(val)] for name, val in top_by_spend]
    t2 = Table(spend_table, hAlign="LEFT", colWidths=[11 * cm, 4 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Top Entities (Impressions)", styles["Heading2"]))
    imps_table = [["Entity", "Impressions"]] + [[name, fmt_int(val)] for name, val in top_by_imps]
    t3 = Table(imps_table, hAlign="LEFT", colWidths=[11 * cm, 4 * cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Trends", styles["Heading2"]))

    def chart_to_image_bytes(xy, title: str, ylabel: str) -> io.BytesIO:
        xs = [d for d, _ in xy]
        ys = [v for _, v in xy]
        fig = plt.figure(figsize=(7.2, 2.6), dpi=140)
        ax = fig.add_subplot(111)
        ax.plot(xs, ys)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()
        out = io.BytesIO()
        fig.savefig(out, format="png")
        plt.close(fig)
        out.seek(0)
        return out

    img1 = chart_to_image_bytes(series_imps, "Daily Impressions", "Impressions")
    img2 = chart_to_image_bytes(series_spend, "Daily Spend", "Spend (EUR)")

    story.append(Image(img1, width=16 * cm, height=5.7 * cm))
    story.append(Spacer(1, 10))
    story.append(Image(img2, width=16 * cm, height=5.7 * cm))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Appendix: Notes", styles["Heading2"]))
    story.append(Paragraph(
        "This report was generated from aggregated metrics using a mocked Ads API response for demonstration. "
        "In production: pagination, deterministic inputs, data quality checks, and auditable/signed report artifacts.",
        styles["BodyText"],
    ))

    doc.build(story)
    return buf.getvalue()
