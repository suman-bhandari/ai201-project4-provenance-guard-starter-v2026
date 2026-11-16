"""
Benchmark 10 warm runs + 2 failure runs for Milestone 3 observability & cost measurement.
Run while `python app.py` or `gunicorn` is active on http://127.0.0.1:5000.
"""
import statistics
import urllib.request
import urllib.error
import json

URL = "http://127.0.0.1:5000/submit"

SAMPLES = [
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

FAILURES = [
    {"text": "   ", "creator_id": "bench_fail_empty"},
    {"text": "hi", "creator_id": "bench_fail_short"},
]

def post(payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

if __name__ == "__main__":
    # Warm-up call so cold model load isn't counted in steady-state average
    post({"text": SAMPLES[0], "creator_id": "warmup_caller"})

    latencies, models, styles, tokens, throughputs, costs = [], [], [], [], [], []
    for i, text in enumerate(SAMPLES, start=1):
        status, body = post({"text": text, "creator_id": f"bench_user_{i:02d}"})
        t = body["telemetry"]
        latencies.append(t["total_latency_ms"])
        models.append(t["model_latency_ms"])
        styles.append(t["style_latency_ms"])
        tokens.append(t["token_count"])
        throughputs.append(t["tokens_per_sec"])
        costs.append(t["estimated_cost_usd"])

    for bad in FAILURES:
        post(bad)

    print("\n=== 10-RUN BENCHMARK SUMMARY ===")
    print(f"Mean Total Latency:  {statistics.mean(latencies):.2f} ms (min: {min(latencies):.2f}, max: {max(latencies):.2f})")
    print(f"Mean Model Latency:  {statistics.mean(models):.2f} ms ({(statistics.mean(models)/statistics.mean(latencies))*100:.1f}% of total)")
    print(f"Mean Style Latency:  {statistics.mean(styles):.2f} ms")
    print(f"Mean Tokens / Run:   {statistics.mean(tokens):.1f} tokens")
    print(f"Mean Throughput:     {statistics.mean(throughputs):.2f} tokens/sec")
    print(f"Mean Cost / Run:     ${statistics.mean(costs):.6f} USD")
    print(f"Cost per 1,000 Runs: ${statistics.mean(costs) * 1000:.4f} USD")