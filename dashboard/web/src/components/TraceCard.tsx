import type { TraceListItem } from "../types";
import { formatWarnings, healthLabel, listHealth } from "../utils/health";
import { formatDurationMs } from "../utils/timing";

type Props = {
  trace: TraceListItem;
  selected: boolean;
  onClick: () => void;
};

export default function TraceCard({ trace, selected, onClick }: Props) {
  const demoCase = getDemoCase(trace.name);
  const health = listHealth(
    trace.status,
    trace.warning_count,
    trace.high_warning_count ?? 0,
  );

  return (
    <button
      className={selected ? "trace-card selected" : "trace-card"}
      onClick={onClick}
    >
      <div className="trace-card-top">
        <span
          className={`status-dot health-${health}`}
          title={healthLabel(health, trace.warning_count)}
          aria-label={healthLabel(health, trace.warning_count)}
        />

        <div className="trace-card-title">
          <strong>{trace.name}</strong>

          {demoCase && (
            <span className="trace-case-badge">demo: {demoCase}</span>
          )}
        </div>
      </div>

      <div className="trace-query">{trace.query || "No query recorded"}</div>

      {trace.answer && <div className="trace-answer">{trace.answer}</div>}

      <div className="trace-meta">
        <span>{formatDurationMs(trace.duration_ms ?? null)}</span>
        <span className={trace.warning_count > 0 ? "trace-meta-warnings" : undefined}>
          {formatWarnings(trace.warning_count)}
        </span>
        <span>{formatDate(trace.started_at)}</span>
      </div>
    </button>
  );
}

function getDemoCase(traceName: string): string | null {
  const prefix = "real-local-rag-";

  if (!traceName.startsWith(prefix)) {
    return null;
  }

  return traceName.slice(prefix.length);
}

function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleTimeString();
}