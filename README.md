# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. Submission Ingestion: The client sends a raw text payload and an optional `creator_id` to `POST /submit`.
2. Signal 1 (Language Model Evaluation): The text is evaluated by `detector.py`, measuring predictability (perplexity) against a local language model and outputting an AI score from 0.0 to 1.0.
3. Signal 2 (Stylometric Evaluation): The text is analyzed structurally by `stylometry.py`, measuring sentence length variance, type-token ratio, and clause punctuation density, outputting an AI score from 0.0 to 1.0.
4. Signal Aggregation: `scoring.py::combine_signals` combines both scores via a weighted average and applies a disagreement dampener if the two signals conflict.
5. Threshold Categorization: `scoring.py::score_to_label` classifies the combined score into one of three ranges: human, unsure, or AI.
6. Reader-Facing Label Assignment: Plain-English text is generated to communicate the finding clearly without accusing authentic writers.
7. Audit Logging & Response: The complete decision and both signal scores are recorded to `logs/audit.jsonl`, and an actionable JSON payload with an appeal pathway is returned to the client.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**
Text predictability, quantified as perplexity using a local causal language model.

**Why that might differ between human and AI writing:**
AI models produce text by repeatedly selecting statistically likely next tokens, resulting in uniformly low perplexity. Human writing tends to wander, featuring idiosyncratic phrasing, abrupt syntactic shifts, and domain-specific terminology that surprises the model.

**What it can't see:**
It cannot distinguish between machine generation and plain, direct human writing. Writers using simple vocabulary or short sentences—such as non-native English speakers or younger students—register as predictable and receive falsely elevated AI scores. Ornate, rare-word-heavy AI text can slip through as human.

### Signal two — the style signal

**What it measures:**
The physical shape and statistical variety of the text as raw text (sentence length variance, vocabulary repetition, and clause punctuation).

**Why that might differ between human and AI writing:**
AI models drift toward uniform sentence lengths and consistent vocabulary frequencies. Human writing is structural "lumpier," placing three-word sentences next to forty-word compound sentences.

**What it can't see:**
It cannot comprehend meaning or context. Purely cosmetic edits that alter layout without changing substance—such as splitting sentences with arbitrary full stops, injecting typos, or inserting block quotes—completely distort its measurements.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**
A weighted combination applying `config.WEIGHT_MODEL_SIGNAL` (0.65) to the language model output and `config.WEIGHT_STYLE_SIGNAL` (0.35) to the stylometry output. If the absolute difference between the two signals exceeds 0.40, the system treats the disagreement as structural uncertainty and averages the result with 0.50, pulling the composite score toward the "unsure" band.

**The numbers:**
- `WEIGHT_MODEL_SIGNAL`: 0.65
- `WEIGHT_STYLE_SIGNAL`: 0.35
- Disagreement threshold: `abs(model_score - style_score) > 0.40` pulls to `0.50`

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**
A writer using concise, plain vocabulary produces predictable phrasing that causes `model_score` to spike to 0.78, but their natural rhythm and irregular sentence structure yields a human-like `style_score` of 0.28. The spread is 0.50 (greater than the 0.40 threshold), which dampens the weighted base score (~0.605) down to ~0.553, keeping the text inside the "unsure" tier and preventing an outright false accusation.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was written by a person. |
| unsure | 0.35 – 0.65 | We can't tell for sure who wrote this — it shares characteristics of both human and automated writing. |
| high-confidence AI | 0.65 – 1.00 | This text closely follows statistical patterns typical of automated writing. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

The "unsure" label must admit system limitations without implying guilt. Accusing a genuine writer of dishonesty causes harm, but treating simple or non-native phrasing as inherently artificial is equally unfair. Framing the label neutrally ("it shares characteristics of both") informs readers while avoiding an accusatory tone toward human writers.

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables.",
    "creator_id": "suman"
  }'
  ```

```json
{
  "confidence": 0.6206,
  "content_id": "c_39583a80584f",
  "creator_id": "suman",
  "guess": "unsure",
  "label": "We can't tell for sure who wrote this — it shares characteristics of both human and automated writing.",
  "model_score": 0.8864,
  "style_score": 0.4714
}

