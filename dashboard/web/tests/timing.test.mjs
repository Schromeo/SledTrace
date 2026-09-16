import assert from "node:assert/strict";
import test from "node:test";

import {
  formatDurationMs,
  getDurationMs,
  getTraceDurationMs,
} from "../src/utils/timing.ts";

test("canonical null stays unmeasured instead of using timestamps", () => {
  assert.equal(
    getDurationMs({
      duration_ms: null,
      started_at: "2026-09-11T10:00:00.000Z",
      ended_at: "2026-09-11T10:00:00.500Z",
    }),
    null,
  );
  assert.equal(formatDurationMs(null), "Not measured");
});

test("measured zero remains distinct from unknown", () => {
  assert.equal(getDurationMs({ duration_ms: 0 }), 0);
  assert.equal(formatDurationMs(0), "0ms");
});

test("legacy duration metadata and timestamp-only records remain readable", () => {
  assert.equal(getDurationMs({ metadata: { latency_ms: "35" } }), 35);
  assert.equal(
    getDurationMs({
      started_at: "2026-09-11T10:00:00.000Z",
      ended_at: "2026-09-11T10:00:00.080Z",
    }),
    80,
  );
});

test("malformed canonical duration is unknown and does not fall through", () => {
  assert.equal(
    getDurationMs({
      duration_ms: -1,
      latency_ms: 25,
      started_at: "2026-09-11T10:00:00.000Z",
      ended_at: "2026-09-11T10:00:00.080Z",
    }),
    null,
  );
});

test("trace duration never becomes a partial sum of measured spans", () => {
  assert.equal(
    getTraceDurationMs({
      trace: { duration_ms: null },
      spans: [{ duration_ms: 30 }, { duration_ms: 40 }],
    }),
    null,
  );
});
