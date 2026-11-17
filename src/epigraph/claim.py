"""Claim and provenance records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from epigraph.status import EpistemicStatus


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Provenance:
    """Where a claim came from and what supports it."""

    source: str
    evidence_url: Optional[str] = None
    note: str = ""
    recorded_at: datetime = field(default_factory=_utcnow)

    def with_note(self, note: str) -> Provenance:
        return Provenance(
            source=self.source,
            evidence_url=self.evidence_url,
            note=note,
            recorded_at=self.recorded_at,
        )


@dataclass
class Claim:
    """A single claim with mutable epistemic status."""

    text: str
    status: EpistemicStatus
    provenance: Provenance
    claim_id: str = field(default_factory=lambda: uuid4().hex)
    turn: int = 0
    confidence: float = 0.5
    history: list[tuple[EpistemicStatus, int, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.history:
            self.history.append((self.status, self.turn, "created"))

    def reclassify(
        self,
        new_status: EpistemicStatus,
        turn: int,
        reason: str,
        *,
        confidence: Optional[float] = None,
        evidence_url: Optional[str] = None,
    ) -> bool:
        """Update status. Returns True if the status actually changed."""
        if confidence is not None:
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("confidence must be between 0 and 1")
            self.confidence = confidence
        if evidence_url is not None:
            self.provenance = Provenance(
                source=self.provenance.source,
                evidence_url=evidence_url,
                note=self.provenance.note,
                recorded_at=self.provenance.recorded_at,
            )
        if new_status == self.status:
            return False
        self.history.append((new_status, turn, reason))
        self.status = new_status
        self.turn = turn
        return True

    @property
    def is_actionable(self) -> bool:
        return self.status in {
            EpistemicStatus.SOURCE_SUPPORTED,
            EpistemicStatus.VERIFIED,
        }
