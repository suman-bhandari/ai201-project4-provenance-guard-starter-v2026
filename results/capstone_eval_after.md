# Capstone Evaluation Log — after

- Produced by: `run_capstone_eval.py::main`
- Service: `app.py::submit` · Audit: `audit.py::log_decision` & `audit.py::log_rejection`

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm inference latency SLA (< 35.0 ms) | >= 9 of 10 | 10/10 | 8/10 | 8/10 | MISSED |
| 2. Token and cost accounting invariant | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 3. Structured audit log completeness | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 4. Bad-path rejection telemetry & short-circuit | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Non-object JSON & oversized payload resilience | 5 of 5 | 5/5 | 2/5 | 1/5 | MISSED |

## Real Output (Trial 1)

### Criterion 1 — Warm Inference Latency SLA
```json
[
  {
    "creator_id": "after_t1_6519cc_c1_01",
    "status": 200,
    "total_latency_ms": 30.3,
    "model_latency_ms": 30.21,
    "token_count": 36,
    "passed": true
  },
  {
    "creator_id": "after_t1_6519cc_c1_02",
    "status": 200,
    "total_latency_ms": 30.95,
    "model_latency_ms": 30.87,
    "token_count": 38,
    "passed": true
  },
  {
    "creator_id": "after_t1_6519cc_c1_03",
    "status": 200,
    "total_latency_ms": 26.38,
    "model_latency_ms": 26.31,
    "token_count": 28,
    "passed": true
  }
]
```

### Criterion 2 — Token & Cost Accounting Invariant
```json
[
  {
    "creator_id": "after_t1_6519cc_c2_01",
    "token_count": 16,
    "estimated_cost_usd": 2e-06,
    "expected_cost_usd": 2e-06,
    "model_latency_ms": 19.07,
    "style_latency_ms": 0.02,
    "total_latency_ms": 19.1,
    "log_matched": true,
    "passed": true
  },
  {
    "creator_id": "after_t1_6519cc_c2_02",
    "token_count": 36,
    "estimated_cost_usd": 5e-06,
    "expected_cost_usd": 5e-06,
    "model_latency_ms": 29.98,
    "style_latency_ms": 0.07,
    "total_latency_ms": 30.05,
    "log_matched": true,
    "passed": true
  },
  {
    "creator_id": "after_t1_6519cc_c2_03",
    "token_count": 38,
    "estimated_cost_usd": 6e-06,
    "expected_cost_usd": 6e-06,
    "model_latency_ms": 31.11,
    "style_latency_ms": 0.07,
    "total_latency_ms": 31.18,
    "log_matched": true,
    "passed": true
  }
]
```

### Criterion 3 — Structured Audit Log Completeness
```json
[
  {
    "timestamp": "2026-11-16T03:05:30+00:00",
    "content_id": "c_5477bc52de06",
    "creator_id": "after_t1_6519cc_c3_ok_01",
    "guess": "unsure",
    "label": "We can't tell for sure who wrote this \u2014 it shares characteristics of both human and automated writing.",
    "model_score": 0.7658,
    "style_score": 0.5666,
    "combined_score": 0.6961,
    "status": "decided",
    "model_latency_ms": 35.27,
    "style_latency_ms": 0.08,
    "total_latency_ms": 35.36,
    "token_count": 38,
    "tokens_per_sec": 1074.66,
    "estimated_cost_usd": 6e-06
  },
  {
    "timestamp": "2026-11-16T03:05:30+00:00",
    "content_id": "c_68b2a017fcc1",
    "creator_id": "after_t1_6519cc_c3_ok_02",
    "guess": "unsure",
    "label": "We can't tell for sure who wrote this \u2014 it shares characteristics of both human and automated writing.",
    "model_score": 0.5148,
    "style_score": 0.4599,
    "combined_score": 0.4956,
    "status": "decided",
    "model_latency_ms": 41.0,
    "style_latency_ms": 0.09,
    "total_latency_ms": 41.1,
    "token_count": 28,
    "tokens_per_sec": 681.27,
    "estimated_cost_usd": 4e-06
  },
  {
    "timestamp": "2026-11-16T03:05:30+00:00",
    "content_id": "c_f4fd436cece1",
    "creator_id": "after_t1_6519cc_c3_ok_03",
    "guess": "human",
    "label": "We think this was written by a person.",
    "model_score": 0.1039,
    "style_score": 0.4007,
    "combined_score": 0.2078,
    "status": "decided",
    "model_latency_ms": 46.5,
    "style_latency_ms": 0.08,
    "total_latency_ms": 46.59,
    "token_count": 37,
    "tokens_per_sec": 794.16,
    "estimated_cost_usd": 6e-06
  },
  {
    "timestamp": "2026-11-16T03:05:30+00:00",
    "creator_id": "after_t1_6519cc_c3_bad_01",
    "event": "rejected",
    "status": "rejected",
    "reason": "missing_or_empty_text",
    "total_latency_ms": 0.0,
    "token_count": 0,
    "estimated_cost_usd": 0.0
  },
  {
    "timestamp": "2026-11-16T03:05:30+00:00",
    "creator_id": "after_t1_6519cc_c3_bad_02",
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
    "creator_id": "after_t1_6519cc_c4_empty",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T03:05:30+00:00",
      "creator_id": "after_t1_6519cc_c4_empty",
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
    "creator_id": "after_t1_6519cc_c4_ws",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T03:05:30+00:00",
      "creator_id": "after_t1_6519cc_c4_ws",
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
    "creator_id": "after_t1_6519cc_c4_short",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T03:05:30+00:00",
      "creator_id": "after_t1_6519cc_c4_short",
      "event": "rejected",
      "status": "rejected",
      "reason": "Text is too short to score \u2014 a few sentences at least.",
      "total_latency_ms": 0.09,
      "token_count": 1,
      "estimated_cost_usd": 0.0
    },
    "passed": true
  },
  {
    "creator_id": "after_t1_6519cc_c4_missing",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T03:05:30+00:00",
      "creator_id": "after_t1_6519cc_c4_missing",
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
    "creator_id": "after_t1_6519cc_c4_int",
    "http_status": 400,
    "log_entry": {
      "timestamp": "2026-11-16T03:05:30+00:00",
      "creator_id": "after_t1_6519cc_c4_int",
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
      "message": "Request body must be a JSON object."
    },
    "passed": true
  },
  {
    "case": "malformed_json",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Request body must be a JSON object."
    },
    "passed": true
  },
  {
    "case": "empty_body",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Request body must be a JSON object."
    },
    "passed": true
  },
  {
    "case": "json_integer",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Request body must be a JSON object."
    },
    "passed": true
  },
  {
    "case": "oversized_60k",
    "status": 400,
    "response_preview": {
      "error": "bad_request",
      "message": "Text exceeds maximum allowed length of 50,000 characters."
    },
    "passed": true
  }
]
```