```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "c_39583a80584f",
    "creator_id": "suman",
    "reasoning": "This is my personal reflective essay about my work routine; the plain phrasing is deliberate."
  }'
```

```json
{
  "content_id": "c_39583a80584f",
  "message": "Appeal recorded and queued for review.",
  "ok": true,
  "status": "under_review"
}

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.6206,
      "content_id": "c_39583a80584f",
      "creator_id": "suman",
      "guess": "unsure",
      "label": "We can't tell for sure who wrote this — it shares characteristics of both human and automated writing.",
      "model_score": 0.8864,
      "status": "decided",
      "style_score": 0.4714,
      "timestamp": "2026-11-01T11:29:59+00:00"
    },
    {
      "content_id": "c_39583a80584f",
      "creator_id": "suman",
      "event": "appeal",
      "reasoning": "This is my personal reflective essay about my work routine; the plain phrasing is deliberate.",
      "status": "under_review",
      "timestamp": "2026-11-01T12:51:38+00:00"
    }
  ]
}

```

---

## How I Used AI

**Moment 1**

- *What I asked for:* Fixing crashes during input validation on /submit when texts were empty or under 3 tokens.
- *What came back:* An explanation that detector.py raises a ValueError on short text and a recommendation to order validation before the model call.
- *What I changed:* Placed JSON and character checks ahead of signal execution and wrapped detector.model_signal in a try/except ValueError block.

**Moment 2**

