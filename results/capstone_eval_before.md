# Capstone Evaluation Log — before

- Produced by: `run_capstone_eval.py::main`
- Service: `app.py::submit` · Audit: `audit.py::log_decision` & `audit.py::log_rejection`

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm inference latency SLA (< 35.0 ms) | >= 9 of 10 | 6/10 | 8/10 | 9/10 | MISSED |
| 2. Token and cost accounting invariant | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 3. Structured audit log completeness | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 4. Bad-path rejection telemetry & short-circuit | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Non-object JSON & oversized payload resilience | 5 of 5 | 3/5 | 1/5 | 0/5 | MISSED |

## Real Output (Trial 1)

### Criterion 1 — Warm Inference Latency SLA
```json
[
  {
    "creator_id": "before_t1_a9c5d8_c1_01",
    "status": 200,
    "total_latency_ms": 47.65,
    "model_latency_ms": 47.51,
    "token_count": 36,
    "passed": false
  },
  {
    "creator_id": "before_t1_a9c5d8_c1_02",
    "status": 200,
    "total_latency_ms": 35.55,
    "model_latency_ms": 35.46,
    "token_count": 38,
    "passed": false
  },
  {
    "creator_id": "before_t1_a9c5d8_c1_03",
    "status": 200,
    "total_latency_ms": 28.57,
    "model_latency_ms": 28.49,
    "token_count": 28,
    "passed": true
  }
]
```

### Criterion 2 — Token & Cost Accounting Invariant
```json
[
  {
    "creator_id": "before_t1_a9c5d8_c2_01",
    "token_count": 16,
    "estimated_cost_usd": 2e-06,
    "expected_cost_usd": 2e-06,
    "model_latency_ms": 19.82,
    "style_latency_ms": 0.02,
    "total_latency_ms": 19.85,
    "log_matched": true,
    "passed": true
  },
  {
    "creator_id": "before_t1_a9c5d8_c2_02",
    "token_count": 36,
    "estimated_cost_usd": 5e-06,
    "expected_cost_usd": 5e-06,
    "model_latency_ms": 33.55,
    "style_latency_ms": 0.08,
    "total_latency_ms": 33.64,
    "log_matched": true,
    "passed": true
  },
  {
    "creator_id": "before_t1_a9c5d8_c2_03",
    "token_count": 38,
    "estimated_cost_usd": 6e-06,
    "expected_cost_usd": 6e-06,
    "model_latency_ms": 37.12,
    "style_latency_ms": 0.08,
    "total_latency_ms": 37.21,
    "log_matched": true,
    "passed": true
  }
]
```

### Criterion 3 — Structured Audit Log Completeness
```json
[
  {
    "timestamp": "2026-11-16T02:02:42+00:00",
    "content_id": "c_155fb09453d8",
    "creator_id": "before_t1_a9c5d8_c3_ok_01",
    "guess": "unsure",
    "label": "We can't tell for sure who wrote this \u2014 it shares characteristics of both human and automated writing.",
    "model_score": 0.7658,
    "style_score": 0.5666,
    "combined_score": 0.6961,
    "status": "decided",
    "model_latency_ms": 34.62,
    "style_latency_ms": 0.08,
    "total_latency_ms": 34.7,
    "token_count": 38,
    "tokens_per_sec": 1095.1,
    "estimated_cost_usd": 6e-06
  },
  {
    "timestamp": "2026-11-16T02:02:42+00:00",
    "content_id": "c_b3f509a33de6",
    "creator_id": "before_t1_a9c5d8_c3_ok_02",
    "guess": "unsure",
    "label": "We can't tell for sure who wrote this \u2014 it shares characteristics of both human and automated writing.",
    "model_score": 0.5148,
    "style_score": 0.4599,
    "combined_score": 0.4956,
    "status": "decided",
    "model_latency_ms": 26.35,
    "style_latency_ms": 0.08,
    "total_latency_ms": 26.43,
    "token_count": 28,
    "tokens_per_sec": 1059.4,
    "estimated_cost_usd": 4e-06
  },
  {
    "timestamp": "2026-11-16T02:02:42+00:00",
    "content_id": "c_26d44abb8b38",
    "creator_id": "before_t1_a9c5d8_c3_ok_03",
    "guess": "human",
    "label": "We think this was written by a person.",
    "model_score": 0.1039,
    "style_score": 0.4007,
    "combined_score": 0.2078,
    "status": "decided",
    "model_latency_ms": 30.35,
    "style_latency_ms": 0.07,
    "total_latency_ms": 30.43,
    "token_count": 37,
    "tokens_per_sec": 1215.91,
    "estimated_cost_usd": 6e-06
  },
  {
    "timestamp": "2026-11-16T02:02:42+00:00",
    "creator_id": "before_t1_a9c5d8_c3_bad_01",
    "event": "rejected",
    "status": "rejected",
    "reason": "missing_or_empty_text",
    "total_latency_ms": 0.0,
    "token_count": 0,
    "estimated_cost_usd": 0.0
  },
  {
    "timestamp": "2026-11-16T02:02:42+00:00",
    "creator_id": "before_t1_a9c5d8_c3_bad_02",
    "event": "rejected",
    "status": "rejected",
    "reason": "missing_or_empty_text",
    "total_latency_ms": 0.0,
    "token_count": 0,
    "estimated_cost_usd": 0.0
  }
]
```

