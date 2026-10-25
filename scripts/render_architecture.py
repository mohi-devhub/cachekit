"""Render the implemented high-level design as a standalone SVG, without downloads."""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/high-level-design.svg"
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1000" viewBox="0 0 1680 1000">',
    "<title>cachekit: high-level design</title>",
    (
        "<desc>Recorded requests enter a deterministic offline analysis pipeline."
        " Local API and dashboard inspect saved evidence. Explicit bounded Devin "
        "handoff and model collectors operate outside the core. Human review "
        "remains separate.</desc>"
    ),
    (
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" '
        'refY="4" orient="auto"><path d="M1 1 L7 4 L1 7" fill="none" '
        'stroke="#252525"/></marker></defs>'
    ),
    '<rect width="1680" height="1000" fill="#fff"/>',
    (
        '<style>text{font-family:"Segoe Print","Bradley Hand",ui-sans-'
        "serif,system-ui,sans-serif;fill:#161616}.title{font-size:24px;font-"
        "weight:600}.label{font-size:16px;font-weight:600}.small{font-"
        "size:12px;fill:#555}.edge{fill:none;stroke:#252525;stroke-"
        "width:1.35;marker-end:url(#arrow)}.group{fill:none;stroke:#555;stroke-"
        "width:1.25;stroke-dasharray:6 5}.box{fill:#fff;stroke:#333;stroke-"
        "width:1.35}</style>"
    ),
]


def text(x, y, value, kind="label", anchor="middle"):
    parts.append(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{kind}">{escape(value)}</text>'
    )


def group(x, y, w, h, title):
    parts.append(f'<rect class="group" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>')
    text(x + 16, y + 23, title, "label", "start")


def box(x, y, w, h, title, lines=()):
    parts.append(f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>')
    text(x + w / 2, y + 25, title)
    for i, line in enumerate(lines):
        text(x + w / 2, y + 46 + i * 17, line, "small")


def edge(points, label="", at=None, dashed=False):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x} {y}" for i, (x, y) in enumerate(points))
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    parts.append(f'<path class="edge" d="{d}"{dash}/>')
    if label and at:
        width = len(label) * 6.1 + 10
        parts.append(
            f'<rect x="{at[0] - width / 2}" y="{at[1] - 12}" '
            f'width="{width}" height="17" fill="#fff"/>'
        )
        text(*at, label, "small")


text(840, 34, "cachekit: High-Level Design", "title")
group(340, 65, 520, 555, "Offline engine · Python · no LLM or network calls")
box(
    365,
    105,
    470,
    64,
    "Typed contracts and pinned configuration",
    ["Pydantic · model/tokenizer revision · cache profile"],
)
parts.append('<rect x="380" y="199" width="440" height="395" rx="13" fill="none" stroke="#222"/>')
parts.append('<rect x="386" y="205" width="428" height="383" rx="9" fill="none" stroke="#777"/>')
steps = [
    (220, "Ingest and validate", ["Native JSONL / public-dataset adapters"]),
    (291, "Render and tokenize", ["Exact local Qwen chat template and token IDs"]),
    (362, "Diagnose cache breakers", ["Route grouping · stable/variable alignment · rules"]),
    (433, "Simulate prefix reuse", ["Sequential prompt-only block cache · bounded capacity"]),
    (504, "Build report", ["Findings · redacted preview · SIMULATED reuse"]),
]
for y, title, lines in steps:
    box(406, y, 388, 59, title, lines)
for y in (279, 350, 421, 492):
    edge([(600, y), (600, y + 12)])
