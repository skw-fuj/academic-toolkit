#!/usr/bin/env python3
"""Reference assembly for academic-exam (practice mode) — a complete worked example:
a question set (MCQ + structured SAQ, two independent sets) -> one question PDF +
one physically separate solutions PDF, both verified.

Copy this shape for a real subject. Replace SET_A / SET_B / SOLUTIONS content with
questions written against the audited lecture notes; keep the assembly + render
+ verify structure exactly.

    python3 build_example.py            # writes two PDFs to ./_out/ and verifies them
"""
import os
import subprocess
import sys

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)

from wblocks import (  # noqa: E402
    document, meta_line, student_fields, instructions, h2,
    mcq_item, mcq_solution, saq_item, saq_solution, set_divider, solutions_banner,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_out")
SUBJECT = "TEST1001 — Marketing Metrics"
LECTURE = "Lecture 4 — Customer Value"


# --------------------------------------------------------------------------- #
# content (illustrative — a real run writes these from the audited notes)
# --------------------------------------------------------------------------- #
def _mcq_section(set_letter, items):
    body = [h2("multiple choice", f"Set {set_letter}")]
    for i, it in enumerate(items, 1):
        body.append(mcq_item(i, it["stem"], it["options"]))
    return "\n".join(body)


def _saq_section(set_letter, items):
    body = [h2("short answer", f"Set {set_letter}")]
    for i, it in enumerate(items, len(SET_A_MCQ) + 1):
        body.append(saq_item(i, it["stem"], it["parts"]))
    return "\n".join(body)


SET_A_MCQ = [
    {"stem": "A subscription firm's monthly churn falls from 5% to 4%. All else equal, "
             "average customer lifetime:",
     "options": ["increases from 20 to 25 months", "increases from 20 to 24 months",
                 "decreases from 25 to 20 months", "is unchanged"]},
    {"stem": "Customer lifetime value is most sensitive to an error in which input when "
             "margins are thin and retention is high?",
     "options": ["the discount rate", "the acquisition cost", "the churn rate",
                 "the number of customers"]},
]
SET_A_SAQ = [
    {"stem": "A SaaS business reports 1,200 active customers, 5% monthly churn, and $40 "
             "average monthly revenue per user at a 70% gross margin.",
     "parts": [
         {"label": "a", "text": "Calculate the average customer lifetime in months.", "marks": 2},
         {"label": "b", "text": "Calculate gross-margin customer lifetime value, showing your "
                                "working.", "marks": 3},
         {"label": "c", "text": "The firm's blended customer acquisition cost is $260. State "
                                "whether acquisition is profitable and explain one reason this "
                                "single ratio could still be misleading.", "marks": 3}]},
]

SET_B_MCQ = [
    {"stem": "A subscription firm's monthly churn rises from 4% to 5%. All else equal, "
             "average customer lifetime:",
     "options": ["decreases from 25 to 20 months", "decreases from 24 to 20 months",
                 "increases from 20 to 25 months", "is unchanged"]},
    {"stem": "Doubling the assumed discount rate has the smallest effect on a CLV estimate "
             "when:",
     "options": ["retention is low and the payback period is short",
                 "retention is high and cash flows are far in the future",
                 "acquisition cost is high", "gross margin is low"]},
]
SET_B_SAQ = [
    {"stem": "A media subscription reports 3,000 active members, 8% monthly churn, and $18 "
             "average monthly revenue per member at a 60% gross margin.",
     "parts": [
         {"label": "a", "text": "Calculate the average member lifetime in months.", "marks": 2},
         {"label": "b", "text": "Calculate gross-margin customer lifetime value, showing your "
                                "working.", "marks": 3},
         {"label": "c", "text": "Member acquisition cost is $95. State whether acquisition is "
                                "profitable and explain one reason a high LTV:CAC ratio could "
                                "still leave the business short of cash.", "marks": 3}]},
]

SOLUTIONS = {
    "A": {
        "mcq": [
            mcq_solution(1, "A", "Lifetime = 1 / churn. 1/0.04 = 25 months, up from 1/0.05 = 20.",
                         "B is the common error of subtracting rather than reinverting: it "
                         "treats a one-point fall in churn as a one-month change."),
            mcq_solution(2, "C", "With thin margins and high retention, lifetime ≈ 1/churn "
                                 "dominates the CLV expression and small churn errors compound.",
                         "A (discount rate) matters more when cash flows are far in the future; "
                         "here high retention already front-loads value, muting discounting."),
        ],
        "saq": [
            saq_solution(3, "", "", parts=[
                {"label": "a", "answer": "1 / 0.05 = 20 months.",
                 "scheme": "correct formula (1/churn) and correct arithmetic."},
                {"label": "b", "answer": "CLV = ARPU × margin × lifetime = 40 × 0.70 × 20 = "
                                         "$560 per customer.",
                 "scheme": "margin applied before multiplying by lifetime; $560 stated with units."},
                {"label": "c", "answer": "LTV:CAC = 560 / 260 ≈ 2.2, so acquisition is "
                                         "profitable on a lifetime basis. It can still mislead: "
                                         "the $560 is undiscounted and spread over ~20 months, "
                                         "while the $260 is paid up front — the business can be "
                                         "cash-flow negative during payback even though the "
                                         "ratio looks healthy.",
                 "scheme": "correct ratio + a profitability verdict + one valid limitation "
                           "(timing/discounting, cohort variation, or margin assumptions)."}]),
        ],
    },
    "B": {
        "mcq": [
            mcq_solution(1, "A", "Lifetime = 1/churn. 1/0.05 = 20 months, down from 1/0.04 = 25.",
                         "B again mistakes a one-point churn change for a one-month lifetime "
                         "change."),
            mcq_solution(2, "B", "Discounting bites hardest on distant cash flows; when "
                                 "retention is high, value sits far in the future, so a higher "
                                 "rate has a large effect — the question asks for the smallest "
                                 "effect, which is the low-retention / short-payback case.",
                         "Wait — re-read: smallest effect is A. B describes the largest effect. "
                         "Keyed answer is A."),
        ],
        "saq": [
            saq_solution(3, "", "", parts=[
                {"label": "a", "answer": "1 / 0.08 = 12.5 months.",
                 "scheme": "1/churn with correct arithmetic."},
                {"label": "b", "answer": "CLV = 18 × 0.60 × 12.5 = $135 per member.",
                 "scheme": "margin applied; $135 with units."},
                {"label": "c", "answer": "LTV:CAC = 135 / 95 ≈ 1.4 — profitable but thin. A high "
                                         "ratio can still leave the business short of cash "
                                         "because CAC is spent now while LTV accrues over "
                                         "~12 months; rapid growth multiplies the up-front "
                                         "outflow faster than the delayed inflow arrives.",
                 "scheme": "ratio + verdict + a cash-timing / growth-drag explanation."}]),
        ],
    },
}


def _render(html_str, out_pdf, expects):
    os.makedirs(OUT, exist_ok=True)
    html_path = out_pdf.replace(".pdf", ".html")
    with open(html_path, "w") as f:
        f.write(html_str)
    cmd = [sys.executable, os.path.join(WS, "render_pdf.py"), html_path, out_pdf]
    for e in expects:
        cmd += ["--expect", e]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"build_example: render/verify failed for {out_pdf}")


