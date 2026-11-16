"""
Capstone Milestone 5 Evaluation Runner (`run_capstone_eval.py`).
Executes all 5 acceptance criteria across 3 trials against the running service
and verifies both HTTP responses and `logs/audit.jsonl` entries.
"""

import argparse
import json
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000/submit"
AUDIT_LOG = Path(__file__).parent / "logs" / "audit.jsonl"
RESULTS_DIR = Path(__file__).parent / "results"
COST_PER_1K_TOKENS_USD = 0.00015

WARM_SAMPLES_30_60_TOK = [
    "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs.",
    "I walked to the grocery store early this morning to pick up some bread and eggs. The streets were quiet and cold, and the cashier was just getting the register started for the day.",
    "Effective communication is an indispensable component of successful team collaboration. By establishing transparent channels and maintaining open dialogue, organizations can foster a positive work culture.",
    "Frost had spider-webbed across the inside of the pantry window overnight, thick enough to scratch initials into. My grandfather used to say cold like that kept a house honest.",
    "Sustainable urban development is crucial for mitigating environmental degradation in contemporary society. Modern planners prioritize energy-efficient public infrastructure and waste management systems.",
    "We bought the canoe for forty dollars from an old carpenter whose shoulder had given out two summers prior. It had cedar ribs, peeling green canvas along the gunwales, and a patch near the keel.",
    "Technological advancements in automated learning systems have reshaped modern industry workflows. Implementing intelligent pipelines allows enterprises to streamline data processing and optimize resource allocation.",
    "The kitchen smelled like burnt garlic and stubborn optimism. Maya was perched on the counter, swinging her heels against the cabinets while I tried to salvage the sauce with half a lemon.",
    "Public transportation plays a significant role in reducing traffic, although many commuters find the current bus schedules unreliable during morning rush hours. Adding express routes could help.",
    "Remote work offers undeniable flexibility for employees, yet it introduces distinct communication hurdles during group brainstorming sessions. Balancing video calls with solitary work is essential.",
]

VARYING_LENGTH_SAMPLES = [
    "Short clear writing still needs enough words to cross the minimum token window for scoring.",
    WARM_SAMPLES_30_60_TOK[0],
    WARM_SAMPLES_30_60_TOK[1],
    " ".join(WARM_SAMPLES_30_60_TOK[0:2]),
    " ".join(WARM_SAMPLES_30_60_TOK[1:3]),
    " ".join(WARM_SAMPLES_30_60_TOK[2:4]),
    " ".join(WARM_SAMPLES_30_60_TOK[3:5]),
    " ".join(WARM_SAMPLES_30_60_TOK[0:4]),
    " ".join(WARM_SAMPLES_30_60_TOK[2:6]),
    " ".join(WARM_SAMPLES_30_60_TOK[4:8]),
]


def send_raw(raw_bytes: bytes, content_type: str = "application/json") -> tuple[int, dict | str]:
    req = urllib.request.Request(
        BASE_URL,
        data=raw_bytes,
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body_text)
            except json.JSONDecodeError:
                return resp.status, body_text
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(body_text)
        except json.JSONDecodeError:
            return exc.code, body_text


def send_json(payload: dict) -> tuple[int, dict | str]:
    return send_raw(json.dumps(payload).encode("utf-8"))


def read_log_lines() -> list[str]:
    if not AUDIT_LOG.exists():
        return []
    return AUDIT_LOG.read_text(encoding="utf-8").splitlines()


