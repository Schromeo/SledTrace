import { useState } from "react";
import { firstTraceSnippet } from "../utils/onboarding";

const QUICKSTART_URL =
  "https://github.com/Schromeo/SledTrace/blob/main/docs/QUICKSTART.md";

export default function FirstTraceGuide({ collectorUrl }: { collectorUrl: string }) {
  const snippet = firstTraceSnippet(collectorUrl);
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(snippet);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="first-trace-guide">
      <div className="eyebrow">Getting started</div>
      <h2>Send your first trace</h2>
      <p>
        SledTrace is running and waiting for traces at <code>{collectorUrl}</code>.
        Save this as <code>first_trace.py</code> and run it with Python in an
        environment where <code>sledtrace</code> is installed. It will show up
        here within a few seconds.
      </p>

      <div className="snippet">
        <button type="button" className="secondary-button snippet-copy" onClick={() => void copy()}>
          {copied ? "Copied" : "Copy"}
        </button>
        <pre>{snippet}</pre>
      </div>

      <p className="muted">
        This example retrieves two policies that disagree, and the answer uses a
        number neither of them contains, so SledTrace flags both problems. To
        trace your own app, follow the{" "}
        <a href={QUICKSTART_URL} target="_blank" rel="noreferrer">
          5-minute quickstart
        </a>
        .
      </p>
    </div>
  );
}
