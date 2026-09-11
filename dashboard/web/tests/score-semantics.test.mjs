import assert from "node:assert/strict";
import test from "node:test";

import {
  describeChunkScoreDirection,
  formatChunkScore,
} from "../src/utils/scoreSemantics.ts";

test("formats similarity as higher-is-better", () => {
  const chunk = {
    score: 0.1,
    score_type: "similarity",
    score_direction: "higher_is_better",
  };

  assert.equal(formatChunkScore(chunk), "Similarity 0.10 ↑");
  assert.equal(describeChunkScoreDirection(chunk), "Higher is better");
});

test("formats distance as lower-is-better", () => {
  const chunk = {
    score: 0.1,
    score_type: "distance",
    score_direction: "lower_is_better",
  };

  assert.equal(formatChunkScore(chunk), "Distance 0.10 ↓");
  assert.equal(describeChunkScoreDirection(chunk), "Lower is better");
});

test("marks an ambiguous tuple score as unknown", () => {
  const chunk = {
    score: 0.1,
    score_type: "unknown",
    score_direction: "unknown",
  };

  assert.equal(formatChunkScore(chunk), "Score 0.10 ?");
  assert.equal(
    describeChunkScoreDirection(chunk),
    "Score direction is unknown",
  );
});

test("preserves the legacy score badge when annotations are absent", () => {
  assert.equal(formatChunkScore({ score: 0.75 }), "Score 0.75");
  assert.equal(describeChunkScoreDirection({ score: 0.75 }), null);
});

test("does not display missing or non-finite scores", () => {
  assert.equal(formatChunkScore({}), null);
  assert.equal(formatChunkScore({ score: Number.NaN }), null);
});