### Criterion 4 — Bad-Path Rejection Telemetry & Short-Circuit
```json
[
  {
    "creator_id": "before_t1_a9c5d8_c4_empty",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T02:02:42+00:00",
      "creator_id": "before_t1_a9c5d8_c4_empty",
      "event": "rejected",
      "status": "rejected",
      "reason": "missing_or_empty_text",
      "total_latency_ms": 0.0,
      "token_count": 0,
      "estimated_cost_usd": 0.0
    },
    "passed": true
  },
  {
    "creator_id": "before_t1_a9c5d8_c4_ws",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T02:02:42+00:00",
      "creator_id": "before_t1_a9c5d8_c4_ws",
      "event": "rejected",
      "status": "rejected",
      "reason": "missing_or_empty_text",
      "total_latency_ms": 0.0,
      "token_count": 0,
      "estimated_cost_usd": 0.0
    },
    "passed": true
  },
  {
    "creator_id": "before_t1_a9c5d8_c4_short",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T02:02:42+00:00",
      "creator_id": "before_t1_a9c5d8_c4_short",
      "event": "rejected",
      "status": "rejected",
      "reason": "Text is too short to score \u2014 a few sentences at least.",
      "total_latency_ms": 0.06,
      "token_count": 1,
      "estimated_cost_usd": 0.0
    },
    "passed": true
  },
  {
    "creator_id": "before_t1_a9c5d8_c4_missing",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T02:02:42+00:00",
      "creator_id": "before_t1_a9c5d8_c4_missing",
      "event": "rejected",
      "status": "rejected",
      "reason": "missing_or_empty_text",
      "total_latency_ms": 0.0,
      "token_count": 0,
      "estimated_cost_usd": 0.0
    },
    "passed": true
  },
  {
    "creator_id": "before_t1_a9c5d8_c4_int",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T02:02:42+00:00",
      "creator_id": "before_t1_a9c5d8_c4_int",
      "event": "rejected",
      "status": "rejected",
      "reason": "missing_or_empty_text",
      "total_latency_ms": 0.0,
      "token_count": 0,
      "estimated_cost_usd": 0.0
    },
    "passed": true
  }
]
```

### Criterion 5 — Non-Object JSON & Oversized Payload Resilience
```json
[
  {
    "case": "json_array",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty 'text'."
    },
    "passed": true
  },
  {
    "case": "malformed_json",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty 'text'."
    },
    "passed": true
  },
  {
    "case": "empty_body",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Send JSON with a non-empty 'text'."
    },
    "passed": true
  },
  {
    "case": "json_integer",
    "status": 500,
    "response_preview": "<!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;int&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger",
    "passed": false
  },
  {
    "case": "oversized_60k",
    "status": 200,
    "response_preview": {
      "confidence": 0.9984,
      "content_id": "c_29388e881f7b",
      "creator_id": "before_t1_a9c5d8_c5_huge",
      "guess": "ai",
      "label": "This text closely follows statistical patterns typical of automated writing.",
      "model_score": 0.9975,
      "style_score": 1.0,
      "telemetry": {
        "estimated_cost_usd": 0.000154,
        "model_latency_ms": 192.57,
        "style_latency_ms": 3.2,
        "token_count": 1024,
        "tokens_per_sec": 5230.36,
        "total_latency_ms": 195.78
      }
    },
    "passed": false
  }
]
```