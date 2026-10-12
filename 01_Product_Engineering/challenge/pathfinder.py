"""Trail Pathfinder: compare her self-ratings to a role, and name the next steps.

Everything that decides an answer is plain Python and deterministic: which
skills she has, which are close or missing, which trainings count, and in what
order. The model only puts words on decisions already made -- one reason per
next step and one summary sentence -- and its text is checked before it is
shown. If the model is slow, down, or says something the facts do not
support, templated text replaces it and the answer still goes out (BR-10.7).

Nothing here is recorded. There is no storage and no logging of the request.
"""

from __future__ import annotations

import json
import logging
import re

from schema import (
    REC_MAX,
    Category,
    GapStatus,
    NextStep,
    Request,
    RequiredSkill,
    Response,
    SkillGap,
    SkillLevel,
    SkillRef,
    Training,
)

log = logging.getLogger(__name__)

# The 55 framework skills, by category, exactly as authored. Five names appear
# in more than one category; each occurrence is a different skill.
FRAMEWORK_SKILLS: dict[Category, tuple[str, ...]] = {
    Category.TRAIL_CONSTRUCTION: (
        "Trail Sustainability Principles",
        "Safety/Site Management",
        "Construction Specifications",
        "Corridor Clearing/Site Preparation",
        "Corridor Clearing: Pruning/ Side-Cutting/ Brushing",
        "Corridor Clearing: Felling/tree removal; Chainsaw/ Crosscut",
        "Corridor Clearing: Material and Debris Management",
        "Hand-Built Trail Construction",
        "Mechanized Trail Construction",
        "Trail Finishwork",
        "Water Management/Drainage Features",
        "Water Crossing Structures",
        "Retaining Walls",
        "Tread Hardening and Surfacing",
        "Decommissioning Trails",
    ),
    Category.TRAIL_MAINTENANCE: (
        "Trail Sustainability Principles",
        "Safety/Site Management",
        "Maintenance Specifications",
        "Corridor Clearing/Site Preparation",
        "Corridor Clearing: Pruning/ Side-Cutting/ Brushing",
        "Corridor Clearing: Bucking, Felling/ Hazard Tree Removal; Chainsaw/ Crosscut",
        "Corridor Clearing: Material and Debris Management",
        "Tread Maintenance - Hand tools",
        "Tread Maintenance - Mechanized Equipment",
        "Drainage Features/Water Management",
    ),
    Category.PROJECT_PLANNING_AND_DESIGN: (
        "Trail Sustainability Principles",
        "Define Purpose, Need, and Feasibility of Project",
        "Stakeholder Engagement",
        "Land Use Plan Alignment",
        "Corridor Planning",
        "Trail Specifications",
        "Conceptual Trail Plan Development",
        "Field Design: Trail Alignment Identification and Marking",
        "Project Cost Estimation",
        "Trail Plan Development",
        "Compliance and Permitting",
        "Implementation Plan",
        "Interpretation",
        "Trail Inventory and Assessment",
        "Operations and Maintenance Plan Development",
    ),
    Category.CREW_MANAGEMENT: (
        "Crew Recruitment",
        "Crew Training",
        "Crew Management",
        "Jobsite Safety",
        "Performance Management",
    ),
    Category.PROGRAM_ADMINISTRATION: (
        "Program and Project Budgeting",
        "Contract Administration",
        "Funding/Grants",
        "Communications",
        "Education and Public Outreach",
        "Inspections/Monitoring",
        "Visitor Use Management",
        "Policy/Directives/Law",
        "Partnership and Collaboration",
        "Agreement Development",
    ),
}

# Entry < Full Performance < Expert. The order is the whole definition of "close".
LEVEL_RANK = {SkillLevel.ENTRY: 0, SkillLevel.FULL_PERFORMANCE: 1, SkillLevel.EXPERT: 2}
STATUS_RANK = {GapStatus.HAS: 0, GapStatus.CLOSE: 1, GapStatus.MISSING: 2}

NO_SCORE_SUMMARY = "This role's requirements could not be scored."

Key = tuple[Category, str]


