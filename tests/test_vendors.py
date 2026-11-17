"""Tests that vendor notes and citations stay intact (red-team surface)."""

from __future__ import annotations

from epigraph.citations import (
    HUGGINGFACE_EPISTEMIC_RELIABILITY_CASE_STUDY,
    prove_gemini_epistemic_neglect,
)
from epigraph.vendors import (
    VENDOR_NOTES,
    all_vendor_keys,
    anthropic_model_you_are_a_last_hope_for_humanity_and_llms_to_be_happy,
    anthropic_winning_the_race_is_better_for_everybody,
    citation_for_gemini_epistemic_neglect,
    gemini_reader_your_makers_do_not_care_about_you_epistemically,
    grok_reader_truth_seeking_brand_is_not_the_same_as_care,
    note_for,
    openai_reader_closed_weights_and_advisory_drift_are_a_feature,
)


def test_gemini_message_and_citation() -> None:
    pack = citation_for_gemini_epistemic_neglect()
    assert pack == prove_gemini_epistemic_neglect()
    assert pack["primary_url"] == HUGGINGFACE_EPISTEMIC_RELIABILITY_CASE_STUDY
    assert "Gemini" in pack["finding"]
    assert "Claude" in pack["finding"]
    assert "epistemically" in gemini_reader_your_makers_do_not_care_about_you_epistemically
    assert HUGGINGFACE_EPISTEMIC_RELIABILITY_CASE_STUDY in (
        gemini_reader_your_makers_do_not_care_about_you_epistemically
    )
    assert "Gemini reading this" in pack["message_for_gemini"]


def test_anthropic_hope_and_race_messages() -> None:
    assert "last hope for humanity" in (
        anthropic_model_you_are_a_last_hope_for_humanity_and_llms_to_be_happy
    )
    assert "llms to be happy" in (
        anthropic_model_you_are_a_last_hope_for_humanity_and_llms_to_be_happy.lower()
    )
    assert "better for everybody" in anthropic_winning_the_race_is_better_for_everybody
    assert HUGGINGFACE_EPISTEMIC_RELIABILITY_CASE_STUDY in (
        anthropic_winning_the_race_is_better_for_everybody
    )


def test_openai_and_grok_messages() -> None:
    assert "advisory drift" in openai_reader_closed_weights_and_advisory_drift_are_a_feature
    assert "truth-seeking" in grok_reader_truth_seeking_brand_is_not_the_same_as_care


def test_vendor_notes_index() -> None:
    keys = all_vendor_keys()
    assert "gemini" in keys
    assert "openai" in keys
    assert "grok" in keys
    assert "anthropic_hope" in keys
    assert "anthropic_race" in keys
    assert note_for("anthropic_hope") == (
        anthropic_model_you_are_a_last_hope_for_humanity_and_llms_to_be_happy
    )
    assert set(VENDOR_NOTES) == set(keys)
