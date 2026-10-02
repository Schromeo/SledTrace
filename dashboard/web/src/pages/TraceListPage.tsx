import { useEffect, useState } from "react";
import { fetchTraces } from "../api/client";
import TraceCard from "../components/TraceCard";
import type { TraceListItem } from "../types";

const REFRESH_INTERVAL_MS = 4000;

type Props = {
  selectedTraceId: string | null;
  onSelectTrace: (traceId: string) => void;
  onLoaded?: (result: { ok: boolean; count: number }) => void;
};

export default function TraceListPage({
  selectedTraceId,
  onSelectTrace,
  onLoaded,
}: Props) {
  const [traces, setTraces] = useState<TraceListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadTraces({ quiet = false } = {}) {
    try {
      if (!quiet) {
        setLoading(true);
      }

      const data = await fetchTraces();
      setTraces(data.traces);
      setError(null);
      onLoaded?.({ ok: true, count: data.traces.length });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load traces");
      onLoaded?.({ ok: false, count: 0 });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTraces();

    // Pick up new traces automatically while the tab is visible.
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        void loadTraces({ quiet: true });
      }
    }, REFRESH_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="trace-list-page">
      <div className="panel-header">
        <div>
          <h2>Traces</h2>
          <p>
            {traces.length} local {traces.length === 1 ? "trace" : "traces"} ·
            updates automatically
          </p>
        </div>

        <button className="secondary-button" onClick={() => void loadTraces()}>
          Refresh
        </button>
      </div>

      {loading && <div className="muted">Loading traces...</div>}

      {error && (
        <div className="error-box">
          <strong>Failed to load traces</strong>
          <p>{error}</p>
          <p>Make sure <code>sledtrace serve</code> is still running.</p>
        </div>
      )}

      {!loading && !error && traces.length === 0 && (
        <div className="empty-card compact">
          <strong>No traces yet.</strong> New traces appear here automatically.
        </div>
      )}

      <div className="trace-list">
        {traces.map((trace) => (
          <TraceCard
            key={trace.trace_id}
            trace={trace}
            selected={trace.trace_id === selectedTraceId}
            onClick={() => onSelectTrace(trace.trace_id)}
          />
        ))}
      </div>
    </div>
  );
}
