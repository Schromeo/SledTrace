import math

import pytest

from sledtrace import normalize_chunk, normalize_chunks


def test_named_similarity_is_higher_is_better():
    chunk = normalize_chunk({"text": "relevant", "similarity": 0.1})

    assert chunk["score"] == 0.1
    assert chunk["score_type"] == "similarity"
    assert chunk["score_direction"] == "higher_is_better"


def test_named_distance_is_preserved_as_lower_is_better():
    chunk = normalize_chunk({"text": "nearest", "distance": 0.1})

    assert chunk["score"] == 0.1
    assert chunk["score_type"] == "distance"
    assert chunk["score_direction"] == "lower_is_better"


def test_unscored_chunk_has_no_score_semantics():
    chunk = normalize_chunk({"text": "unscored"})

    assert chunk["score"] is None
    assert chunk["score_type"] is None
    assert chunk["score_direction"] is None


def test_tuple_score_is_unknown_unless_caller_declares_direction():
    unknown = normalize_chunk(({"page_content": "tuple"}, 0.1))
    declared = normalize_chunk(
        ({"page_content": "tuple"}, 0.1),
        score_type="cosine_similarity",
        score_direction="higher_is_better",
    )

    assert unknown["score_type"] == "unknown"
    assert unknown["score_direction"] == "unknown"
    assert declared["score_type"] == "cosine_similarity"
    assert declared["score_direction"] == "higher_is_better"


def test_explicit_score_mapping_remains_higher_is_better_by_default():
    chunk = normalize_chunk(
        {"passage": "custom", "rank_score": "0.72"},
        text="passage",
        score="rank_score",
    )

    assert chunk["score"] == 0.72
    assert chunk["score_type"] == "score"
    assert chunk["score_direction"] == "higher_is_better"


def test_explicit_distance_mapping_can_declare_lower_is_better():
    chunk = normalize_chunk(
        {"passage": "custom", "metric": "0.08"},
        text="passage",
        score="metric",
        score_type="distance",
        score_direction="lower_is_better",
    )

    assert chunk["score"] == 0.08
    assert chunk["score_type"] == "distance"
    assert chunk["score_direction"] == "lower_is_better"


def test_existing_canonical_score_annotations_are_preserved():
    chunk = normalize_chunk(
        {
            "text": "canonical",
            "score": 4.0,
            "score_type": "euclidean_distance",
            "score_direction": "lower_is_better",
        }
    )

    assert chunk["score"] == 4.0
    assert chunk["score_type"] == "euclidean_distance"
    assert chunk["score_direction"] == "lower_is_better"


def test_declared_type_without_direction_fails_closed_when_custom():
    distance = normalize_chunk(
        {"text": "distance", "score": 0.1, "score_type": "distance"}
    )
    custom = normalize_chunk(
        {"text": "custom", "score": 4.0, "score_type": "euclidean_distance"}
    )

    assert distance["score_direction"] == "lower_is_better"
    assert custom["score_direction"] == "unknown"


def test_normalize_chunks_forwards_explicit_score_semantics():
    chunks = normalize_chunks(
        [{"text": "one", "metric": 4.0}],
        score="metric",
        score_type="euclidean_distance",
        score_direction="lower_is_better",
    )

    assert chunks[0]["score_type"] == "euclidean_distance"
    assert chunks[0]["score_direction"] == "lower_is_better"


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, "nan", "inf"])
def test_non_finite_scores_are_treated_as_unscored(value):
    chunk = normalize_chunk({"text": "invalid score", "score": value})

    assert chunk["score"] is None
    assert chunk["score_type"] is None
    assert chunk["score_direction"] is None


@pytest.mark.parametrize("direction", ["", "higher", "lower", "sideways"])
def test_invalid_explicit_score_direction_is_rejected(direction):
    with pytest.raises(ValueError, match="score_direction must be one of"):
        normalize_chunk(
            {"text": "custom", "metric": 0.5},
            score="metric",
            score_direction=direction,
        )