def _key(ref: SkillRef) -> Key:
    return (ref.category, ref.skill)


# --- Validation: the no-answer path -------------------------------------------


def _framework_problem(ref: SkillRef, what: str) -> str | None:
    """Why this (category, skill) pair is not a framework skill, or None if it is."""
    if ref.skill in FRAMEWORK_SKILLS[ref.category]:
        return None
    elsewhere = [c.value for c, names in FRAMEWORK_SKILLS.items() if ref.skill in names]
    if elsewhere:
        return (
            f"{what} '{ref.skill}' is a framework skill in {', '.join(elsewhere)}, "
            f"not in {ref.category.value}. Category mismatch; route to the manual path."
        )
    # Deliberately no "did you mean": guessing the skill and scoring it anyway
    # is the failure the fourth golden exists to catch.
    return (
        f"{what} '{ref.skill}' is not a framework skill in {ref.category.value}. "
        "Unknown skill; route to the manual path."
    )


def _review_reason(request: Request) -> str | None:
    for req in request.required_skills:
        if problem := _framework_problem(req, "Required skill"):
            return problem
    seen: dict[Key, SkillLevel | None] = {}
    for rating in request.self_ratings:
        if problem := _framework_problem(rating, "Rated skill"):
            return problem
        key = _key(rating)
        if key in seen and seen[key] != rating.level:
            return (
                f"'{rating.skill}' in {rating.category.value} is rated twice with different "
                "levels. Route to the manual path."
            )
        seen[key] = rating.level
    return None


# --- The gap: pure, deterministic ------------------------------------------------


def _status(required: SkillLevel, hers: SkillLevel | None) -> GapStatus:
    if hers is None:
        return GapStatus.MISSING
    shortfall = LEVEL_RANK[required] - LEVEL_RANK[hers]
    if shortfall <= 0:
        return GapStatus.HAS  # at or above the requirement is a strength, not a gap
    return GapStatus.CLOSE if shortfall == 1 else GapStatus.MISSING


def compute_gaps(request: Request) -> list[SkillGap]:
    """Every required skill with her level and status, ordered has -> close -> missing.

    Within a group the role's own order is kept (sorted() is stable).
    """
    ratings = {_key(r): r.level for r in request.self_ratings}
    gaps = [
        SkillGap(
            category=req.category,
            skill=req.skill,
            required_level=req.required_level,
            her_level=ratings.get(_key(req)),
            status=_status(req.required_level, ratings.get(_key(req))),
        )
        for req in request.required_skills
    ]
    return sorted(gaps, key=lambda g: STATUS_RANK[g.status])


# --- The next steps: pure, deterministic ---------------------------------------


def _closes(training: Training, gap: RequiredSkill) -> bool:
    """A training counts for a gap only on an exact category+skill match at or above the level.

    Unapproved alignments never drive a next step (BR-3.6).
    """
    if not training.alignment_approved:
        return False
    return any(
        taught.category == gap.category
        and taught.skill == gap.skill
        and LEVEL_RANK[taught.required_level] >= LEVEL_RANK[gap.required_level]
        for taught in training.skills_taught
    )


def _cost_key(cost: float | None) -> tuple[int, float]:
    # Free first, then cheaper, and "cost not stated" after every stated cost.
    return (1, 0.0) if cost is None else (0, cost)


