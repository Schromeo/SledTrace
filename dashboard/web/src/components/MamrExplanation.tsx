import type { JsonObject, Span } from "../types";
import { buildMamrExplanation } from "../utils/mamrExplanation";

export default function MamrExplanation({ metadata, spans, onInspect }: {
  metadata: JsonObject;
  spans: Span[];
  onInspect: (spanId: string) => void;
}) {
  const explanation = buildMamrExplanation(metadata, spans);
  if (!explanation) return null;
  return (
    <section className="mamr-explanation" aria-label="Failure explanation">
      <div className="eyebrow">Source-backed explanation · D1 local candidate</div>
      <h3>{explanation.title}</h3>
      <p>Application-reported evidence, not independently verified. One card per attempt; start and terminal are not two failures.</p>
      {explanation.missingEvidence && <p className="explanation-gap">Some receipts are missing, unsupported or inconsistent. Capture gaps are not successful or free calls. Check the source capture/export before drawing a conclusion.</p>}
      {explanation.attempts.map(attempt => (
        <details className={`attempt-explanation ${attempt.layer}`} key={attempt.attemptId} open={attempt.layer !== "none"}>
          <summary>{attempt.title} · {attempt.attemptId}</summary>
          <p className="mono">{attempt.identity}</p>
          <ul>{attempt.facts.map(fact => <li key={fact}>{fact}</li>)}</ul>
          <p><strong>Next check: </strong>{attempt.nextCheck}</p>
          {attempt.spanId ? <button type="button" onClick={() => onInspect(attempt.spanId!)}>Inspect receipt · {attempt.attemptId}</button>
            : <p>Matching stored span unavailable or ambiguous. Inspect the source bundle below; no nearby span was substituted.</p>}
        </details>
      ))}
      <details className="explanation-context">
        <summary>Workflow and task context — not a causal chain</summary>
        <dl className="evidence-grid">{explanation.context.map(fact => <div key={fact.label}><dt>{fact.label}</dt><dd>{fact.value}</dd></div>)}</dl>
        <p>No explicit dependency/blocking link was exported. Workflow interruption and memo absence are separate observations, not proven consequences of a particular attempt. Root cause inside the model and answer quality are unknown.</p>
      </details>
    </section>
  );
}
