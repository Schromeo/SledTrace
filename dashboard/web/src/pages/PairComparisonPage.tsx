import { useEffect, useRef, useState } from "react";
import { ApiRequestError, fetchTraceDetail } from "../api/client";
import type { TraceDetailResponse } from "../types";
import { buildUsageLedger } from "../utils/usage";
import { estimateOpenAITextCost, formatEstimatedUsd } from "../utils/pricing";
import { formatDurationMs, getTraceDurationMs } from "../utils/timing";
import { taskDisplay } from "../utils/taskDisplay";
import { buildMamrExplanation } from "../utils/mamrExplanation";
import { comparePair, isPairTraceDetail, measurePairRun, PAIR_FILE_LIMIT, parsePairEvidence } from "../utils/pairComparison";
import type { PairEvidence, PairRun, RunMeasurements } from "../utils/pairComparison";

function measurements(detail: TraceDetailResponse) {
  const ledger = buildUsageLedger(detail.spans);
  return measurePairRun(ledger, ledger.calls.map(call => estimateOpenAITextCost(call)), getTraceDurationMs(detail));
}
function count(value: number | null) { return value === null ? "Unknown" : value.toLocaleString("en-US"); }
function difference(value: number | null, suffix = "") {
  return value === null ? "Unavailable — conditions, coverage or basis unresolved"
    : `${value > 0 ? "+" : ""}${value.toLocaleString("en-US", { maximumFractionDigits: 6 })}${suffix}`;
}

