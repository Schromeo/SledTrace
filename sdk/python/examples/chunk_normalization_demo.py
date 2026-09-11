"""
SledTrace Chunk Normalization Demo

This demo shows how SledTrace can accept retrieval outputs that look like
common RAG framework results instead of requiring one strict chunk shape.

Run:

  cd sdk/python
  python -m examples.chunk_normalization_demo

This demo does not require a collector, dashboard, or LLM API key.
It only demonstrates SDK-side normalization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from sledtrace import normalize_chunk, normalize_chunks


@dataclass
class LangChainLikeDocument:
    page_content: str
    metadata: Dict[str, Any]


@dataclass
class HaystackLikeDocument:
    content: str
    meta: Dict[str, Any]
    score: float
    id: str


@dataclass
class LlamaIndexLikeNode:
    text: str
    metadata: Dict[str, Any]
    node_id: str


@dataclass
class LlamaIndexLikeNodeWithScore:
    node: LlamaIndexLikeNode
    score: float


def print_case(title: str, value: Any) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> int:
    standard_dict = {
        "id": "refund-policy-current::chunk-1",
        "text": "Customers may return most physical products within 30 days.",
        "source": "refund_policy_current.md",
        "score": 0.93,
        "metadata": {
            "doc_type": "markdown",
            "version": "current",
            "section": "Refund window",
        },
    }

    langchain_like_dict = {
        "page_content": "Refunds are usually processed within 5 to 10 business days.",
        "metadata": {
            "source": "refund_policy.pdf",
            "page": 3,
            "section": "Processing",
        },
    }

    langchain_like_object = LangChainLikeDocument(
        page_content="Digital gift cards and final sale items are non-refundable.",
        metadata={
            "source": "refund_policy.pdf",
            "page": 4,
            "section": "Non-refundable items",
        },
    )

    langchain_tuple_with_score = (
        LangChainLikeDocument(
            page_content="Physical products can only be returned within 14 days.",
            metadata={
                "source": "refund_policy_legacy.pdf",
                "page": 2,
                "version": "legacy",
            },
        ),
        0.78,
    )

    haystack_like_dict = {
        "content": "Standard shipping usually takes 5 to 7 business days.",
        "meta": {
            "source": "shipping_policy.pdf",
            "page": 1,
            "doc_type": "policy",
        },
        "score": 0.88,
        "id": "shipping-policy::chunk-1",
    }

    haystack_like_object = HaystackLikeDocument(
        content="Customers should contact support if a package is delayed by more than 10 business days.",
        meta={
            "source": "shipping_policy.pdf",
            "page": 2,
        },
        score=0.81,
        id="shipping-policy::chunk-2",
    )

    llamaindex_like_dict = {
        "node": {
            "text": "Warranty coverage lasts for one year from the purchase date.",
            "metadata": {
                "file_name": "warranty_policy.pdf",
                "page_label": "1",
            },
            "node_id": "warranty-node-1",
        },
        "score": 0.84,
    }

    llamaindex_like_object = LlamaIndexLikeNodeWithScore(
        node=LlamaIndexLikeNode(
            text="The warranty covers manufacturing defects but not accidental damage.",
            metadata={
                "file_name": "warranty_policy.pdf",
                "page_label": "2",
            },
            node_id="warranty-node-2",
        ),
        score=0.79,
    )

    custom_enterprise_dict = {
        "body": "Subscription cancellation takes effect at the end of the current billing cycle.",
        "doc_id": "subscription-policy-v3",
        "url": "https://internal.example.com/policies/subscription",
        "similarity": 0.76,
        "metadata": {
            "department": "billing",
            "updated_at": "2026-06-01",
            "version": "current",
        },
    }

    missing_source_dict = {
        "text": "Customers must include the original packaging for damaged-item returns.",
        "score": 0.67,
    }

    bare_string = "Customers may be asked to verify their email address before refund requests are processed."

    raw_chunks = [
        standard_dict,
        langchain_like_dict,
        langchain_like_object,
        langchain_tuple_with_score,
        haystack_like_dict,
        haystack_like_object,
        llamaindex_like_dict,
        llamaindex_like_object,
        custom_enterprise_dict,
        missing_source_dict,
        bare_string,
    ]

    normalized = normalize_chunks(raw_chunks)

    print_case("Normalized mixed RAG retrieval outputs", normalized)

        # -------------------------------------------------------------------------
    # Explicit custom mapping
    # -------------------------------------------------------------------------
    #
    # Most common RAG outputs can be normalized automatically because they use
    # familiar fields such as:
    #
    #   text / page_content / content
    #   metadata / meta
    #   source / file_name / doc_id
    #   score / similarity
    #
    # But some real enterprise RAG systems use custom field names. For example,
    # this object uses:
    #
    #   passage      -> the retrieved text
    #   document.path -> the source location
    #   rank_score   -> the retrieval score
    #   extra        -> metadata
    #
    # SledTrace cannot always guess these custom fields safely, so normalize_chunk()
    # lets users provide explicit extractors.
    #
    # Extractors can be:
    #
    #   1. dotted path strings:
    #        text="passage"
    #        source="document.path"
    #        score="rank_score"
    #
    #   2. callables:
    #        source=lambda item: item["document"]["path"]
    #
    # Dotted paths are simpler. Callables are useful when the mapping needs
    # custom logic or combines multiple fields.
    explicit_mapping_raw = {
        "passage": "A damaged item must be reported within 7 days of delivery.",
        "document": {
            "title": "Damaged Items Policy",
            "path": "s3://company-kb/policies/damaged_items.pdf",
        },
        "rank_score": "0.72",
        "extra": {
            "page": 5,
            "owner": "support",
        },
    }

    explicit_mapping_result = normalize_chunk(
        explicit_mapping_raw,
        rank=1,

        # Dotted path extractor:
        # Read retrieved text from explicit_mapping_raw["passage"].
        text="passage",

        # Dotted path extractor:
        # Read source from explicit_mapping_raw["document"]["path"].
        source="document.path",

        # Dotted path extractor:
        # Read score from explicit_mapping_raw["rank_score"].
        # String scores such as "0.72" are converted to float.
        score="rank_score",

        # Explicit score mappings remain higher-is-better by default. Declare
        # these fields when a custom metric has different or unknown semantics.
        score_type="rerank",
        score_direction="higher_is_better",

        # Callable extractor:
        # Build metadata by combining fields from "extra" and "document".
        metadata=lambda item: {
            **item["extra"],
            "title": item["document"]["title"],
        },
    )

    print_case("Explicit custom mapping", explicit_mapping_result)

    print("\nChunk normalization demo completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


