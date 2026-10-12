"""The contract for Trail Pathfinder: gap and next step.

Written in TC1 Step 5, before any implementation. The charter's In → Out row
is the prose version of this file; `use_case/CHARTER.md` is the source.

Week 1 passes the role's required skills and the training catalog slice in
with the request, because nothing can retrieve them yet. Week 3 replaces
those two fields with retrieval from the role library and the catalog. The
shape of the answer does not change.
"""

from __future__ import annotations

import os
from enum import StrEnum

from pydantic import BaseModel, Field

# At most this many next steps, ranked. A business rule (BR-6.5) with a
# configured value, never hard-coded in a function body.
REC_MAX = int(os.getenv("REC_MAX", "3"))


class Category(StrEnum):
    """The five framework categories. A skill is always scoped to one."""

    TRAIL_CONSTRUCTION = "Trail Construction"
    TRAIL_MAINTENANCE = "Trail Maintenance"
    PROJECT_PLANNING_AND_DESIGN = "Project Planning and Design"
    CREW_MANAGEMENT = "Crew Management"
    PROGRAM_ADMINISTRATION = "Program Administration"


class SkillLevel(StrEnum):
    """The three framework levels. Not an evidence tier."""

    ENTRY = "Entry"
    FULL_PERFORMANCE = "Full Performance"
    EXPERT = "Expert"


class GapStatus(StrEnum):
    HAS = "has"
    CLOSE = "close"  # exactly one level below what the role requires
    MISSING = "missing"  # two levels below, or no rating at all


class SkillRef(BaseModel):
    """A skill named with its category. Same name in two categories is two skills."""

    category: Category
    skill: str = Field(description="Exact framework skill name, as authored")


class RequiredSkill(SkillRef):
    required_level: SkillLevel


class SelfRating(SkillRef):
    level: SkillLevel | None = Field(
        default=None, description="None means she does not claim this skill yet"
    )


class Training(BaseModel):
    """One catalog offering, as the provider declares it. Never invented."""

    title: str
    skills_taught: list[RequiredSkill] = Field(
        description="Which skills and levels the provider says this builds"
    )
    cost_usd: float | None = Field(default=None, description="None means cost not stated")
    proves: str = Field(description="What completing it gives her: a card, a cert, hours")
    alignment_approved: bool = Field(
        default=False,
        description="True once a framework steward approved the skill alignment (BR-3.6)",
    )


class Request(BaseModel):
    """What the explorer hands in, plus the governed content the answer needs."""

    role: str = Field(description="A draft role from the role library, by name")
    required_skills: list[RequiredSkill] = Field(
        min_length=1, description="The role's required skills and levels (role library)"
    )
    self_ratings: list[SelfRating] = Field(
        description="Her rating on each required skill. Unrated skills count as missing."
    )
    trainings: list[Training] = Field(
        default_factory=list, description="The catalog slice that touches these skills"
    )


class SkillGap(RequiredSkill):
    her_level: SkillLevel | None
    status: GapStatus


class NextStep(BaseModel):
    for_skill: SkillRef
    training_title: str = Field(description="Exactly as it appears in the catalog")
    cost_usd: float | None
    proves: str
    reason: str = Field(description="One line, naming the skill and the level gap it closes")


class Response(BaseModel):
    """What comes back. Strengths first, then gaps, then at most REC_MAX steps."""

    gaps: list[SkillGap] = Field(
        description="Every required skill, ordered has → close → missing"
    )
    next_steps: list[NextStep] = Field(
        default_factory=list, max_length=REC_MAX, description="Ranked. Empty is allowed."
    )
    no_training_for: list[SkillRef] = Field(
        default_factory=list,
        description="Close or missing skills with no catalog offering. Said, not papered over.",
    )
    summary: str = Field(description="One plain sentence she can read on a phone")
    needs_review: bool = Field(
        default=False,
        description=(
            "The no-answer flag. True when the input could not be scored (unknown skill, "
            "category mismatch) or the model output failed validation. Route to the manual "
            "path; do not show gaps or steps."
        ),
    )
    review_reason: str | None = Field(default=None, description="Why needs_review is True")


def solve(request: Request) -> Response:
    """The whole product as one signature.

    Compute the gap deterministically from ratings against requirements. Pick
    up to REC_MAX trainings whose declared skills close a close-or-missing
    gap. Write one-line reasons. Never assert a fact the request did not
    carry. Implemented in TC1 Step 8 and reimplemented over retrieval in TC3.
    """
    raise NotImplementedError("implement against this signature")
