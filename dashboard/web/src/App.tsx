import { useState } from "react";
import { API_BASE_URL } from "./api/client";
import TraceDetailPage from "./pages/TraceDetailPage";
import TraceListPage from "./pages/TraceListPage";

export default function App() {
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  function toggleSidebar() {
    setSidebarOpen((open) => !open);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-left">
          <button
            className="secondary-button sidebar-toggle-button"
            onClick={toggleSidebar}
            title={sidebarOpen ? "Hide trace sidebar" : "Show trace sidebar"}
          >
            {sidebarOpen ? "<< Hide traces" : ">> Show traces"}
          </button>
        </div>

        <div className="topbar-brand">
          <div className="eyebrow">Local-first AI trace debugger</div>
          <h1>SledTrace</h1>
        </div>

        <div className="topbar-right">
          <span className="status-pill">Collector: {API_BASE_URL}</span>
        </div>
      </header>

      <main className={sidebarOpen ? "layout" : "layout sidebar-collapsed"}>
        {sidebarOpen && (
          <section className="sidebar">
            <TraceListPage
              selectedTraceId={selectedTraceId}
              onSelectTrace={setSelectedTraceId}
            />
          </section>
        )}

        <section className="detail">
          {selectedTraceId ? (
            <TraceDetailPage traceId={selectedTraceId} />
          ) : (
            <div className="empty-state">
              <h2>Select a trace</h2>
              <p>
                Choose a trace from the trace panel to inspect retrieval chunks,
                LLM and tool attempts, metadata, and warnings. You can use the Show traces
                button in the top bar anytime.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
