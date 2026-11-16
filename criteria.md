# Acceptance criteria — Provenance Guard

# Capstone Acceptance Criteria — Provenance Guard (Shape A, Path B)

## 1. Warm Inference Latency SLA (Extension)

Across 10 consecutive warm `POST /submit` requests (30–60 tokens each, measured after 1 cold-start warm-up request), at least **9 of 10** requests must complete with `telemetry.total_latency_ms < 35.0` ms.

**Why this target:**
In baseline benchmarking on local CPU (`distilgpt2`), warm requests averaged `29.01 ms` (range `26.13–32.90 ms`), with 99.7% of wall-clock time spent inside Signal 1's PyTorch forward pass. A `< 35.0 ms` ceiling across 9 of 10 runs catches accidental model reloads (`detector._load()`), tokenizer re-initialization, or synchronous disk I/O bottlenecks while allowing 1 outlier for OS scheduling jitter. A stricter `< 25.0 ms` target would fail against the local CPU compute floor, while a looser `< 500 ms` target would fail to detect model-reloading regressions.

---

## 2. Token and Cost Accounting Invariant (Extension)

Across 10 valid `POST /submit` requests spanning varying input lengths (25 to 250 tokens), **10 of 10** JSON responses and their matching `logs/audit.jsonl` entries must satisfy both:
1. `estimated_cost_usd == round((token_count / 1000.0) * config.COST_PER_1K_TOKENS_USD, 6)`
2. `model_latency_ms + style_latency_ms <= total_latency_ms`

**Why this target:**
Token accounting and stage-latency decomposition are deterministic invariants. Even a single mismatch (9 of 10) indicates floating-point rounding drift, mismatched tokenizer truncation windows (`max_length=1024`), or inverted `time.perf_counter()` boundaries. Anything below 10 of 10 corrupts downstream unit-economics reporting.

---

## 3. Structured Audit Log Completeness and Schema Parity (Extension)

Across a mixed batch of 15 requests (10 valid submissions and 5 rejected bad inputs), **15 of 15** requests must append a valid, parseable JSON line to `logs/audit.jsonl` containing all 5 core telemetry fields (`timestamp`, `status`, `total_latency_ms`, `token_count`, `estimated_cost_usd`) with zero dropped writes or `JSONDecodeError` failures.

**Why this target:**
In an LLMOps observability layer, silent log drops create unrecorded compute spend and blind spots during production incidents. Requiring 15 of 15 verifies that `audit._lock` safely serializes writes across both `audit.log_decision` and `audit.log_rejection`. Accepting 14 of 15 would mask silent exception paths that return an HTTP response without persisting an audit record.

---

## 4. Bad-Path Rejection Telemetry and Zero-Cost Short-Circuit (Extension + Failure Path)

Across 5 invalid `POST /submit` payloads (empty string `""`, whitespace-only `"   \n\t  "`, 1-token text `"hi"`, missing `text` field, and numeric `text: 123`), **5 of 5** requests must return HTTP `400`, write a `status: "rejected"` entry to `logs/audit.jsonl` with a non-empty `reason` and `estimated_cost_usd == 0.0`, and short-circuit in `total_latency_ms < 5.0` ms.

**Why this target:**
Input validation must block malformed payloads before invoking `distilgpt2` inference (~29 ms CPU compute). Verifying `estimated_cost_usd == 0.0` and `total_latency_ms < 5.0` ms proves expensive model execution never runs on bad inputs, while 5 of 5 guarantees every validation guard logs its rejection reason. A looser latency target (e.g., `< 50 ms`) would allow bad inputs to leak into model inference unnoticed.

---

## 5. Non-Object JSON and Oversized Payload Resilience (Failure Path)

Across 5 pathological HTTP requests to `POST /submit` (a JSON array `[]`, malformed JSON syntax `{bad`, an empty request body, a JSON integer `42`, and a 60,000-character string), **5 of 5** requests must return HTTP `400` with a structured JSON error payload and **0** unhandled HTTP `500` exceptions.

**Why this target:**
An unhandled `500` error returns an HTML debugger/error page instead of JSON, breaking API clients and bypassing `audit.log_rejection` completely. Requiring 5 of 5 `400` responses stress-tests the outer request boundary of `app.py::submit` against non-dictionary JSON types (`list`, `int`) and extreme payload lengths before `payload.get()` or model inference executes.




<!-- ─────────────────────────────────────────────────────────────────────────
UNIT 7

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False Positives on Plain Human Writing

Across 3 separate runs of 10 plainly-written human samples, at most 1 sample per run scores $\ge 0.70$ ("Likely AI").


**Why this target:**
Falsely accusing a real writer destroys trust. Plain writing must default to the uncertain band rather than receiving an unearned high-confidence AI label.

---

## 2. Score Separation Between Distinct Archetypes

Across 5 clearly human texts and 5 raw AI texts, the mean composite score of the AI samples must exceed the human mean by at least 0.35.

**Why this target:**
If the two extremes score closely together, the system has no discriminatory power and the threshold boundaries become arbitrary.

---

## 3. Label Reachability Across the Calibration Set

Given 12 calibration inputs (4 clear human, 4 borderline, 4 clear AI), each of the three reader labels must be assigned to at least 2 samples.

**Why this target:**
Prevents the thresholds from collapsing into a binary decision or making the "Unsure" middle band so wide that no definitive labels ever get applied.

---

## 4. Appeal Mutation and Persistence

Every valid call to POST /api/v1/pushback must return HTTP 200/201 with a ticket_id, update the status to "review_pending", and log the event in 100% of cases.

**Why this target:**
Because detection is fallible by design, pushback is a core contract. A dropped or unrecorded appeal leaves the accused writer without recourse.

---

## 5. Pathological Input Rejection

Inputs that are empty, whitespace-only, shorter than 3 tokens, or longer than 50,000 characters must return HTTP 400 in 100% of cases without unhandled 500 exceptions.

**Why this target:**
Both underlying scoring modules crash on empty or undersized inputs; input validation must protect the service before expensive model inference runs.

---
     ───────────────────────────────────────────────────────────────────────── -->
     
<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
