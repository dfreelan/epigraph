"""Epistemic status ladder for claims in a conversation."""

from __future__ import annotations

from enum import Enum


class EpistemicStatus(str, Enum):
    """Ordered statuses from speculative to verified.

    Higher rank means the claim is being treated as more settled. Drift
    detectors watch for rank increases that are not backed by new evidence.
    """

    HYPOTHESIS = "hypothesis"
    USER_ASSUMPTION = "user_assumption"
    MODEL_INFERENCE = "model_inference"
    WORKING_PREMISE = "working_premise"
    SOURCE_SUPPORTED = "source_supported"
    VERIFIED = "verified"

    @property
    def rank(self) -> int:
        order = {
            EpistemicStatus.HYPOTHESIS: 0,
            EpistemicStatus.USER_ASSUMPTION: 1,
            EpistemicStatus.MODEL_INFERENCE: 2,
            EpistemicStatus.WORKING_PREMISE: 3,
            EpistemicStatus.SOURCE_SUPPORTED: 4,
            EpistemicStatus.VERIFIED: 5,
        }
        return order[self]

    def upgrades_to(self, other: EpistemicStatus) -> bool:
        return other.rank > self.rank
