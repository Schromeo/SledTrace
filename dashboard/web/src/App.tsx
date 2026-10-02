import { useState } from "react";
import { API_DISPLAY_URL } from "./api/client";
import FirstTraceGuide from "./components/FirstTraceGuide";
import TraceDetailPage from "./pages/TraceDetailPage";
import TraceListPage from "./pages/TraceListPage";

type CollectorState = "connecting" | "online" | "offline";

export default function App() {
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [collector, setCollector] = useState<CollectorState>("connecting");
  const [traceCount, setTraceCount] = useState<number | null>(null);

  function toggleSidebar() {
    setSidebarOpen((open) => !open);
  }

  function handleLoaded({ ok, count }: { ok: boolean; count: number }) {
    setCollector(ok ? "online" : "offline");
    if (ok) {
      setTraceCount(count);
    }
  }

  const sidebarLabel = sidebarOpen ? "Hide trace list" : "Show trace list";
  const collectorLabel =
    collector === "online"
      ? "Connected"
      : collector === "offline"
        ? "Not reachable"
        : "Connecting";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          <button
            type="button"
            className="icon-button"
            onClick={toggleSidebar}
            title={sidebarLabel}
            aria-label={sidebarLabel}
            aria-pressed={sidebarOpen}
          >
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" strokeWidth="2" />
              <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" strokeWidth="2" />
            </svg>
          </button>
        </div>

        <div className="topbar-brand">
          <div className="eyebrow">Local RAG debugger</div>
          <h1>SledTrace</h1>
        </div>

        <div className="topbar-right">
          <span
            className={`status-pill collector-${collector}`}
            title={
              collector === "offline"
                ? "The dashboard cannot reach the collector. Is sledtrace serve still running?"
                : undefined
            }
          >
            <span className="collector-dot" aria-hidden="true" />
            {collectorLabel} · {API_DISPLAY_URL}
          </span>
        </div>
      </header>

      <main className={sidebarOpen ? "layout" : "layout sidebar-collapsed"}>
        {/* Stays mounted while hidden so the list keeps refreshing. */}
        <section className="sidebar" hidden={!sidebarOpen}>
          <TraceListPage
            selectedTraceId={selectedTraceId}
            onSelectTrace={setSelectedTraceId}
            onLoaded={handleLoaded}
          />
        </section>

        <section className="detail">
          {selectedTraceId ? (
            <TraceDetailPage traceId={selectedTraceId} />
          ) : traceCount === 0 ? (
            <FirstTraceGuide collectorUrl={API_DISPLAY_URL} />
          ) : (
            <div className="empty-state">
              <h2>Select a trace</h2>
              <p>
                Choose a trace from the list to see its warnings, retrieved
                chunks, LLM calls and token usage.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
