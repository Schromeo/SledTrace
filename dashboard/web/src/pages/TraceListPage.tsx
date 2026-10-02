import { useEffect, useState } from "react";
import { fetchTraces, importMamrFile } from "../api/client";
import TraceCard from "../components/TraceCard";
import type { TraceListItem } from "../types";

type Props = {
  selectedTraceId: string | null;
  onSelectTrace: (traceId: string) => void;
};

export default function TraceListPage({
  selectedTraceId,
  onSelectTrace,
}: Props) {
  const [traces, setTraces] = useState<TraceListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importMessage, setImportMessage] = useState<string | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  async function importFile(file: File) {
    setImporting(true);
    setImportMessage(null);
    setImportError(null);
    try {
      const result = await importMamrFile(file);
      setImportMessage(result.status === "unchanged"
        ? "Already imported. Existing evidence kept; no duplicate calls."
        : "MeetingRoom evidence imported. Select the trace to inspect its source receipts.");
      await loadTraces();
      onSelectTrace(result.trace_id);
    } catch (err) {
      setImportError(err instanceof Error ? err.message : "MeetingRoom import failed.");
    } finally {
      setImporting(false);
    }
  }

  async function loadTraces() {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchTraces();
      setTraces(data.traces);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load traces");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTraces();
  }, []);

  return (
    <div className="trace-list-page">
      <div className="panel-header">
        <div>
          <h2>Traces</h2>
          <p>{traces.length} local traces</p>
        </div>

        <button className="secondary-button" onClick={() => void loadTraces()}>
          Refresh
        </button>
      </div>

      <div className="meeting-import">
        <label htmlFor="mamr-file">Import MeetingRoom diagnostic JSON</label>
        <p>One ordinary meeting · diagnostic-v1 · up to 1 MiB. Text and model names are omitted by the source export.</p>
        <input id="mamr-file" type="file" accept=".json,application/json" disabled={importing}
          onChange={(event) => {
            const file = event.currentTarget.files?.[0];
            event.currentTarget.value = "";
            if (file) void importFile(file);
          }} />
        <div role="status" aria-live="polite">{importing ? "Importing…" : importMessage}</div>
        {importError && <div className="error-box compact" role="alert">{importError}</div>}
      </div>

      {loading && <div className="muted">Loading traces...</div>}

      {error && (
        <div className="error-box">
          <strong>Failed to load traces</strong>
          <p>{error}</p>
          <p>Make sure the Go collector is running on port 4319.</p>
        </div>
      )}

      {!loading && !error && traces.length === 0 && (
        <div className="empty-card">
          <h3>No traces yet</h3>
          <p>Instrument your Python application with the installed SDK:</p>
          <pre>python -m pip install sledtrace</pre>
          <p>Or install this checkout's matching SDK and send a deterministic trace:</p>
          <pre>{`python -m pip install -e sdk/python
cd sdk/python
python -m examples.independent_app success`}</pre>
          <p className="muted">
            The example is repo-local; the installed SDK works from any directory.
          </p>
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
