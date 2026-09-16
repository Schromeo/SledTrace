type TimingRecord = Record<string, unknown>;

type DurationCandidate = {
  container: TimingRecord;
  key: string;
};

function asRecord(value: unknown): TimingRecord {
  return value !== null && typeof value === "object"
    ? (value as TimingRecord)
    : {};
}

function hasOwn(container: TimingRecord, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(container, key);
}

function parseDurationMs(value: unknown): number | null {
  if (typeof value === "number") {
    return Number.isFinite(value) && value >= 0 ? value : null;
  }

  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
  }

  return null;
}

function parseTimestampMs(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value > 0 && value < 10_000_000_000 ? value * 1000 : value;
  }

  if (typeof value !== "string" || value.trim() === "") {
    return null;
  }

  const trimmed = value.trim();
  const numeric = Number(trimmed);
  if (Number.isFinite(numeric)) {
    return numeric > 0 && numeric < 10_000_000_000
      ? numeric * 1000
      : numeric;
  }

  const parsed = Date.parse(trimmed);
  return Number.isFinite(parsed) ? parsed : null;
}

function firstPresentDuration(
  candidates: DurationCandidate[],
): { found: boolean; value: number | null } {
  for (const candidate of candidates) {
    if (hasOwn(candidate.container, candidate.key)) {
      return {
        found: true,
        value: parseDurationMs(candidate.container[candidate.key]),
      };
    }
  }

  return { found: false, value: null };
}

function firstTimestamp(container: TimingRecord, keys: string[]): number | null {
  for (const key of keys) {
    if (!hasOwn(container, key)) {
      continue;
    }

    const parsed = parseTimestampMs(container[key]);
    if (parsed !== null) {
      return parsed;
    }
  }

  return null;
}

export function getDurationMs(value: unknown): number | null {
  const record = asRecord(value);
  const metadata = asRecord(record.metadata);
  const direct = firstPresentDuration([
    { container: record, key: "duration_ms" },
    { container: record, key: "durationMs" },
    { container: record, key: "duration" },
    { container: record, key: "latency_ms" },
    { container: record, key: "latencyMs" },
    { container: metadata, key: "duration_ms" },
    { container: metadata, key: "durationMs" },
    { container: metadata, key: "latency_ms" },
    { container: metadata, key: "latencyMs" },
  ]);

  // A canonical null is an explicit "not measured" value. Falling through to
  // record timestamps would turn unknown timing back into a fabricated value.
  if (direct.found) {
    return direct.value;
  }

  const startMs = firstTimestamp(record, [
    "start_time",
    "startTime",
    "started_at",
    "startedAt",
    "start",
  ]) ?? firstTimestamp(metadata, [
    "start_time",
    "startTime",
    "started_at",
    "startedAt",
    "start",
  ]);

  const endMs = firstTimestamp(record, [
    "end_time",
    "endTime",
    "ended_at",
    "endedAt",
    "end",
    "finish_time",
    "finishTime",
    "finished_at",
    "finishedAt",
  ]) ?? firstTimestamp(metadata, [
    "end_time",
    "endTime",
    "ended_at",
    "endedAt",
    "end",
    "finish_time",
    "finishTime",
    "finished_at",
    "finishedAt",
  ]);

  if (startMs === null || endMs === null) {
    return null;
  }

  const durationMs = endMs - startMs;
  return Number.isFinite(durationMs) && durationMs >= 0 ? durationMs : null;
}

export function getTraceDurationMs(detail: unknown): number | null {
  return getDurationMs(asRecord(detail).trace);
}

export function formatDurationMs(durationMs: number | null): string {
  if (durationMs === null) {
    return "Not measured";
  }

  if (durationMs < 1000) {
    return `${Math.round(durationMs)}ms`;
  }

  return `${(durationMs / 1000).toFixed(2)}s`;
}