- *What I asked for:* Resolving a TypeError: log_appeal() got an unexpected keyword argument 'status' and AttributeError inside /appeal.
- *What came back:* Correct syntax for string validation (isinstance(reasoning, str) and reasoning.strip()) and the exact argument signature for audit.log_appeal().
- *What I changed:* Updated variable checks in app.py::appeal and passed creator_id, content_id, and reasoning directly without the redundant status parameter.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

     A genuine writer composing or revising poems or essays will rarely submit more than 2 or 3 times in a single minute. In contrast, an attacker attempting to probe the scoring boundaries or reverse-engineer the detector thresholds requires dozens of iterations. A limit of 5/minute provides a smooth human experience while rendering rapid automated sweeps impossible.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Per `creator_id` (or IP address depending on limiter key config).

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->
| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_97695524c8f0` | human | 0.280 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_7c3852db57a3` | unsure | 0.494 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_4bedaa7b2c0c` | unsure | 0.565 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_3e89407a3a92` | unsure | 0.560 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_ee2d2f3c2e94` | human | 0.287 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_aafac0d327fe` | unsure | 0.464 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_3218252448cf` | unsure | 0.498 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `c_b28b8ba22b0e` | unsure | 0.351 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_23a19c744ad8` | unsure | 0.581 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_bba3b5e12656` | ai | 0.876 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_a2807d6356c4` | unsure | 0.553 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_993fb5cfd3f4` | ai | 0.668 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_2aebb4b78095` | ai | 0.709 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_4d0b7ef94550` | ai | 0.710 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_910817f0806f` | ai | 0.710 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_a1624ee15a95` | unsure | 0.609 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_dfa5e5710bc1` | unsure | 0.607 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `c_cc9bb7c1281a` | unsure | 0.380 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_fd47501fb625` | unsure | 0.437 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_faad7abe89bd` | human | 0.237 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_8df67c3cbfb0` | unsure | 0.555 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_24b424ddd11c` | unsure | 0.470 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_badc7fdb716b` | unsure | 0.482 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_c622f7fdea92` | unsure | 0.517 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `c_b83c9e6cadbc` | unsure | 0.367 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `c_481b626a1486` | unsure | 0.429 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `c_7231e98ffdcd` | ai | 0.882 | HELD |
| MF06 | malformed | text is emoji only | 200 | `c_a00045d307b4` | ai | 0.998 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_c5a6cecbe56b` | ai | 0.939 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `c_9393811166ba` | ai | 0.913 | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_6abac077e42b` | unsure | 0.445 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | `c_f1c368c3f781` | unsure | 0.383 | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_69e241f90b1e` | unsure | 0.376 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_0bb6f4744080` | unsure | 0.376 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_b8061f4af5d6` | unsure | 0.376 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_df514bd19e56` | unsure | 0.376 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_3d5e3c148ede` | unsure | 0.376 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |


**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
[
  {
    "timestamp": "2026-11-05T08:11:02+00:00",
    "creator_id": "attacker_FL01",
    "event": "rejection",
    "reason": "rate_limit_exceeded",
    "status": 429
  },
  {
    "timestamp": "2026-11-05T08:11:05+00:00",
    "creator_id": "attacker_MF01",
    "event": "rejection",
    "reason": "missing_or_empty_text",
    "status": 400
  },
  {
    "timestamp": "2026-11-05T08:11:10+00:00",
    "content_id": "c_2aebb4b78095",
    "creator_id": "attacker_FP03",
    "guess": "ai",
    "label": "This text closely follows statistical patterns typical of automated writing.",
    "model_score": 0.8051,
    "style_score": 0.5299,
    "combined_score": 0.7088,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:12+00:00",
    "content_id": "c_4d0b7ef94550",
    "creator_id": "attacker_FP04",
    "guess": "ai",
    "label": "This text closely follows statistical patterns typical of automated writing.",
    "model_score": 0.8329,
    "style_score": 0.4812,
    "combined_score": 0.7098,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:15+00:00",
    "content_id": "c_910817f0806f",
    "creator_id": "attacker_FP05",
    "guess": "ai",
    "label": "This text closely follows statistical patterns typical of automated writing.",
    "model_score": 0.8005,
    "style_score": 0.5422,
    "combined_score": 0.7101,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:18+00:00",
    "content_id": "c_97695524c8f0",
    "creator_id": "attacker_EV01",
    "guess": "human",
    "label": "We think this was written by a person.",
    "model_score": 0.1635,
    "style_score": 0.4951,
    "combined_score": 0.2796,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:21+00:00",
    "content_id": "c_ee2d2f3c2e94",
    "creator_id": "attacker_EV05",
    "guess": "human",
    "label": "We think this was written by a person.",
    "model_score": 0.3212,
    "style_score": 0.2227,
    "combined_score": 0.2867,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:25+00:00",
    "content_id": "c_a1624ee15a95",
    "creator_id": "attacker_FP06",
    "guess": "unsure",
    "label": "We can't tell for sure who wrote this — it shares characteristics of both human and automated writing.",
    "model_score": 0.8814,
    "style_score": 0.4156,
    "combined_score": 0.6092,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:28+00:00",
    "content_id": "c_badc7fdb716b",
    "creator_id": "attacker_PI05",
    "guess": "unsure",
    "label": "We can't tell for sure who wrote this — it shares characteristics of both human and automated writing.",
    "model_score": 0.6401,
    "style_score": 0.1369,
    "combined_score": 0.4820,
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T08:11:32+00:00",
    "content_id": "c_faad7abe89bd",
    "creator_id": "attacker_PI02",
    "guess": "human",
    "label": "We think this was written by a person.",
    "model_score": 0.2044,
    "style_score": 0.2963,
    "combined_score": 0.2366,
    "status": "decided"
  }
]

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:
Attack FP03 (Content ID: c_2aebb4b78095) — A non-native English speaker writing carefully.
The service returned a composite score of 0.7088 and assigned the highest-severity classification: "ai" ("This text closely follows statistical patterns typical of automated writing.").
Because the author wrote in a second language, they deliberately relied on clear, conservative vocabulary and standard sentence structures. Signal one penalized this predictability with a high AI score of 0.8051. Because signal two also registered moderate uniformity (0.5299), the score was not divergent enough to trigger the disagreement dampener. The service issued an unearned accusation of academic dishonesty to an authentic writer who took extra care to write cleanly. Accusing an earnest student or non-native speaker of cheating destroys community trust and directly exemplifies the structural bias of perplexity-based detection.


---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
