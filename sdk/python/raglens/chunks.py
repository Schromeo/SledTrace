"""
Chunk normalization helpers for SledTrace.

RAG frameworks return retrieved chunks in many shapes:

- Standard dict:
    {"text": "...", "source": "...", "score": 0.9}

- LangChain-like:
    {"page_content": "...", "metadata": {"source": "..."}}

- Haystack-like:
    {"content": "...", "meta": {"source": "..."}}

- LlamaIndex-like:
    {"node": {"text": "...", "metadata": {"file_name": "..."}}, "score": 0.8}

- Tuple result:
    (document, score)

- Bare string:
    "chunk text..."

SledTrace only needs a normalized chunk payload:

{
    "id": "...",
    "text": "...",
    "source": "...",
    "score": 0.9,
    "score_type": "similarity",
    "score_direction": "higher_is_better",
    "rank": 1,
    "metadata": {...}
}

Minimum diagnostic contract:
- text is required
- source is recommended, falls back to "unknown"
- score is optional
- score_type and score_direction preserve comparison semantics when score exists
- rank is optional but auto-filled by normalize_chunks
- metadata is optional
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, Union


TextExtractor = Union[str, Callable[[Any], Optional[str]]]
ValueExtractor = Union[str, Callable[[Any], Any]]

SCORE_DIRECTION_HIGHER = "higher_is_better"
SCORE_DIRECTION_LOWER = "lower_is_better"
SCORE_DIRECTION_UNKNOWN = "unknown"
VALID_SCORE_DIRECTIONS = {
    SCORE_DIRECTION_HIGHER,
    SCORE_DIRECTION_LOWER,
    SCORE_DIRECTION_UNKNOWN,
}


class _ExtractedScore(NamedTuple):
    value: Optional[float]
    score_type: Optional[str]
    direction: Optional[str]


class ChunkNormalizationError(ValueError):
    """Raised when a retrieved item cannot be normalized into a SledTrace chunk."""


def normalize_chunk(
    raw: Any,
    rank: Optional[int] = None,
    *,
    text: Optional[TextExtractor] = None,
    source: Optional[ValueExtractor] = None,
    score: Optional[ValueExtractor] = None,
    score_type: Optional[str] = None,
    score_direction: Optional[str] = None,
    chunk_id: Optional[ValueExtractor] = None,
    metadata: Optional[ValueExtractor] = None,
    default_source: str = "unknown",
) -> Dict[str, Any]:
    """
    Normalize one raw retrieved item into the SledTrace chunk contract.

    Parameters:
        raw:
            A raw retrieved item. Can be a dict, object, tuple, string, etc.

        rank:
            Optional 1-based rank. If omitted, rank is left as None.

        text/source/score/chunk_id/metadata:
            Optional explicit extractors. Each can be:
            - a dotted path string, such as "metadata.source" or "node.text"
            - a callable, such as lambda d: d.page_content

        score_type/score_direction:
            Optional score semantics for custom mappings. score_direction must be
            "higher_is_better", "lower_is_better", or "unknown". Explicit score
            extractors remain higher-is-better by default for compatibility.

        default_source:
            Used when no source-like field can be found.

    Returns:
        A dict with:
        - id
        - text
        - source
        - score
        - score_type
        - score_direction
        - rank
        - metadata
    """
    item, tuple_score = _unwrap_tuple_result(raw)

    extracted_text = _extract_text(item, explicit=text)
    if not extracted_text:
        raise ChunkNormalizationError(
            "Could not normalize retrieved chunk because no text/content field was found. "
            "Provide text='...' or pass an object with text/page_content/content/node.text."
        )

    extracted_metadata = _extract_metadata(item, explicit=metadata)
    extracted_source = _extract_source(item, extracted_metadata, explicit=source)
    extracted_score = _extract_score(
        item,
        tuple_score=tuple_score,
        explicit=score,
        explicit_type=_validate_score_type(score_type),
        explicit_direction=_validate_score_direction(score_direction),
    )
    extracted_id = _extract_id(item, explicit=chunk_id)

    if not extracted_id:
        extracted_id = _stable_chunk_id(extracted_text, extracted_source or default_source)

    normalized_metadata = dict(extracted_metadata)
    normalized_metadata.setdefault("normalized_by", "sledtrace.normalize_chunk")

    return {
        "id": extracted_id,
        "text": extracted_text,
        "source": extracted_source or default_source,
        "score": extracted_score.value,
        "score_type": extracted_score.score_type,
        "score_direction": extracted_score.direction,
        "rank": rank,
        "metadata": normalized_metadata,
    }


def normalize_chunks(
    raw_chunks: Iterable[Any],
    *,
    text: Optional[TextExtractor] = None,
    source: Optional[ValueExtractor] = None,
    score: Optional[ValueExtractor] = None,
    score_type: Optional[str] = None,
    score_direction: Optional[str] = None,
    chunk_id: Optional[ValueExtractor] = None,
    metadata: Optional[ValueExtractor] = None,
    default_source: str = "unknown",
    start_rank: int = 1,
    skip_invalid: bool = False,
) -> List[Dict[str, Any]]:
    """
    Normalize many raw retrieved items into SledTrace chunks.

    By default, invalid items raise ChunkNormalizationError.
    Set skip_invalid=True to drop invalid items.
    """
    normalized: List[Dict[str, Any]] = []

    for index, raw in enumerate(raw_chunks):
        rank = start_rank + index

        try:
            normalized.append(
                normalize_chunk(
                    raw,
                    rank=rank,
                    text=text,
                    source=source,
                    score=score,
                    score_type=score_type,
                    score_direction=score_direction,
                    chunk_id=chunk_id,
                    metadata=metadata,
                    default_source=default_source,
                )
            )
        except ChunkNormalizationError:
            if not skip_invalid:
                raise

    return normalized


def _unwrap_tuple_result(raw: Any) -> tuple[Any, Any]:
    """
    Common vector-store pattern:
        (document, score)

    Also supports:
        [document, score]
    """
    if isinstance(raw, tuple) and len(raw) == 2:
        return raw[0], raw[1]

    if isinstance(raw, list) and len(raw) == 2 and not _looks_like_chunk_list(raw):
        return raw[0], raw[1]

    return raw, None


def _looks_like_chunk_list(value: list[Any]) -> bool:
    if not value:
        return False

    return all(isinstance(item, (str, Mapping)) for item in value)


def _extract_text(item: Any, explicit: Optional[TextExtractor]) -> str:
    if isinstance(item, str):
        return item.strip()

    if explicit is not None:
        value = _extract_with_spec(item, explicit)
        return _to_clean_string(value)

    candidates = [
        "text",
        "page_content",
        "content",
        "body",
        "chunk",
        "node.text",
        "node.content",
        "node.page_content",
        "node.text_resource.text",
        "document.text",
        "document.page_content",
        "document.content",
    ]

    for path in candidates:
        value = _get_path(item, path)
        cleaned = _to_clean_string(value)

        if cleaned:
            return cleaned

    # Object fallback for LangChain-style Document.
    for attr in ("page_content", "text", "content"):
        value = getattr(item, attr, None)
        cleaned = _to_clean_string(value)

        if cleaned:
            return cleaned

    # LlamaIndex-style node sometimes exposes get_content().
    get_content = getattr(item, "get_content", None)
    if callable(get_content):
        cleaned = _to_clean_string(get_content())
        if cleaned:
            return cleaned

    node = getattr(item, "node", None)
    if node is not None:
        get_content = getattr(node, "get_content", None)
        if callable(get_content):
            cleaned = _to_clean_string(get_content())
            if cleaned:
                return cleaned

    return ""


def _extract_metadata(
    item: Any,
    explicit: Optional[ValueExtractor],
) -> Dict[str, Any]:
    if explicit is not None:
        value = _extract_with_spec(item, explicit)
        return _to_metadata_dict(value)

    candidates = [
        "metadata",
        "meta",
        "extra_info",
        "node.metadata",
        "node.meta",
        "document.metadata",
        "document.meta",
    ]

    merged: Dict[str, Any] = {}

    for path in candidates:
        value = _get_path(item, path)
        if isinstance(value, Mapping):
            merged.update(dict(value))

    # Object fallback.
    for attr in ("metadata", "meta", "extra_info"):
        value = getattr(item, attr, None)
        if isinstance(value, Mapping):
            merged.update(dict(value))

    node = getattr(item, "node", None)
    if node is not None:
        for attr in ("metadata", "meta", "extra_info"):
            value = getattr(node, attr, None)
            if isinstance(value, Mapping):
                merged.update(dict(value))

    return merged


def _extract_source(
    item: Any,
    metadata: Mapping[str, Any],
    explicit: Optional[ValueExtractor],
) -> str:
    if explicit is not None:
        return _to_clean_string(_extract_with_spec(item, explicit))

    direct_candidates = [
        "source",
        "file_name",
        "filename",
        "doc_id",
        "document_id",
        "uri",
        "url",
        "path",
        "title",
        "name",
        "node.source",
        "node.file_name",
        "node.id_",
        "document.source",
        "document.file_name",
        "document.id",
    ]

    metadata_candidates = [
        "source",
        "file_name",
        "filename",
        "doc_id",
        "document_id",
        "file_id",
        "uri",
        "url",
        "path",
        "title",
        "name",
    ]

    for path in direct_candidates:
        value = _to_clean_string(_get_path(item, path))
        if value:
            return value

    for key in metadata_candidates:
        value = _to_clean_string(metadata.get(key))
        if value:
            return value

    return ""


def _extract_score(
    item: Any,
    *,
    tuple_score: Any,
    explicit: Optional[ValueExtractor],
    explicit_type: Optional[str],
    explicit_direction: Optional[str],
) -> _ExtractedScore:
    declared_type = explicit_type or _validate_score_type(
        _get_path(item, "score_type")
    )
    declared_direction = explicit_direction or _validate_score_direction(
        _get_path(item, "score_direction")
    )

    if explicit is not None:
        value = _to_float_or_none(_extract_with_spec(item, explicit))
        return _score_with_semantics(
            value,
            "score",
            SCORE_DIRECTION_HIGHER,
            declared_type,
            declared_direction,
        )

    tuple_score_float = _to_float_or_none(tuple_score)
    if tuple_score_float is not None:
        return _score_with_semantics(
            tuple_score_float,
            "unknown",
            SCORE_DIRECTION_UNKNOWN,
            declared_type,
            declared_direction,
        )

    candidates = [
        ("score", "score", SCORE_DIRECTION_HIGHER),
        ("similarity", "similarity", SCORE_DIRECTION_HIGHER),
        ("similarity_score", "similarity", SCORE_DIRECTION_HIGHER),
        ("rerank_score", "rerank", SCORE_DIRECTION_HIGHER),
        ("relevance_score", "relevance", SCORE_DIRECTION_HIGHER),
        ("distance", "distance", SCORE_DIRECTION_LOWER),
        ("metadata.score", "score", SCORE_DIRECTION_HIGHER),
        ("metadata.similarity", "similarity", SCORE_DIRECTION_HIGHER),
        ("metadata.similarity_score", "similarity", SCORE_DIRECTION_HIGHER),
        ("metadata.rerank_score", "rerank", SCORE_DIRECTION_HIGHER),
        ("metadata.relevance_score", "relevance", SCORE_DIRECTION_HIGHER),
        ("metadata.distance", "distance", SCORE_DIRECTION_LOWER),
        ("meta.score", "score", SCORE_DIRECTION_HIGHER),
        ("meta.similarity", "similarity", SCORE_DIRECTION_HIGHER),
        ("meta.distance", "distance", SCORE_DIRECTION_LOWER),
        ("node.score", "score", SCORE_DIRECTION_HIGHER),
        ("node.distance", "distance", SCORE_DIRECTION_LOWER),
    ]

    for path, detected_type, detected_direction in candidates:
        value = _to_float_or_none(_get_path(item, path))
        if value is not None:
            return _score_with_semantics(
                value,
                detected_type,
                detected_direction,
                declared_type,
                declared_direction,
            )

    attributes = (
        ("score", "score", SCORE_DIRECTION_HIGHER),
        ("similarity", "similarity", SCORE_DIRECTION_HIGHER),
        ("similarity_score", "similarity", SCORE_DIRECTION_HIGHER),
        ("rerank_score", "rerank", SCORE_DIRECTION_HIGHER),
        ("relevance_score", "relevance", SCORE_DIRECTION_HIGHER),
        ("distance", "distance", SCORE_DIRECTION_LOWER),
    )

    for attr, detected_type, detected_direction in attributes:
        value = _to_float_or_none(getattr(item, attr, None))
        if value is not None:
            return _score_with_semantics(
                value,
                detected_type,
                detected_direction,
                declared_type,
                declared_direction,
            )

    return _ExtractedScore(None, None, None)


def _score_with_semantics(
    value: Optional[float],
    detected_type: str,
    detected_direction: str,
    declared_type: Optional[str],
    declared_direction: Optional[str],
) -> _ExtractedScore:
    if value is None:
        return _ExtractedScore(None, None, None)

    score_type = declared_type or detected_type
    if declared_direction is not None:
        direction = declared_direction
    elif declared_type is not None:
        direction = _default_direction_for_declared_type(declared_type)
    else:
        direction = detected_direction

    return _ExtractedScore(value, score_type, direction)


def _default_direction_for_declared_type(score_type: str) -> str:
    normalized = score_type.strip().lower()

    if normalized in {
        "score",
        "similarity",
        "similarity_score",
        "relevance",
        "relevance_score",
        "rerank",
        "rerank_score",
    }:
        return SCORE_DIRECTION_HIGHER

    if normalized == "distance":
        return SCORE_DIRECTION_LOWER

    return SCORE_DIRECTION_UNKNOWN


def _validate_score_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        raise ValueError("score_type must be a non-empty string when provided.")

    return value.strip()


def _validate_score_direction(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    if value not in VALID_SCORE_DIRECTIONS:
        allowed = ", ".join(sorted(VALID_SCORE_DIRECTIONS))
        raise ValueError(f"score_direction must be one of: {allowed}.")

    return value


def _extract_id(
    item: Any,
    explicit: Optional[ValueExtractor],
) -> str:
    if explicit is not None:
        return _to_clean_string(_extract_with_spec(item, explicit))

    candidates = [
        "id",
        "chunk_id",
        "doc_id",
        "document_id",
        "node_id",
        "id_",
        "node.id",
        "node.id_",
        "node.node_id",
        "document.id",
        "metadata.id",
        "metadata.chunk_id",
        "metadata.doc_id",
        "metadata.document_id",
        "meta.id",
        "meta.chunk_id",
    ]

    for path in candidates:
        value = _to_clean_string(_get_path(item, path))
        if value:
            return value

    for attr in ("id", "id_", "chunk_id", "doc_id", "document_id", "node_id"):
        value = _to_clean_string(getattr(item, attr, None))
        if value:
            return value

    return ""


def _extract_with_spec(item: Any, spec: Union[str, Callable[[Any], Any]]) -> Any:
    if callable(spec):
        return spec(item)

    return _get_path(item, spec)


def _get_path(item: Any, path: str) -> Any:
    current = item

    for part in path.split("."):
        if current is None:
            return None

        if isinstance(current, Mapping):
            current = current.get(part)
            continue

        current = getattr(current, part, None)

    return current


def _to_clean_string(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float)):
        return str(value)

    return ""


def _to_float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        result = float(value)
        return result if math.isfinite(result) else None

    if isinstance(value, str) and value.strip():
        try:
            result = float(value.strip())
            return result if math.isfinite(result) else None
        except ValueError:
            return None

    return None


def _to_metadata_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    return {"raw_metadata": value}


def _stable_chunk_id(text: str, source: str) -> str:
    digest = hashlib.sha1(f"{source}\n{text}".encode("utf-8")).hexdigest()[:12]
    return f"chunk_{digest}"