def run_trial(trial_num: int, label: str) -> dict:
    run_tag = f"{label}_t{trial_num}_{uuid.uuid4().hex[:6]}"

    # Warm-up call so cold model load is excluded from warm SLA measurement
    send_json({"text": WARM_SAMPLES_30_60_TOK[0], "creator_id": f"{run_tag}_warmup"})

    # ── Criterion 1: Warm Inference Latency SLA (< 35.0 ms, target >= 9/10) ──
    c1_records = []
    c1_passed = 0
    for idx, text in enumerate(WARM_SAMPLES_30_60_TOK, start=1):
        cid = f"{run_tag}_c1_{idx:02d}"
        status, body = send_json({"text": text, "creator_id": cid})
        t = body["telemetry"] if isinstance(body, dict) and "telemetry" in body else {}
        lat = t.get("total_latency_ms", 9999.0)
        ok = status == 200 and lat < 35.0
        if ok:
            c1_passed += 1
        c1_records.append({
            "creator_id": cid,
            "status": status,
            "total_latency_ms": lat,
            "model_latency_ms": t.get("model_latency_ms"),
            "token_count": t.get("token_count"),
            "passed": ok,
        })

    # ── Criterion 2: Token & Cost Accounting Invariant (target 10/10) ─────────
    log_before_c2 = len(read_log_lines())
    c2_records = []
    c2_passed = 0
    for idx, text in enumerate(VARYING_LENGTH_SAMPLES, start=1):
        cid = f"{run_tag}_c2_{idx:02d}"
        status, body = send_json({"text": text, "creator_id": cid})
        t = body["telemetry"] if isinstance(body, dict) and "telemetry" in body else {}
        tok = t.get("token_count", -1)
        cost = t.get("estimated_cost_usd", -1.0)
        expected_cost = round((tok / 1000.0) * COST_PER_1K_TOKENS_USD, 6)
        m_lat = t.get("model_latency_ms", 0.0)
        s_lat = t.get("style_latency_ms", 0.0)
        tot_lat = t.get("total_latency_ms", -1.0)

        # Match corresponding audit.jsonl line
        new_lines = [json.loads(line) for line in read_log_lines()[log_before_c2:] if line.strip()]
        matched = next((e for e in new_lines if e.get("creator_id") == cid), None)

        inv_math = (cost == expected_cost) and (round(m_lat + s_lat, 2) <= round(tot_lat + 0.02, 2))
        inv_log = (
            matched is not None
            and matched.get("estimated_cost_usd") == cost
            and matched.get("token_count") == tok
        )
        ok = status == 200 and inv_math and inv_log
        if ok:
            c2_passed += 1
        c2_records.append({
            "creator_id": cid,
            "token_count": tok,
            "estimated_cost_usd": cost,
            "expected_cost_usd": expected_cost,
            "model_latency_ms": m_lat,
            "style_latency_ms": s_lat,
            "total_latency_ms": tot_lat,
            "log_matched": inv_log,
            "passed": ok,
        })

    # ── Criterion 3: Structured Audit Log Completeness (target 15/15) ─────────
    log_before_c3 = len(read_log_lines())
    c3_inputs = [
        {"text": WARM_SAMPLES_30_60_TOK[i % len(WARM_SAMPLES_30_60_TOK)], "creator_id": f"{run_tag}_c3_ok_{i:02d}"}
        for i in range(1, 11)
    ] + [
        {"text": "", "creator_id": f"{run_tag}_c3_bad_01"},
        {"text": "   ", "creator_id": f"{run_tag}_c3_bad_02"},
        {"text": "hi", "creator_id": f"{run_tag}_c3_bad_03"},
        {"creator_id": f"{run_tag}_c3_bad_04"},
        {"text": 999, "creator_id": f"{run_tag}_c3_bad_05"},
    ]
    for item in c3_inputs:
        send_json(item)

    raw_new_lines = read_log_lines()[log_before_c3:]
    required_keys = {"timestamp", "status", "total_latency_ms", "token_count", "estimated_cost_usd"}
    c3_passed = 0
    c3_sample_entries = []
    for raw_line in raw_new_lines:
        try:
            parsed = json.loads(raw_line)
            if required_keys.issubset(parsed.keys()):
                c3_passed += 1
            if len(c3_sample_entries) < 3 or parsed.get("status") == "rejected":
                c3_sample_entries.append(parsed)
        except json.JSONDecodeError:
            pass

    # ── Criterion 4: Bad-Path Rejection Telemetry & Short-Circuit (target 5/5) ─
    log_before_c4 = len(read_log_lines())
    c4_payloads = [
        {"text": "", "creator_id": f"{run_tag}_c4_empty"},
        {"text": "   \n\t  ", "creator_id": f"{run_tag}_c4_ws"},
        {"text": "hi", "creator_id": f"{run_tag}_c4_short"},
        {"creator_id": f"{run_tag}_c4_missing"},
        {"text": 123, "creator_id": f"{run_tag}_c4_int"},
    ]
    c4_records = []
    c4_passed = 0
    for item in c4_payloads:
        cid = item["creator_id"]
        status, body = send_json(item)
        new_lines = [json.loads(line) for line in read_log_lines()[log_before_c4:] if line.strip()]
        matched = next((e for e in new_lines if e.get("creator_id") == cid), None)
        ok = (
            status == 400
            and matched is not None
            and matched.get("status") == "rejected"
            and bool(matched.get("reason"))
            and matched.get("estimated_cost_usd") == 0.0
            and matched.get("total_latency_ms", 999.0) < 5.0
        )
        if ok:
            c4_passed += 1
        c4_records.append({
            "creator_id": cid,
            "http_status": status,
            "log_entry": matched,
            "passed": ok,
        })

    # ── Criterion 5: Non-Object JSON & Oversized Payload Resilience (target 5/5)
    c5_cases = [
        ("json_array", b"[]"),
        ("malformed_json", b"{bad_json"),
        ("empty_body", b""),
        ("json_integer", b"42"),
        ("oversized_60k", json.dumps({"text": "word " * 12000, "creator_id": f"{run_tag}_c5_huge"}).encode("utf-8")),
    ]
    c5_records = []
    c5_passed = 0
    for case_name, raw_body in c5_cases:
        status, body = send_raw(raw_body)
        is_json_dict = isinstance(body, dict)
        ok = status == 400 and is_json_dict
        if ok:
            c5_passed += 1
        c5_records.append({
            "case": case_name,
            "status": status,
            "response_preview": body if is_json_dict else str(body)[:140],
            "passed": ok,
        })

    return {
        "trial": trial_num,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "c1": {"score": f"{c1_passed}/10", "passed": c1_passed >= 9, "records": c1_records},
        "c2": {"score": f"{c2_passed}/10", "passed": c2_passed == 10, "records": c2_records},
        "c3": {"score": f"{c3_passed}/15", "passed": c3_passed == 15, "sample_entries": c3_sample_entries[:5]},
        "c4": {"score": f"{c4_passed}/5", "passed": c4_passed == 5, "records": c4_records},
        "c5": {"score": f"{c5_passed}/5", "passed": c5_passed == 5, "records": c5_records},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="before", help="Run label (e.g. before or after)")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    trials = []
    for t in (1, 2, 3):
        print(f"Running Trial {t}/3 ({args.label})...")
        trials.append(run_trial(t, args.label))
        time.sleep(0.5)

    out_json = RESULTS_DIR / f"capstone_eval_{args.label}.json"
    out_json.write_text(json.dumps(trials, indent=2, ensure_ascii=False), encoding="utf-8")

    def verdict(key: str) -> str:
        return "MET" if all(tr[key]["passed"] for tr in trials) else "MISSED"

    table_lines = [
        f"# Capstone Evaluation Log — {args.label}",
        "",
        "- Produced by: `run_capstone_eval.py::main`",
        "- Service: `app.py::submit` · Audit: `audit.py::log_decision` & `audit.py::log_rejection`",
        "",
        "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
        "|---|---|---|---|---|---|",
        f"| 1. Warm inference latency SLA (< 35.0 ms) | >= 9 of 10 | {trials[0]['c1']['score']} | {trials[1]['c1']['score']} | {trials[2]['c1']['score']} | {verdict('c1')} |",
        f"| 2. Token and cost accounting invariant | 10 of 10 | {trials[0]['c2']['score']} | {trials[1]['c2']['score']} | {trials[2]['c2']['score']} | {verdict('c2')} |",
        f"| 3. Structured audit log completeness | 15 of 15 | {trials[0]['c3']['score']} | {trials[1]['c3']['score']} | {trials[2]['c3']['score']} | {verdict('c3')} |",
        f"| 4. Bad-path rejection telemetry & short-circuit | 5 of 5 | {trials[0]['c4']['score']} | {trials[1]['c4']['score']} | {trials[2]['c4']['score']} | {verdict('c4')} |",
        f"| 5. Non-object JSON & oversized payload resilience | 5 of 5 | {trials[0]['c5']['score']} | {trials[1]['c5']['score']} | {trials[2]['c5']['score']} | {verdict('c5')} |",
        "",
        "## Real Output (Trial 1)",
        "",
        "### Criterion 1 — Warm Inference Latency SLA",
        "```json",
        json.dumps(trials[0]["c1"]["records"][:3], indent=2),
        "```",
        "",
        "### Criterion 2 — Token & Cost Accounting Invariant",
        "```json",
        json.dumps(trials[0]["c2"]["records"][:3], indent=2),
        "```",
        "",
        "### Criterion 3 — Structured Audit Log Completeness",
        "```json",
        json.dumps(trials[0]["c3"]["sample_entries"], indent=2),
        "```",
        "",
        "### Criterion 4 — Bad-Path Rejection Telemetry & Short-Circuit",
        "```json",
        json.dumps(trials[0]["c4"]["records"], indent=2),
        "```",
        "",
        "### Criterion 5 — Non-Object JSON & Oversized Payload Resilience",
        "```json",
        json.dumps(trials[0]["c5"]["records"], indent=2),
        "```",
    ]

    out_md = RESULTS_DIR / f"capstone_eval_{args.label}.md"
    out_md.write_text("\n".join(table_lines), encoding="utf-8")
    print(f"\nSaved {out_json} and {out_md}\n")
    print("\n".join(table_lines[:15]))


if __name__ == "__main__":
    main()