edge([(600, 169), (600, 220)])
box(
    35,
    125,
    250,
    88,
    "Recorded model requests",
    ["Application-provided JSONL", "messages · tools · settings · route"],
)
box(
    35,
    298,
    250,
    85,
    "Public dataset adapters",
    ["SWE-agent / Glaive", "converted locally; source timing is synthetic"],
)
box(
    35,
    500,
    250,
    90,
    "data/ · private local inputs",
    ["Recorded clock/seeds and BEFORE requests", "Never sent to Devin or committed"],
)
edge([(285, 169), (314, 169), (314, 250), (406, 250)], "validated records", (346, 241))
edge([(285, 340), (325, 340), (325, 265), (406, 265)])
group(965, 65, 675, 282, "Local inspection · FastAPI + Next.js / React / TypeScript")
box(
    990,
    112,
    253,
    83,
    "Local REST API",
    ["Analyze files · read reports and evidence", "Task / verify / approval endpoints"],
)
box(
    1340,
    112,
    275,
    83,
    "Web dashboard",
    ["Findings · cache scanner · measured results", "Fix task and behavioral review"],
)
box(
    1340, 251, 275, 65, "Saved public demo snapshot", ["Read-only fallback; matching evidence only"]
)
edge([(794, 535), (910, 535), (910, 152), (990, 152)], "reports / evidence", (906, 369))
edge([(1243, 153), (1340, 153)], "HTTP / JSON", (1290, 144))
edge([(1478, 251), (1478, 195)], "offline fallback", (1541, 225), True)
group(965, 390, 675, 282, "Explicit source-fix workflow · external fixer stays outside the engine")
box(
    990,
    435,
    253,
    78,
    "Constrained task builder",
    ["Redacted structured findings", "Allowed files · preserved baseline"],
)
box(
    1340,
    435,
    275,
    78,
    "Devin · explicit capped session",
    ["Repository source + redacted task only", "Fresh branch; no private prompt logs"],
)
box(
    990,
    564,
    253,
    81,
    "Local deterministic verifier",
    ["Scope / content / roles / tests / reuse", "Consumes saved golden outputs and reviews"],
)
box(
    1340,
    564,
    275,
    81,
    "GitHub pull request",
    ["Actual changed source and checks", "Saved comparison table; no automatic merge"],
)
edge([(794, 550), (920, 550), (920, 474), (990, 474)], "selected findings", (905, 466))
edge([(1243, 474), (1340, 474)], "approved handoff", (1291, 465), True)
edge([(1478, 513), (1478, 564)], "source change + PR", (1543, 542), True)
edge([(1340, 605), (1243, 605)], "local checkout", (1290, 594))
box(
    1280,
    713,
    335,
    64,
    "Human review and merge",
    ["Acceptance is bound to the exact verified source"],
)
edge([(1117, 645), (1117, 745), (1280, 745)], "passing evidence", (1193, 735))
edge([(1500, 645), (1500, 713)], "review PR", (1543, 688))
parts.append(
    '<path d="M410 670 C410 650 800 650 800 670 L800 735 C800 755 410 755 410 735 Z" class="box"/>'
)
parts.append(
    '<ellipse cx="605" cy="670" rx="195" ry="17" fill="#fff" stroke="#333" stroke-width="1.35"/>'
)
text(605, 709, "eval_results/ · saved artifacts")
text(605, 730, "Reports · hashes · counters · timings · public golden outputs", "small")
edge([(600, 563), (600, 653)], "save deterministic report", (694, 635))
edge([(800, 700), (900, 700), (900, 620), (990, 620)], "recorded evidence", (898, 693))
edge(
    [(285, 546), (310, 546), (310, 774), (955, 774), (955, 635), (990, 635)],
    "local recorded-input replay",
    (495, 784),
)
group(340, 819, 905, 150, "Explicit measurement tools · separate from offline analysis")
box(
    365,
    858,
    235,
    82,
    "Quality collector",
    ["Fixed public BEFORE / AFTER cases", "Actual model answers; bounded assertions"],
)
box(
    630,
    858,
    235,
    92,
    "Matched replay runner",
    [
        "Same inputs / schedule / settings",
        "MEASURED counters and TTFT",
        "GPU-window cost component",
    ],
)
box(
    960,
    858,
    260,
    82,
    "Modal + pinned vLLM / Qwen",
    ["One L4 · explicit inference allocation", "Stop after the measurement block"],
)
edge(
    [(600, 877), (615, 877), (615, 850), (1090, 850), (1090, 858)],
    "explicit quality calls",
    (823, 841),
    True,
)
edge([(865, 906), (960, 906)], "explicit replay", (912, 895), True)
edge([(483, 858), (483, 752)], "save actual observations", (574, 807))
box(
    1280,
    819,
    335,
    150,
    "Legend and boundaries",
    [
        "Double border: deterministic core",
        "Solid arrow: primary data flow",
        "Dashed arrow: explicit / secondary flow",
        "Diagram describes implemented boundaries",
    ],
)
parts.append("</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(OUT.relative_to(ROOT))
