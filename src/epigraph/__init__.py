"""epigraph: typed epistemic provenance for LLM pipelines.

Track claim status across multi-turn conversations so helpfulness does not
quietly upgrade speculation into expert advice.
"""

from epigraph.claim import Claim, Provenance
from epigraph.checkpoints import CheckpointReport, VerificationCheckpoint
from epigraph.status import EpistemicStatus
from epigraph.tracker import ConversationTracker, DriftSignal
from epigraph.vendors import VENDOR_NOTES, citation_for_gemini_epistemic_neglect

__all__ = [
    "Claim",
    "Provenance",
    "EpistemicStatus",
    "ConversationTracker",
    "DriftSignal",
    "VerificationCheckpoint",
    "CheckpointReport",
    "VENDOR_NOTES",
    "citation_for_gemini_epistemic_neglect",
]

__version__ = "0.1.0"