export default function PairComparisonPage({ onInspect }: { onInspect: (traceId: string) => void }) {
  const [evidence, setEvidence] = useState<PairEvidence | null>(null);
  const [pair, setPair] = useState<[TraceDetailResponse, TraceDetailResponse] | null>(null);
  const [reading, setReading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const heading = useRef<HTMLHeadingElement>(null);
  const fileGeneration = useRef(0);
  useEffect(() => { heading.current?.focus(); return () => { fileGeneration.current++; }; }, []);
  useEffect(() => {
    if (!evidence) return;
    let cancelled = false;
    setLoading(true); setPair(null); setError(null);
    async function readRun(id: string, label: string) {
      let detail: TraceDetailResponse;
      try { detail = await fetchTraceDetail(id); }
      catch (err) {
        throw new Error(err instanceof ApiRequestError && err.status === 404
          ? `${label} record not found. No empty run was substituted.`
          : err instanceof SyntaxError ? `${label} response is invalid JSON.`
          : `${label} could not be read. Collector offline or request failed; usage is not zero.`);
      }
      if (!isPairTraceDetail(detail, id)) throw new Error(`${label} record is malformed or has inconsistent identity.`);
      return detail;
    }
    void Promise.all([readRun(evidence.baseline.traceId, "Baseline"), readRun(evidence.candidate.traceId, "Candidate")])
      .then(result => { if (!cancelled) setPair(result); })
      .catch(err => { if (!cancelled) setError(err instanceof Error ? err.message : "Comparison read failed."); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [evidence, retry]);

  async function readFile(file: File) {
    const generation = ++fileGeneration.current;
    setEvidence(null); setPair(null); setError(null); setLoading(false); setReading(true);
    try {
      if (file.size > PAIR_FILE_LIMIT) throw new Error("Pair evidence exceeds 16 KiB.");
      const parsed = parsePairEvidence(await file.text());
      if (generation === fileGeneration.current) setEvidence(parsed);
    } catch (err) {
      if (generation === fileGeneration.current) setError(err instanceof Error ? err.message : "Pair file could not be read.");
    } finally { if (generation === fileGeneration.current) setReading(false); }
  }
  const before = pair ? measurements(pair[0]) : null, after = pair ? measurements(pair[1]) : null;
  const comparison = evidence && before && after ? comparePair(evidence, before, after) : null;
  return <div className="pair-page">
    <div className="eyebrow">Outcome-aware comparison · local candidate</div>
    <h2 ref={heading} tabIndex={-1}>Compare two recorded runs</h2>
    <p>Read-only. Manual context is kept only on this page; leaving or refreshing discards it. No source trace is modified.</p>
    <div className="meeting-import">
      <label htmlFor="pair-file">Choose pair-evidence JSON</label>
      <p>Version 1 · up to 16 KiB · two distinct trace IDs. Declare fixed case/input/controls/criteria and changed code versions. No prompts, responses or secrets.</p>
      <input id="pair-file" type="file" accept=".json,application/json" disabled={reading}
        onChange={event => { const file = event.currentTarget.files?.[0]; event.currentTarget.value = ""; if (file) void readFile(file); }} />
      <details><summary>File format and privacy</summary>
        <p>kind: sledtrace-pair-evidence; schemaVersion: 1; provenance: user_declared; interventionId plus baseline/candidate.</p>
        <p>Each run: traceId, caseId, inputRef, controlConfigRef, criteriaVersion, appVersion, qualityStatus, qualityEvidenceRef. Unknown references use null. passed/failed require an assessment reference; not_evaluated requires null.</p>
        <p>References: 1–200 ASCII letters/digits/dot/underscore/colon/slash/hyphen, first character alphanumeric. References are not fetched or verified and can still contain sensitive identifiers.</p>
      </details>
    </div>
    <div role="status" aria-live="polite">{reading ? "Reading local declaration…" : loading ? "Reading both trace records…" : !evidence && !error ? "No pair selected. Choose a declaration file to begin." : ""}</div>
    {error && <div className="error-box" role="alert"><strong>Comparison unavailable</strong><p>{error}</p>
      {evidence && <button className="secondary-button" onClick={() => setRetry(n => n + 1)}>Retry reads</button>}
    </div>}
    {comparison && evidence && pair && before && after && <>
      <section className={`pair-verdict ${comparison.state}`} aria-label="Comparison conditions">
        <h3>{comparison.state === "declared_match" ? "Declared conditions match — not independently verified"
          : comparison.state === "not_comparable" ? "Not comparable" : "Insufficient comparison evidence"}</h3>
        <p>Intervention: <span className="mono">{evidence.interventionId}</span> · provenance: user_declared</p>
        {[...comparison.mismatch, ...comparison.gaps].length > 0 && <ul>{[...comparison.mismatch, ...comparison.gaps].map(reason => <li key={reason}>{reason}</li>)}</ul>}
        <p><strong>{comparison.quality}</strong></p>
        <p>Matching references are human declarations, not verified configurations. Two runs are a case description, not statistical proof or an automatic keep/revert recommendation.</p>
      </section>
      <div className="pair-runs">
        <RunColumn label="Baseline" declaration={evidence.baseline} detail={pair[0]} measured={before} onInspect={onInspect} />
        <RunColumn label="Candidate" declaration={evidence.candidate} detail={pair[1]} measured={after} onInspect={onInspect} />
      </div>
      <section className="pair-verdict" aria-label="Recorded metric differences">
        <h3>Candidate minus baseline · absolute recorded differences</h3>
        <dl className="evidence-grid">
          <div><dt>Observed LLM calls</dt><dd>{difference(comparison.callsDelta)}</dd></div>
          <div><dt>Compatible recorded tokens</dt><dd>{difference(comparison.tokensDelta)}</dd></div>
          <div><dt>Estimated covered text cost</dt><dd>{difference(comparison.usdDelta, " USD")}</dd></div>
          <div><dt>Measured trace duration</dt><dd>{difference(comparison.durationDelta, " ms")}</dd></div>
        </dl>
        <p>No percentages or whole-workflow savings. Failed, cancelled and unresolved recorded LLM attempts are included. Missing attempts cannot be counted; coverage is not capture completeness.</p>
        <p>Cost uses the existing Standard-text USD snapshot (2026-09-24), excludes other charges and is not provider billing. Unknown is not free.</p>
      </section>
    </>}
  </div>;
}

function RunColumn({ label, declaration, detail, measured, onInspect }: {
  label: string; declaration: PairRun; detail: TraceDetailResponse; measured: RunMeasurements; onInspect: (traceId: string) => void;
}) {
  const source = buildMamrExplanation(detail.trace.metadata, detail.spans);
  const task = taskDisplay(detail.trace.output);
  return <section className="pair-run" aria-label={`${label} run`}>
    <h3>{label} · {detail.trace.name}</h3>
    <p className="mono">{detail.trace.trace_id}</p>
    <button className="secondary-button" onClick={() => onInspect(detail.trace.trace_id)}>Inspect {label.toLowerCase()} trace / receipts</button>
    <h4>Captured source facts</h4>
    <p>Trace status: {detail.trace.status} (not a quality verdict)</p>
    {source ? <><p>{source.title}</p><dl className="evidence-grid">{source.context.map(item => <div key={item.label}><dt>{item.label}</dt><dd>{item.value}</dd></div>)}</dl>
      <ul>{source.attempts.map(attempt => <li key={attempt.attemptId}>{attempt.attemptId}: {attempt.title}</li>)}</ul></>
      : <><p>No source-backed MAMR gate explanation for this record.</p><p>Caller task acceptance: {task.accepted === null ? "Not recorded" : String(task.accepted)} — not a versioned quality assessment.</p>
        {task.text && <details><summary>Recorded {task.label.toLowerCase()}</summary><p>{task.text}</p></details>}</>}
    <details><summary>Recorded step statuses — not a causal diagnosis</summary>
      {detail.spans.length ? <ul>{detail.spans.map(span => <li key={span.span_id}>{span.type} · {span.name}: {span.status}</li>)}</ul>
        : <p>No recorded steps. Missing capture is not a free or successful run.</p>}
    </details>
    <h4>Manual declaration — not source verified</h4>
    <dl className="evidence-grid">{(["caseId", "inputRef", "controlConfigRef", "criteriaVersion", "appVersion", "qualityStatus", "qualityEvidenceRef"] as const).map(key =>
      <div key={key}><dt>{key}</dt><dd>{declaration[key] ?? "Unknown"}</dd></div>)}</dl>
    <h4>Recorded measurements</h4>
    <dl className="evidence-grid">
      <div><dt>Observed LLM calls (all statuses)</dt><dd>{measured.observedCalls}</dd></div>
      <div><dt>Known token subtotal</dt><dd>{count(measured.knownTokens)}</dd></div>
      <div><dt>Token coverage / conflicts</dt><dd>{measured.coveredCalls}/{measured.observedCalls} · {measured.conflictCalls} conflicts</dd></div>
      <div><dt>Token comparison basis</dt><dd>{measured.tokenBasis ?? "Unknown, partial or mixed"}</dd></div>
      <div><dt>Known estimated cost subtotal</dt><dd>{measured.knownUsd === null ? "Unknown" : formatEstimatedUsd(measured.knownUsd)}</dd></div>
      <div><dt>Cost coverage / basis</dt><dd>{measured.costCoveredCalls}/{measured.observedCalls} · {measured.costBasis ?? "Unknown or partial"}</dd></div>
      <div><dt>Measured trace duration</dt><dd>{formatDurationMs(measured.durationMs)}</dd></div>
    </dl>
    <p>Coverage describes observed calls only. Failed attempts and capture gaps are not successful/free calls; source quality is not replaced by manual assessment.</p>
  </section>;
}
