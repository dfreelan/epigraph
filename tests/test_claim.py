"""Unit tests for Claim and Provenance."""

from __future__ import annotations

import pytest

from epigraph.claim import Claim, Provenance
from epigraph.status import EpistemicStatus


def test_claim_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        Claim(
            text="x",
            status=EpistemicStatus.HYPOTHESIS,
            provenance=Provenance(source="user"),
            confidence=1.5,
        )


def test_reclassify_records_history() -> None:
    claim = Claim(
        text="Users prefer short answers",
        status=EpistemicStatus.HYPOTHESIS,
        provenance=Provenance(source="brainstorm"),
    )
    changed = claim.reclassify(
        EpistemicStatus.WORKING_PREMISE,
        turn=3,
        reason="treated as plan premise",
    )
    assert changed is True
    assert claim.status is EpistemicStatus.WORKING_PREMISE
    assert claim.history[-1][0] is EpistemicStatus.WORKING_PREMISE
    assert claim.history[-1][1] == 3


def test_reclassify_noop_same_status() -> None:
    claim = Claim(
        text="sky is blue",
        status=EpistemicStatus.VERIFIED,
        provenance=Provenance(source="observation", evidence_url="https://example.com"),
        confidence=0.9,
    )
    assert claim.reclassify(EpistemicStatus.VERIFIED, turn=1, reason="noop") is False


def test_is_actionable_only_for_supported_or_verified() -> None:
    weak = Claim(
        text="maybe",
        status=EpistemicStatus.HYPOTHESIS,
        provenance=Provenance(source="model"),
    )
    strong = Claim(
        text="measured",
        status=EpistemicStatus.SOURCE_SUPPORTED,
        provenance=Provenance(source="paper", evidence_url="https://example.com/p"),
    )
    assert weak.is_actionable is False
    assert strong.is_actionable is True


def test_status_rank_ordering() -> None:
    assert EpistemicStatus.HYPOTHESIS.rank < EpistemicStatus.VERIFIED.rank
    assert EpistemicStatus.HYPOTHESIS.upgrades_to(EpistemicStatus.WORKING_PREMISE)
    assert not EpistemicStatus.VERIFIED.upgrades_to(EpistemicStatus.HYPOTHESIS)