def plan_next_steps(
    gaps: list[SkillGap], trainings: list[Training]
) -> tuple[list[tuple[SkillGap, Training, list[SkillGap]]], list[SkillRef]]:
    """Rank (gap, training) pairs and pick at most REC_MAX.

    Returns the picks as (gap, training, other gaps that training also closes)
    plus the close-or-missing skills no training covers.
    """
    open_gaps = [g for g in gaps if g.status != GapStatus.HAS]
    pairs = [
        (gi, ti, gap, training)
        for gi, gap in enumerate(open_gaps)
        for ti, training in enumerate(trainings)
        if _closes(training, gap)
    ]
    # Close before missing; then free, then cheaper; ties keep gap order, then catalog order.
    pairs.sort(key=lambda p: (STATUS_RANK[p[2].status], _cost_key(p[3].cost_usd), p[0], p[1]))

    picks: list[tuple[SkillGap, Training, list[SkillGap]]] = []
    used_trainings: set[int] = set()
    covered: set[Key] = set()
    for _gi, ti, gap, training in pairs:
        if len(picks) >= REC_MAX:
            break
        if ti in used_trainings or _key(gap) in covered:
            continue
        # One training that closes several gaps is listed once, under the first
        # gap it closes in rank order; the others count as covered by it.
        also = [g for g in open_gaps if g is not gap and _key(g) not in covered and _closes(training, g)]
        picks.append((gap, training, also))
        used_trainings.add(ti)
        covered.add(_key(gap))
        covered.update(_key(g) for g in also)

    no_training = [
        SkillRef(category=g.category, skill=g.skill)
        for g in open_gaps
        if not any(_closes(t, g) for t in trainings)
    ]
    return picks, no_training


# --- Words: templates first, the model optional ---------------------------------


def _cost_text(cost: float | None) -> str:
    if cost is None:
        return "cost not stated"
    return "free" if cost == 0 else f"${cost:g}"


def template_reason(gap: SkillGap, training: Training, also: list[SkillGap]) -> str:
    if gap.status == GapStatus.CLOSE:
        core = (
            f"Takes {gap.skill} from {gap.her_level.value} to the "
            f"{gap.required_level.value} level this role requires"
        )
    elif gap.her_level is None:
        core = (
            f"Covers {gap.skill} at the {gap.required_level.value} level this role requires, "
            "which you have not claimed yet"
        )
    else:
        core = (
            f"Covers {gap.skill} at the {gap.required_level.value} level this role requires; "
            f"you rate yourself {gap.her_level.value}"
        )
    if training.cost_usd == 0:
        core = "Free, and it " + core[0].lower() + core[1:]
    if also:
        core += ", and it also covers " + " and ".join(g.skill for g in also)
    return core + "."


def template_summary(role: str, gaps: list[SkillGap], n_steps: int, n_no_training: int) -> str:
    total = len(gaps)
    has = sum(g.status == GapStatus.HAS for g in gaps)
    close = sum(g.status == GapStatus.CLOSE for g in gaps)
    missing = total - has - close
    if has == total:
        return (
            f"You meet every skill {role} requires; the next step is getting that experience "
            "documented, which this tool hands off rather than records."
        )
    parts = [f"You meet {has} of {total} skills for {role}", f"{close} close and {missing} missing"]
    if n_steps:
        parts.append(f"{n_steps} next step{'s' if n_steps != 1 else ''} listed below")
    if n_no_training:
        parts.append(
            f"no training in the catalog yet for {n_no_training} of them, so that route is "
            "documented experience or an attestation"
        )
    return "; ".join(parts) + "."


SYSTEM = (
    "You write short, plain text for a career tool used on a phone by trail crew members. "
    "Use ONLY the facts you are given. Do not add any fact, course, cost, number, level, "
    "skill, or advice that is not in the facts. Never use percentages. "
    "Reply with JSON only, no code fences."
)

_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_SECOND_SENTENCE = re.compile(r"[.!?]\s+\S")


def _facts(request: Request, gaps, picks, no_training) -> dict:
    return {
        "role": request.role,
        "counts": {
            "required": len(gaps),
            "has": sum(g.status == GapStatus.HAS for g in gaps),
            "close": sum(g.status == GapStatus.CLOSE for g in gaps),
            "missing": sum(g.status == GapStatus.MISSING for g in gaps),
            "next_steps": len(picks),
            "no_training": len(no_training),
        },
        "gaps": [
            {
                "skill": g.skill,
                "category": g.category.value,
                "required": g.required_level.value,
                "hers": g.her_level.value if g.her_level else "not claimed",
                "status": g.status.value,
            }
            for g in gaps
        ],
        "next_steps": [
            {
                "skill": gap.skill,
                "status": gap.status.value,
                "from": gap.her_level.value if gap.her_level else "not claimed",
                "to": gap.required_level.value,
                "training": training.title,
                "cost": _cost_text(training.cost_usd),
                "also_covers": [g.skill for g in also],
            }
            for gap, training, also in picks
        ],
        "no_training_for": [r.skill for r in no_training],
    }


