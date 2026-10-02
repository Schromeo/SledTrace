import type { JsonObject } from "../types";
import { evidenceValue, mamrBundle, mamrRecord } from "../utils/mamr";

export function MamrEvidence({ metadata }: { metadata: JsonObject }) {
  const bundle = mamrBundle(metadata);
  if (!bundle) return null;
  const room = mamrRecord(bundle, "room");
  const workflow = mamrRecord(bundle, "workflow");
  const task = mamrRecord(bundle, "taskResult");
  const source = mamrRecord(bundle, "sourceEvidence");
  const outcome = mamrRecord(bundle, "outcomeSignals");
  const receipts = Array.isArray(source.receipts) ? source.receipts : [];
  const unresolved = Array.isArray(source.unresolvedAttemptIds) ? source.unresolvedAttemptIds : [];
  return (
    <section className="mamr-evidence" aria-label="MeetingRoom source evidence">
      <h3>MeetingRoom source evidence</h3>
      <p>Ordinary meeting diagnostic-v1 · source-reported metadata. Quality: not evaluated.</p>
      <dl className="evidence-grid">
        <Evidence label="Source room" value={evidenceValue(room.id)} />
        <Evidence label="Workflow state" value={evidenceValue(workflow.status)} />
        <Evidence label="Workflow phase" value={evidenceValue(workflow.phase)} />
        <Evidence label="Contract rejection observed" value={evidenceValue(outcome.turnEnvelopeRejectionObserved)} />
        <Evidence label="Human decision" value={evidenceValue(task.humanDecision)} />
        <Evidence label="Memo present" value={evidenceValue(task.memoPresent)} />
        <Evidence label="Source evidence" value={evidenceValue(source.state)} />
        <Evidence label="Source receipts" value={String(receipts.length)} />
        <Evidence label="Unresolved attempts" value={String(unresolved.length)} />
        <Evidence label="Source room created" value={evidenceValue(room.createdAt)} />
        <Evidence label="Source room updated" value={evidenceValue(room.updatedAt)} />
        <Evidence label="Workflow updated" value={evidenceValue(workflow.updatedAt)} />
      </dl>
      <p>Room update times are not execution duration. Model names, task text and responses were not exported. Missing terminal evidence does not prove a running call or a free call.</p>
      <details>
        <summary>Inspect allowlisted source bundle</summary>
        <pre>{JSON.stringify(bundle, null, 2)}</pre>
      </details>
    </section>
  );
}

export function MamrReceipt({ metadata }: { metadata: JsonObject }) {
  const receipt = mamrRecord(metadata, "mamr_receipt");
  if (metadata.usage_source !== "mamr_reported" || !receipt.attemptId) return null;
  return (
    <section className="mamr-evidence" aria-label="Source attempt receipt">
      <h4>Source attempt receipt</h4>
      <dl className="evidence-grid">
        {(["attemptId", "turnId", "seatId", "lifecycle", "callStatus", "providerFinish", "providerReason", "validation", "validationCode", "validationPath", "startedAt", "endedAt", "elapsedMs", "outputTokenBasis"] as const).map(key =>
          <Evidence key={key} label={key} value={evidenceValue(receipt[key])} />)}
      </dl>
      <p>Call status, provider finish and application validation are separate source facts. A returned call can have a rejected contract.</p>
    </section>
  );
}

function Evidence({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>;
}