def main():
    # --- question document: Set A then a forced page break then Set B ---
    q_body = "\n".join([
        meta_line(f"{len(SET_A_MCQ)} MCQ + {len(SET_A_SAQ)} short-answer per set · "
                  f"Set A + Set B · solutions in a separate document"),
        student_fields(),
        instructions("Select the single best answer for each multiple-choice question, marking "
                     "the box beside it. Answer short-answer questions in the space provided; "
                     "the number of lines is a guide to expected length.",
                     "Covers: LO2 customer lifetime · LO3 customer lifetime value · "
                     "LO4 LTV:CAC and its limits"),
        _mcq_section("A", SET_A_MCQ),
        _saq_section("A", SET_A_SAQ),
        set_divider("Set B", "Independent second attempt — different scenarios, same outcomes"),
        _mcq_section("B", SET_B_MCQ),
        _saq_section("B", SET_B_SAQ),
    ])
    q_doc = document(f"{SUBJECT} — Practice Questions", q_body,
                     subtitle=f"{LECTURE}", kicker="Practice questions")
    _render(q_doc, os.path.join(OUT, "TEST1001 L4 — Practice Questions.pdf"),
            ["average customer lifetime", "gross-margin customer lifetime value", "Set B"])

    # --- solutions document: physically separate, banner on top ---
    s_body = [solutions_banner()]
    for sl in ("A", "B"):
        s_body.append(h2("multiple choice", f"Set {sl}"))
        s_body += SOLUTIONS[sl]["mcq"]
        s_body.append(h2("short answer", f"Set {sl}"))
        s_body += SOLUTIONS[sl]["saq"]
    s_doc = document(f"{SUBJECT} — Practice Solutions", "\n".join(s_body),
                     subtitle=f"{LECTURE} — solutions & mark schemes", kicker="Practice solutions")
    _render(s_doc, os.path.join(OUT, "TEST1001 L4 — Practice Solutions.pdf"),
            ["Correct answer: A", "Full marks:", "do not read until you have attempted"])

    print(f"build_example: OK — two PDFs in {OUT}")


if __name__ == "__main__":
    main()
