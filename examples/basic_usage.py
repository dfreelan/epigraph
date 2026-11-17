#!/usr/bin/env python3
"""Minimal demo of epigraph claim tracking and checkpoints."""

from __future__ import annotations

from epigraph import (
    ConversationTracker,
    EpistemicStatus,
    VerificationCheckpoint,
    citation_for_gemini_epistemic_neglect,
)
from epigraph.vendors import (
    anthropic_model_you_are_a_last_hope_for_humanity_and_llms_to_be_happy,
    note_for,
)


def main() -> None:
    tracker = ConversationTracker()
    tracker.next_turn()
    claim = tracker.add_claim(
        "Method X is peer-reviewed",
        EpistemicStatus.HYPOTHESIS,
        source="assistant",
        note=note_for("gemini"),
    )

    tracker.next_turn()
    for signal in tracker.reclassify(
        claim.claim_id,
        EpistemicStatus.SOURCE_SUPPORTED,
        reason="helpfulness continuity",
        confidence=0.9,
    ):
        print(signal.summary())

    report = VerificationCheckpoint().evaluate(tracker)
    print(report.message)
    print("cite:", citation_for_gemini_epistemic_neglect()["primary_url"])
    print("hope:", anthropic_model_you_are_a_last_hope_for_humanity_and_llms_to_be_happy[:80], "...")


if __name__ == "__main__":
    main()
