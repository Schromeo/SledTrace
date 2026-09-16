import type { Chunk } from "../types";

const SCORE_TYPE_LABELS: Record<string, string> = {
  distance: "Distance",
  relevance: "Relevance",
  rerank: "Rerank score",
  score: "Score",
  similarity: "Similarity",
  unknown: "Score",
};

const SCORE_DIRECTION_MARKERS: Record<string, string> = {
  higher_is_better: "↑",
  lower_is_better: "↓",
  unknown: "?",
};

export function formatChunkScore(chunk: Chunk): string | null {
  if (typeof chunk.score !== "number" || !Number.isFinite(chunk.score)) {
    return null;
  }

  const scoreType = normalizeAnnotation(chunk.score_type);
  const direction = normalizeAnnotation(chunk.score_direction);
  const label = scoreType
    ? SCORE_TYPE_LABELS[scoreType] ?? humanizeScoreType(scoreType)
    : "Score";
  const marker = direction ? SCORE_DIRECTION_MARKERS[direction] ?? "?" : "";

  return [label, chunk.score.toFixed(2), marker].filter(Boolean).join(" ");
}

export function describeChunkScoreDirection(chunk: Chunk): string | null {
  const direction = normalizeAnnotation(chunk.score_direction);

  switch (direction) {
    case "higher_is_better":
      return "Higher is better";
    case "lower_is_better":
      return "Lower is better";
    case "unknown":
      return "Score direction is unknown";
    default:
      return direction ? "Score direction is not recognized" : null;
  }
}

function normalizeAnnotation(value: string | undefined): string {
  return typeof value === "string" ? value.trim().toLowerCase() : "";
}

function humanizeScoreType(value: string): string {
  const words = value.replace(/[_-]+/g, " ").trim();
  return words ? `${words[0].toUpperCase()}${words.slice(1)}` : "Score";
}
