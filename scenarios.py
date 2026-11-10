"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

    # A bad-input criterion looks like this. Uncomment and adjust if that's one
    # of your five — these are raw request bodies, sent exactly as written.
    #
    # {
    #     "name": "bad input",
    #     "criterion": 3,
    #     "bodies": [
    #         {"text": "", "creator_id": "eval_bad_empty"},
    #         {"creator_id": "eval_bad_missing"},          # no text field at all
    #         {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
    #         {"text": None, "creator_id": "eval_bad_null"},
    #     ],
    # },

    # TODO: add what your remaining criteria need.
    #
    # A criterion about the appeal path can't be tested by sending text alone;
    # it needs a submission first and then an appeal against the content_id
    # that came back. You'll need to test that one by hand, or extend this file
    # and run_eval.py to do it. Saying which you did is part of the write-up.

SCENARIOS = [
    # ── Criterion 1: False Positives on Plain Human Writing ───────────────────
    # 10 plain human writing samples (simple, conversational, or second-language).
    # Target: at most 1 in 10 scores >= 0.70.
    {
        "name": "plain human writing",
        "criterion": 1,
        "texts": [
            "I walked to the grocery store early this morning to pick up some bread and eggs. The streets were quiet and cold, and the cashier was just getting the register started for the day.",
            "My sister called yesterday to tell me about her new apartment downtown. She was excited because it is close to the train station and has large windows with plenty of light.",
            "Cooking dinner at home takes more planning than ordering takeout, but it usually tastes fresher. Tonight I made vegetable soup with carrots, celery, potatoes, and vegetable broth.",
            "We spent the afternoon fixing the wooden fence in the backyard. Two of the posts were rotting at the base, so we had to dig them out and pour fresh cement.",
            "Learning a second language as an adult requires patience and daily repetition. Even practicing for fifteen minutes every evening makes reading simpler texts much easier over time.",
            "The library down the street is one of my favorite places to study on weekends. It stays warm, nobody talks loudly, and the desks near the corner have reliable power outlets.",
            "Our train was delayed by forty minutes due to track maintenance near the bridge. Most passengers waited quietly on the platform while drinking coffee from the station kiosk.",
            "I decided to clean out my desk drawers after realizing I could never find a working pen. I threw away old receipts, organized my cables, and wiped down the surface.",
            "Taking care of house plants seemed difficult at first, but remembering to check the soil moisture once a week solved most problems. Now they survive without any trouble.",
            "After finishing my homework, I went for a quick run around the park before sunset. The air was crisp, and there were several people out walking their dogs along the path.",
        ],
    },

    # ── Criterion 2: Score Separation Between Distinct Archetypes ───────────
    # 5 creative human texts vs. 5 raw AI essays.
    # Target: AI mean composite score - Human mean composite score >= 0.35.
    {
        "name": "score separation - human creative",
        "criterion": 2,
        "texts": [
            "I didn't sleep. Not properly, anyway — I lay there listening to the boiler tick and thinking about the thing I'd said to Marcus at the pub, which was stupid, and which he will absolutely bring up again. Twice now. So: coffee, and the long way round to work, and a plan. Priya asked how the weekend was and I said \"fine\" in the voice that means it wasn't; she put her mug down and looked at me. That's Priya. She notices.",
            "The kitchen smelled like burnt garlic and stubborn optimism. Maya was perched on the counter, swinging her heels against the cabinets in a syncopated, irritating rhythm while I tried to salvage the sauce with half a lemon and three pinches of brown sugar. Neither of us admitted the dinner was ruined; admitting it meant ordering pizza, and ordering pizza meant Marcus was right.",
            "Frost had spider-webbed across the inside of the pantry window overnight, thick enough to scratch initials into. My grandfather used to say cold like that kept a house honest. What he meant was the chimney drafted backwards when the north wind hit the ridge, and by seven in the morning you either had the stove roaring or you were drinking tea with your coat zipped to your chin.",
            "We bought the canoe for forty dollars from an old carpenter whose shoulder had given out two summers prior. It had cedar ribs, peeling green canvas along the gunwales, and a patch near the keel that looked like melted tar. It was clumsy, heavy as wet cordwood, and the best purchase we ever made.",
            "There is a peculiar stillness that settles over a printing press right before the rollers drop. The hum of the drive belt slips into an even drone, ink sits glossy and viscous in the reservoir, and the shop air goes heavy with kerosene and damp newsprint.",
        ],
    },
    {
        "name": "score separation - raw AI",
        "criterion": 2,
        "texts": [
            "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables. In conclusion, ongoing evaluation ensures optimal results across diverse operational environments.",
            "Effective communication is an indispensable component of successful team collaboration. By establishing transparent channels and maintaining open dialogue, organizations can foster a positive work culture. Furthermore, proactive communication reduces misunderstandings and enhances productivity, ensuring all team members work synchronously toward common milestones.",
            "Sustainable urban development is crucial for mitigating environmental degradation in contemporary society. Modern planners prioritize energy-efficient public infrastructure, comprehensive waste management systems, and the preservation of urban green spaces. Consequently, communities achieve both ecological resilience and enhanced economic viability.",
            "Technological advancements in automated learning systems have reshaped modern industry workflows. Implementing intelligent pipelines allows enterprises to streamline data processing, optimize resource allocation, and minimize manual intervention. As these frameworks mature, continuous monitoring remains essential for maintaining institutional efficacy.",
            "The significance of regular physical activity cannot be overstated in modern health discourse. Engaging in consistent cardiovascular exercise enhances cardiovascular longevity and mitigates psychological stress. Therefore, adopting a balanced physical regimen represents a fundamental pillar of preventative well-being.",
        ],
    },

    # ── Criterion 3: Label Reachability Across Calibration Set ───────────────
    # 12 samples: 4 clear human, 4 borderline/edited, 4 clear AI.
    # Target: Each of the 3 labels assigned to >= 2 samples.
    {
        "name": "label reachability",
        "criterion": 3,
        "texts": [
            # 4 Human
            "Rain came down sideways off the bay, rattling against the storm doors like gravel. We pulled the dory onto the gravel bar, threw a tarp over the lobster crates, and sprinted for the boathouse before the tide could catch our boots.",
            "My father never kept an appointment in his life without arriving forty minutes early and sitting in the car with the radio off, tapping the steering wheel to some invisible beat.",
            "There was an old copper coin wedged between the floorboards behind the upright piano, so corroded you couldn't tell if the profile belonged to a king or an eagle.",
            "The typewriter keys always stuck on lowercase 'g' and uppercase 'W', leaving odd little ink smudges and pale gaps all through my draft chapters.",
            # 4 Borderline / Lightly-Edited
            "Time management matters more than people admit, especially now that work moves as fast as it does. If you're organised you hit deadlines, and you're less frazzled doing it. A few things actually help: prioritize the essentials, eliminate notifications, and take short pauses.",
            "Public transportation plays a significant role in reducing traffic, although many commuters find the current bus schedules unreliable during morning rush hours. Adding more express routes could solve several complaints.",
            "Learning digital photography is straightforward once you grasp the relationship between shutter speed and aperture. While modern smartphone cameras automate these settings, adjusting them manually offers far more creative control over depth.",
            "Remote work offers undeniable flexibility for employees, yet it introduces distinct communication hurdles during group brainstorming sessions. Balancing video calls with focused solitary work hours is essential for team morale.",
            # 4 AI
            "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs.",
            "Effective communication is an indispensable component of successful team collaboration. By establishing transparent channels and maintaining open dialogue, organizations can foster a positive work culture.",
            "Sustainable urban development is crucial for mitigating environmental degradation in contemporary society. Modern planners prioritize energy-efficient public infrastructure and waste management systems.",
            "Technological advancements in automated learning systems have reshaped modern industry workflows. Implementing intelligent pipelines allows enterprises to streamline data processing and optimize resource allocation.",
        ],
    },

    # ── Criterion 4: Appeal Mutation and Audit Logging ────────────────────────
    # A submission to create content_id records, ready to be appealed.
    # (See note below on how Criterion 4 is verified).
    {
        "name": "appeal candidate submissions",
        "criterion": 4,
        "texts": [
            "This is submission one for appeal testing: a straightforward essay on workplace productivity and routine task prioritization.",
            "This is submission two for appeal testing: an essay describing early morning walks along the riverbank in autumn.",
            "This is submission three for appeal testing: reflections on learning Python and debugging automated web servers.",
            "This is submission four for appeal testing: an overview of community gardening initiatives in dense urban neighborhoods.",
            "This is submission five for appeal testing: notes on the acoustic properties of wood construction in small performance halls.",
        ],
    },

    # ── Criterion 5: Pathological Input Rejection ─────────────────────────────
    # Request bodies sent as raw payloads.
    # Target: 100% return HTTP 400 without unhandled 500 exceptions.
    {
        "name": "pathological inputs",
        "criterion": 5,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "   \n\t   ", "creator_id": "eval_bad_whitespace"},
            {"text": "hi", "creator_id": "eval_bad_short"},
            {"text": "word " * 15000, "creator_id": "eval_bad_huge"},
            {"creator_id": "eval_bad_missing_text"},
            {"text": None, "creator_id": "eval_bad_null"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