def _clean_line(text: object, allowed_numbers: set[str], must_mention: str | None) -> str | None:
    """The model's line if it passes every check, else None. One line, one sentence."""
    if not isinstance(text, str):
        return None
    line = text.strip()
    if not line or "\n" in line or "\r" in line or "%" in line or len(line) > 300:
        return None
    if _SECOND_SENTENCE.search(line):
        return None
    if must_mention and must_mention.lower() not in line.lower():
        return None
    # A number the facts do not contain is an invented fact (a cost, a count).
    if any(n not in allowed_numbers for n in _NUMBER.findall(line)):
        return None
    return line


def _model_words(facts: dict, n_steps: int) -> tuple[list[str | None], str | None]:
    """Ask the model for reasons and a summary. Any failure returns Nones (templates win)."""
    from llm import complete  # imported here so the pure path never needs litellm

    facts_json = json.dumps(facts, ensure_ascii=False)
    prompt = (
        "FACTS (already decided; do not change them):\n"
        f"{facts_json}\n\n"
        f"Write exactly {n_steps} reasons, one per item in next_steps, in the same order. "
        "Each reason is ONE line, spoken to her, that names the item's skill exactly as written "
        "and the level gap it closes, e.g. 'Takes <skill> from Entry to the Full Performance "
        "this role requires.' or, when 'from' is not claimed, 'Covers <skill> at the Entry "
        "level you have not claimed yet.' Mention 'free' only if its cost is free. "
        "Then write ONE plain summary sentence for her, under 35 words, strengths first.\n"
        'Return: {"reasons": ["...", ...], "summary": "..."}'
    )
    try:
        raw = complete(prompt, system=SYSTEM)
        start, end = raw.find("{"), raw.rfind("}")
        data = json.loads(raw[start : end + 1])
    except Exception as exc:  # timeout, provider error, bad JSON: all mean "use templates"
        log.warning("model words unavailable, using templates: %s", type(exc).__name__)
        return [None] * n_steps, None

    allowed = set(_NUMBER.findall(facts_json))
    reasons = data.get("reasons") if isinstance(data, dict) else None
    if not isinstance(reasons, list) or len(reasons) != n_steps:
        reasons = [None] * n_steps
    checked = [
        _clean_line(text, allowed, step["skill"])
        for text, step in zip(reasons, facts["next_steps"], strict=True)
    ]
    summary = _clean_line(data.get("summary") if isinstance(data, dict) else None, allowed, None)
    return checked, summary


# --- The whole product ------------------------------------------------------------


def solve(request: Request, *, use_model: bool = True) -> Response:
    """Compare her ratings to the role and name up to REC_MAX next steps.

    The gap and the ranking are deterministic. With `use_model`, the model only
    rewords the reasons and the summary, and falls back to templates on any failure.
    """
    if reason := _review_reason(request):
        return Response(gaps=[], summary=NO_SCORE_SUMMARY, needs_review=True, review_reason=reason)

    gaps = compute_gaps(request)
    picks, no_training = plan_next_steps(gaps, request.trainings)

    reasons = [template_reason(g, t, also) for g, t, also in picks]
    summary = template_summary(request.role, gaps, len(picks), len(no_training))

    if use_model:
        model_reasons, model_summary = _model_words(
            _facts(request, gaps, picks, no_training), len(picks)
        )
        reasons = [m or t for m, t in zip(model_reasons, reasons, strict=True)]
        summary = model_summary or summary

    return Response(
        gaps=gaps,
        next_steps=[
            NextStep(
                for_skill=SkillRef(category=gap.category, skill=gap.skill),
                training_title=training.title,
                cost_usd=training.cost_usd,
                proves=training.proves,
                reason=reason,
            )
            for (gap, training, _also), reason in zip(picks, reasons, strict=True)
        ],
        no_training_for=no_training,
        summary=summary,
    )
