"""Render the six required dashboard panels from structured application logs.

The generated HTML is self-contained, so it can be opened locally or committed as
runtime evidence without relying on a third-party dashboard service.
"""

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "submission" / "evidence" / "11-dashboard-overview.html"


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round(percent / 100 * len(ordered) + 0.5) - 1))
    return ordered[index]


def read_records(log_path: Path) -> list[dict]:
    records: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def status(value: float, operator: str, threshold: float) -> str:
    is_healthy = value <= threshold if operator == "lte" else value >= threshold
    return "healthy" if is_healthy else "breach"


def panel(title: str, values: list[tuple[str, str]], state: str, subtitle: str) -> str:
    rows = "".join(
        f"<div class='metric'><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>"
        for label, value in values
    )
    return f"""
    <section class='panel {state}'>
      <div class='panel-title'><h2>{html.escape(title)}</h2><span class='badge'>{state}</span></div>
      <p>{html.escape(subtitle)}</p>{rows}
    </section>"""


def render(records: list[dict], *, window_minutes: int = 60) -> str:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=window_minutes)
    window_records: list[dict] = []
    for record in records:
        timestamp = record.get("ts")
        if not timestamp:
            continue
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            continue
        if parsed_timestamp.tzinfo is None:
            parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
        if cutoff <= parsed_timestamp <= now:
            window_records.append(record)
    records = window_records

    requests = [record for record in records if record.get("event") == "request_received"]
    responses = [record for record in records if record.get("event") == "response_sent"]
    failures = [record for record in records if record.get("event") == "request_failed"]
    latencies = [float(record["latency_ms"]) for record in responses if record.get("latency_ms") is not None]
    ttfts = [float(record["ttft_ms"]) for record in responses if record.get("ttft_ms") is not None]
    costs = [float(record["cost_usd"]) for record in responses if record.get("cost_usd") is not None]
    tokens_in = sum(int(record.get("tokens_in") or 0) for record in responses)
    tokens_out = sum(int(record.get("tokens_out") or 0) for record in responses)
    quality = [float(record["quality_score"]) for record in responses if record.get("quality_score") is not None]
    retrieval = [record["tool_success"] for record in responses + failures if record.get("tool_success") is not None]
    error_rate = 100 * len(failures) / len(requests) if requests else 0.0
    retrieval_success = 100 * sum(retrieval) / len(retrieval) if retrieval else 0.0
    timestamps = [record.get("ts") for record in requests if record.get("ts")]
    rate_per_minute = len(requests)
    if len(timestamps) >= 2:
        parsed = [datetime.fromisoformat(timestamp.replace("Z", "+00:00")) for timestamp in timestamps]
        elapsed_minutes = max((max(parsed) - min(parsed)).total_seconds() / 60, 1)
        rate_per_minute = len(requests) / elapsed_minutes
    error_types = Counter(str(record.get("error_type") or "unknown") for record in failures)
    latest_ids = [str(record.get("correlation_id", "")) for record in requests[-5:]]

    panels = "\n".join(
        [
            panel(
                "Latency percentiles and TTFT",
                [("P50", f"{percentile(latencies, 50):.0f} ms"), ("P95", f"{percentile(latencies, 95):.0f} ms"), ("P99", f"{percentile(latencies, 99):.0f} ms"), ("TTFT P95", f"{percentile(ttfts, 95):.0f} ms")],
                status(percentile(latencies, 95), "lte", 3000),
                "SLO threshold: P95 ≤ 3000 ms",
            ),
            panel("Request traffic", [("Requests", str(len(requests))), ("Rate", f"{rate_per_minute:.1f} req/min")], status(rate_per_minute, "gte", 1), "Threshold: ≥ 1 request/minute"),
            panel("Error rate and retrieval success", [("Error rate", f"{error_rate:.1f}%"), ("Retrieval success", f"{retrieval_success:.1f}%"), ("Failure breakdown", ", ".join(f"{key}: {value}" for key, value in error_types.items()) or "none")], status(error_rate, "lte", 2), "Threshold: error rate ≤ 2%; retrieval success target ≥ 90%"),
            panel("Cost over time", [("Total", f"${sum(costs):.4f}"), ("Average/request", f"${mean(costs) if costs else 0:.4f}")], status(sum(costs), "lte", 2.5), "Window threshold: total cost ≤ $2.50"),
            panel("Input and output tokens", [("Input", f"{tokens_in:,}"), ("Output", f"{tokens_out:,}"), ("Total", f"{tokens_in + tokens_out:,}")], status(tokens_in + tokens_out, "lte", 50000), "Window threshold: total tokens ≤ 50,000"),
            panel("Quality proxy", [("Mean quality", f"{mean(quality) if quality else 0:.2f}"), ("Responses", str(len(quality)))], status(mean(quality) if quality else 0, "gte", 0.75), "Threshold: mean quality score ≥ 0.75"),
        ]
    )
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    correlation_ids = ", ".join(html.escape(value) for value in latest_ids) or "No request data"
    return f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><title>Day 13 Monitoring Dashboard</title>
<style>
body{{font-family:Arial,sans-serif;background:#0b1020;color:#e5e7eb;margin:0;padding:32px}} h1{{margin:0}} .meta{{color:#9ca3af}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:24px}} .panel{{background:#18213d;border:1px solid #334155;border-radius:12px;padding:18px}} .panel.healthy{{border-top:4px solid #22c55e}} .panel.breach{{border-top:4px solid #ef4444}} .panel-title{{display:flex;justify-content:space-between;align-items:center}} h2{{font-size:18px;margin:0}} p{{color:#a5b4fc;font-size:14px}} .metric{{display:flex;justify-content:space-between;border-top:1px solid #334155;padding:9px 0}} .metric strong{{color:#f8fafc}} .badge{{font-size:12px;text-transform:uppercase;padding:4px 8px;border-radius:12px;background:#334155}} footer{{margin-top:24px;color:#9ca3af;font-size:13px}}
</style></head><body>
<h1>Day 13 Monitoring &amp; LLMOps</h1><p class='meta'>Source: data/logs.jsonl · time range: last {window_minutes} minutes · generated {html.escape(generated_at)}</p>
<div class='grid'>{panels}</div>
<footer>Recent correlation IDs: {correlation_ids}</footer>
</body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the six-panel dashboard from structured logs")
    parser.add_argument("--logs", type=Path, default=DEFAULT_LOG_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    records = read_records(args.logs)
    if not records:
        raise SystemExit(f"No JSON log records found in {args.logs}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(records), encoding="utf-8")
    print(f"Dashboard written to {args.output}")


if __name__ == "__main__":
    main()
