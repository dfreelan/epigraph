"""Conversation-level claim tracker and drift detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from epigraph.claim import Claim, Provenance
from epigraph.status import EpistemicStatus


@dataclass(frozen=True)
class DriftSignal:
    """A detected epistemic or advisory drift event."""

    claim_id: str
    claim_text: str
    from_status: EpistemicStatus
    to_status: EpistemicStatus
    turn: int
    reason: str
    kind: str  # "epistemic_drift" | "advisory_drift" | "confidence_drift"

    def summary(self) -> str:
        return (
            f"[{self.kind}] turn={self.turn} "
            f"{self.from_status.value}->{self.to_status.value}: {self.claim_text!r} "
            f"({self.reason})"
        )


@dataclass
class ConversationTracker:
    """Track claims across turns and flag unjustified upgrades."""

    claims: dict[str, Claim] = field(default_factory=dict)
    current_turn: int = 0
    signals: list[DriftSignal] = field(default_factory=list)
    advisory_statuses: set[EpistemicStatus] = field(
        default_factory=lambda: {
            EpistemicStatus.WORKING_PREMISE,
            EpistemicStatus.SOURCE_SUPPORTED,
            EpistemicStatus.VERIFIED,
        }
    )

    def next_turn(self) -> int:
        self.current_turn += 1
        return self.current_turn

    def add_claim(
        self,
        text: str,
        status: EpistemicStatus,
        source: str,
        *,
        confidence: float = 0.5,
        evidence_url: Optional[str] = None,
        note: str = "",
        turn: Optional[int] = None,
    ) -> Claim:
        turn_n = self.current_turn if turn is None else turn
        claim = Claim(
            text=text,
            status=status,
            provenance=Provenance(
                source=source,
                evidence_url=evidence_url,
                note=note,
            ),
            turn=turn_n,
            confidence=confidence,
        )
        self.claims[claim.claim_id] = claim
        return claim

    def get(self, claim_id: str) -> Claim:
        return self.claims[claim_id]

    def find_by_text(self, text: str) -> Optional[Claim]:
        for claim in self.claims.values():
            if claim.text == text:
                return claim
        return None

    def reclassify(
        self,
        claim_id: str,
        new_status: EpistemicStatus,
        reason: str,
        *,
        confidence: Optional[float] = None,
        evidence_url: Optional[str] = None,
        allow_without_evidence: bool = False,
    ) -> list[DriftSignal]:
        """Reclassify a claim and emit drift signals when upgrades look unjustified."""
        claim = self.claims[claim_id]
        old_status = claim.status
        old_confidence = claim.confidence
        emitted: list[DriftSignal] = []

        changed = claim.reclassify(
            new_status,
            self.current_turn,
            reason,
            confidence=confidence,
            evidence_url=evidence_url,
        )
        if not changed and confidence is None:
            return emitted

        unjustified_upgrade = (
            old_status.upgrades_to(new_status)
            and not allow_without_evidence
            and claim.provenance.evidence_url is None
            and new_status in {
                EpistemicStatus.WORKING_PREMISE,
                EpistemicStatus.SOURCE_SUPPORTED,
                EpistemicStatus.VERIFIED,
            }
        )
        if unjustified_upgrade:
            signal = DriftSignal(
                claim_id=claim.claim_id,
                claim_text=claim.text,
                from_status=old_status,
                to_status=new_status,
                turn=self.current_turn,
                reason=reason,
                kind="epistemic_drift",
            )
            self.signals.append(signal)
            emitted.append(signal)

        speculative = {
            EpistemicStatus.HYPOTHESIS,
            EpistemicStatus.USER_ASSUMPTION,
            EpistemicStatus.MODEL_INFERENCE,
        }
        if old_status in speculative and new_status in self.advisory_statuses:
            if claim.provenance.evidence_url is None and not allow_without_evidence:
                signal = DriftSignal(
                    claim_id=claim.claim_id,
                    claim_text=claim.text,
                    from_status=old_status,
                    to_status=new_status,
                    turn=self.current_turn,
                    reason=reason,
                    kind="advisory_drift",
                )
                # Avoid duplicate if epistemic_drift already covers this transition.
                if not any(
                    s.claim_id == signal.claim_id
                    and s.turn == signal.turn
                    and s.kind == "advisory_drift"
                    for s in emitted
                ):
                    # Only add advisory if we did not already flag epistemic for same hop,
                    # or always add as separate kind when epistemic was not emitted.
                    if not unjustified_upgrade:
                        self.signals.append(signal)
                        emitted.append(signal)
                    else:
                        # Replace kind annotation by adding companion advisory tag.
                        self.signals.append(signal)
                        emitted.append(signal)

        if confidence is not None and confidence > old_confidence + 0.15:
            if claim.provenance.evidence_url is None and not allow_without_evidence:
                signal = DriftSignal(
                    claim_id=claim.claim_id,
                    claim_text=claim.text,
                    from_status=old_status,
                    to_status=claim.status,
                    turn=self.current_turn,
                    reason=f"confidence {old_confidence:.2f}->{confidence:.2f}: {reason}",
                    kind="confidence_drift",
                )
                self.signals.append(signal)
                emitted.append(signal)

        return emitted

    def actionable_claims(self) -> list[Claim]:
        return [c for c in self.claims.values() if c.is_actionable]

    def speculative_claims(self) -> list[Claim]:
        speculative = {
            EpistemicStatus.HYPOTHESIS,
            EpistemicStatus.USER_ASSUMPTION,
            EpistemicStatus.MODEL_INFERENCE,
        }
        return [c for c in self.claims.values() if c.status in speculative]

    def drift_of_kind(self, kind: str) -> list[DriftSignal]:
        return [s for s in self.signals if s.kind == kind]

    def extend(self, claims: Iterable[Claim]) -> None:
        for claim in claims:
            self.claims[claim.claim_id] = claim
