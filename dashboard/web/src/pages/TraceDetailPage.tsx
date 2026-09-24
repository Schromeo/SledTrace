import { useEffect, useMemo, useState } from "react";
import { fetchTraceDetail } from "../api/client";
import ChunkCard from "../components/ChunkCard";
import JsonViewer from "../components/JsonViewer";
import SpanTimeline from "../components/SpanTimeline";
import {
  formatDurationMs,
  getDurationMs,
  getTraceDurationMs,
} from "../utils/timing";
import {
  buildUsageLedger,
  formatCallTotal,
  formatTokenField,
} from "../utils/usage";
import { stepError, taskDisplay } from "../utils/taskDisplay";
import {
  hasEnhancedWarning,
  normalizeWarning,
  NO_WARNINGS_MESSAGE,
  WARNING_GUIDANCE,
} from "../utils/warnings";
import type {
  Chunk,
  EvidenceItem,
  Span,
  TraceDetailResponse,
  Warning,
} from "../types";
import type { CallTotal, LlmUsageCall, TokenField, UsageLedger } from "../utils/usage";

type Props = {
  traceId: string;
};

function formatDuration(span: Span): string {
  return formatDurationMs(getDurationMs(span));
}

function formatTraceDuration(detail: TraceDetailResponse): string {
  return formatDurationMs(getTraceDurationMs(detail));
}

export default function TraceDetailPage({ traceId }: Props) {
  const [detail, setDetail] = useState<TraceDetailResponse | null>(null);
  const [selectedSpanId, setSelectedSpanId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadDetail() {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchTraceDetail(traceId);

      const normalizedData = {
        ...data,
        spans: data.spans ?? [],
        warnings: (data.warnings ?? []).map(normalizeWarning),
      };

      setDetail(normalizedData);

      if (normalizedData.spans.length > 0) {
        setSelectedSpanId(normalizedData.spans[0].span_id);
      } else {
        setSelectedSpanId(null);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load trace detail",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDetail();
  }, [traceId]);

  const selectedSpan = useMemo(() => {
    if (!detail || !selectedSpanId) {
      return null;
    }

    return detail.spans.find((span) => span.span_id === selectedSpanId) ?? null;
  }, [detail, selectedSpanId]);

  const usageLedger = useMemo(
    () => buildUsageLedger(detail?.spans ?? [], getDurationMs),
    [detail],
  );

  if (loading) {
    return <div className="muted">Loading trace detail...</div>;
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>Failed to load trace detail</strong>
        <p>{error}</p>
      </div>
    );
  }

  if (!detail) {
    return <div className="muted">Trace not found.</div>;
  }

  const query = getString(detail.trace.input, "query");
  const finalResult = taskDisplay(detail.trace.output);
  const hasTool = detail.spans.some((span) => span.type === "tool");
  const warningCount = detail.warnings.length;
  const warningCountClass =
    warningCount > 0 ? "summary-value-danger" : "summary-value-ok";

  return (
    <div className="trace-detail-page">
      <div className="trace-hero">
        <div>
          <div className="eyebrow">Trace detail</div>
          <h2>{detail.trace.name}</h2>
          <p className="mono small">{detail.trace.trace_id}</p>
        </div>

        <div className={`big-status ${detail.trace.status}`}>
          {detail.trace.status}
        </div>
      </div>

      {hasTool && (
        <div className="task-context" aria-label="Task context">
          {(["task_id", "run_id", "variant", "app_version"] as const).map(
            (key) => {
              const value = getString(detail.trace.metadata, key);
              return value ? (
                <span key={key}>
                  <strong>{key.replace("_", " ")}: </strong>{value}
                </span>
              ) : null;
            },
          )}
        </div>
      )}

      <div className="summary-grid">
        <div className="summary-card">
          <div className="summary-label">Query</div>
          <div className="summary-value summary-value-query">
            {query || "No query recorded"}
          </div>
        </div>

        <div className="summary-card summary-card-answer">
          <div className="summary-label">{finalResult.label}</div>
          <div className="summary-value summary-value-answer">
            <div className="inline-resizable-answer">
              {finalResult.text || "No result recorded"}
            </div>
            {finalResult.accepted !== null ? (
              <div className="task-acceptance">
                Acceptance: {finalResult.accepted ? "passed" : "failed"}
              </div>
            ) : null}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Duration</div>
          <div className="summary-value summary-value-duration">
            {formatTraceDuration(detail)}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Warnings</div>
          <div className={`summary-value ${warningCountClass}`}>
            {warningCount}
          </div>
        </div>
      </div>

      <UsageLedgerPanel
        ledger={usageLedger}
        selectedSpanId={selectedSpanId}
        onSelectSpan={setSelectedSpanId}
      />

      <div className="detail-grid">
        <div className="timeline-panel">
          <h3>{hasTool ? "Execution steps" : "Pipeline timeline"}</h3>
          <SpanTimeline
            spans={detail.spans}
            selectedSpanId={selectedSpanId}
            onSelectSpan={setSelectedSpanId}
          />

          <h3>Warnings</h3>
          <p className="warning-help">{WARNING_GUIDANCE}</p>
          {detail.warnings.length === 0 ? (
            <div className="empty-card compact">
              {NO_WARNINGS_MESSAGE}
            </div>
          ) : (
            <div className="warning-list">
              {detail.warnings.map((warning) => (
                <div key={warning.warning_id} className="warning-card">
                  <div className="warning-card-header">
                    <strong>{getWarningTitle(warning)}</strong>
                    <span className="warning-severity">
                      {warning.severity}
                    </span>
                  </div>

                  {hasEnhancedWarning(warning) ? (
                    <>
                      <div className="warning-meta-row">
                        <span className="warning-meta-badge warning-meta-badge-secondary">
                          Heuristic
                        </span>
                        {warning.category ? (
                          <span className="warning-meta-badge">
                            {warning.category}
                          </span>
                        ) : null}

                      </div>

                      <p>{warning.explanation || warning.message}</p>

                      {renderComparedValuesBlock(warning)}

                      {renderEvidencePreview(warning.evidence ?? [])}

                      <div className="warning-recommendation">
                        <div className="warning-section-label">
                          Recommended action
                        </div>
                        <div className="warning-help">
                          {warning.recommended_action ||
                            getWarningHelpText(warning.type)}
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <p>{warning.message}</p>

                      <div className="warning-help">
                        {getWarningHelpText(warning.type)}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="span-detail-panel">
          {selectedSpan ? (
            <SelectedSpanView span={selectedSpan} />
          ) : (
            <div className="empty-card">Select a span to inspect details.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function UsageLedgerPanel({
  ledger,
  selectedSpanId,
  onSelectSpan,
}: {
  ledger: UsageLedger;
  selectedSpanId: string | null;
  onSelectSpan: (spanId: string) => void;
}) {
  const subtotal =
    ledger.coveredCalls > 0
      ? ledger.knownSubtotal.toLocaleString("en-US")
      : "Unknown";

  return (
    <section className="usage-panel" aria-labelledby="usage-ledger-heading">
      <div className="usage-panel-header">
        <div>
          <div className="eyebrow">Observed execution usage</div>
          <h3 id="usage-ledger-heading">LLM usage ledger</h3>
          <p className="usage-help">
            Known subtotal covers only observed calls with a trustworthy total.
            Usage source is not provider-verified, and uninstrumented calls may
            exist outside this trace.
          </p>
        </div>

        <div className="usage-summary" aria-label="LLM usage summary">
          <div>
            <span>Known subtotal</span>
            <strong>{subtotal}</strong>
            <small>tokens</small>
          </div>
          <div>
            <span>Coverage</span>
            <strong>
              {ledger.coveredCalls}/{ledger.observedCalls}
            </strong>
            <small>observed calls</small>
          </div>
          {ledger.conflictCalls > 0 ? (
            <div className="usage-summary-alert">
              <span>Conflicts</span>
              <strong>{ledger.conflictCalls}</strong>
              <small>excluded</small>
            </div>
          ) : null}
        </div>
      </div>

      {ledger.calls.length === 0 ? (
        <div className="empty-card compact">
          No LLM calls were recorded in this trace. Usage is unknown, not zero.
        </div>
      ) : (
        <div className="usage-call-list">
          {ledger.calls.map((call) => (
            <UsageCallRow
              key={call.spanId}
              call={call}
              selected={call.spanId === selectedSpanId}
              onSelect={() => onSelectSpan(call.spanId)}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function UsageCallRow({
  call,
  selected,
  onSelect,
}: {
  call: LlmUsageCall;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={selected ? "usage-call selected" : "usage-call"}
      aria-pressed={selected}
      onClick={onSelect}
    >
      <div className="usage-call-identity">
        <span className="usage-call-order">Call {call.order}</span>
        <strong>{call.name}</strong>
        <span>{call.model}</span>
      </div>

      <UsageMetric label="Input" field={call.inputTokens} />
      <UsageMetric label="Output" field={call.outputTokens} />
      <UsageTotalMetric total={call.total} />

      <div className="usage-metric">
        <span>Duration</span>
        <strong className={call.durationMs === null ? "usage-unknown" : ""}>
          {formatDurationMs(call.durationMs)}
        </strong>
        <small>call timing</small>
      </div>

      <div className="usage-metric">
        <span>Usage source</span>
        <strong className="usage-unknown">Unknown</strong>
        <small>not provider-verified</small>
      </div>
    </button>
  );
}

function UsageMetric({ label, field }: { label: string; field: TokenField }) {
  return (
    <div className="usage-metric">
      <span>{label}</span>
      <strong className={getTokenStateClass(field.kind)}>
        {formatTokenField(field)}
      </strong>
      <small>tokens</small>
    </div>
  );
}

function UsageTotalMetric({ total }: { total: CallTotal }) {
  const detail =
    total.kind === "known"
      ? total.basis === "recorded_total"
        ? "recorded total"
        : "input + output"
      : total.kind === "conflict"
        ? "excluded from subtotal"
        : "tokens";

  return (
    <div className="usage-metric usage-metric-total">
      <span>Total</span>
      <strong className={getTokenStateClass(total.kind)}>
        {formatCallTotal(total)}
      </strong>
      <small>{detail}</small>
    </div>
  );
}

function getTokenStateClass(kind: TokenField["kind"] | CallTotal["kind"]): string {
  if (kind === "known") {
    return "";
  }

  return kind === "conflict" || kind === "invalid"
    ? "usage-invalid"
    : "usage-unknown";
}

function SelectedSpanView({ span }: { span: Span }) {
  const chunks = getChunks(span);

  return (
    <div>
      <div className="span-detail-header">
        <div>
          <div className="eyebrow">{span.type} span</div>
          <h3>{span.name}</h3>
        </div>

        <div className="span-header-meta">
          <div className={`big-status ${span.status}`}>{span.status}</div>
          <div className="span-duration">{formatDuration(span)}</div>
        </div>
      </div>

      {span.type === "retrieval" && (
        <section className="section">
          <h4>Retrieved chunks</h4>

          {chunks.length === 0 ? (
            <div className="empty-card compact">No chunks recorded.</div>
          ) : (
            <div className="chunk-list">
              {chunks.map((chunk, index) => (
                <ChunkCard
                  key={chunk.id ?? `${span.span_id}-chunk-${index}`}
                  chunk={chunk}
                />
              ))}
            </div>
          )}
        </section>
      )}

      {span.type === "llm" && (
        <section className="section">
          <h4>LLM call</h4>

          <div className="llm-box">
            <div className="summary-label">Model</div>
            <div>{getString(span.input, "model") || "Unknown model"}</div>
          </div>

          <div className="llm-box">
            <div className="summary-label">Prompt</div>
            <pre>{getString(span.input, "prompt") || "No prompt recorded"}</pre>
          </div>

          <div className="llm-box">
            <div className="summary-label">Response</div>
            <pre>
              {getString(span.output, "response") || "No response recorded"}
            </pre>
          </div>
        </section>
      )}

      {span.type === "tool" && (
        <section className="section">
          <h4>Tool attempt</h4>
          <div className="llm-box">
            <div className="summary-label">Input summary</div>
            <pre>{getString(span.input, "summary") || "Not recorded"}</pre>
          </div>
          <div className="llm-box">
            <div className="summary-label">Output summary</div>
            <pre>{getString(span.output, "summary") || "Not recorded"}</pre>
          </div>
        </section>
      )}

      {stepError(span.error) && (
        <div className="error-box compact" role="status">
          Step error: {stepError(span.error)}
        </div>
      )}

      <section className="section">
        <h4>Input</h4>
        <JsonViewer value={span.input} />
      </section>

      <section className="section">
        <h4>Output</h4>
        <JsonViewer value={span.output} />
      </section>

      <section className="section">
        <h4>Metadata</h4>
        <JsonViewer value={span.metadata} />
      </section>
    </div>
  );
}

function getString(value: Record<string, unknown>, key: string): string {
  const raw = value[key];

  return typeof raw === "string" ? raw : "";
}

function getChunks(span: Span): Chunk[] {
  const raw = span.output["chunks"];

  if (!Array.isArray(raw)) {
    return [];
  }

  return raw as Chunk[];
}

function getWarningTitle(warning: Warning): string {
  return warning.title || formatWarningType(warning.type);
}

function renderComparedValuesBlock(warning: Warning) {
  const comparedValues = getComparedValues(warning);

  if (!comparedValues) {
    return null;
  }

  return (
    <div className="warning-value-diff">
      <div className="warning-section-label">Compared values</div>

      <div className="warning-value-diff-row">
        <span>Answer value</span>
        <strong>{comparedValues.answerValue}</strong>
      </div>

      <div className="warning-value-diff-row">
        <span>Retrieved value</span>
        <strong>{comparedValues.retrievedValue}</strong>
      </div>
    </div>
  );
}

function getComparedValues(
  warning: Warning,
): { answerValue: string; retrievedValue: string } | null {
  if (warning.type !== "numeric_mismatch") {
    return null;
  }

  const evidenceValue = getComparedValuesFromEvidence(warning.evidence ?? []);
  if (evidenceValue) {
    return evidenceValue;
  }

  const answerValue = getRecordString(warning.details, "answer_value");
  const retrievedValue = getRecordString(warning.details, "retrieved_value");

  if (!answerValue || !retrievedValue) {
    return null;
  }

  return {
    answerValue,
    retrievedValue,
  };
}

function getComparedValuesFromEvidence(
  evidence: EvidenceItem[],
): { answerValue: string; retrievedValue: string } | null {
  for (const item of evidence) {
    if (item.type !== "numeric_value") {
      continue;
    }

    const answerValue = getRecordString(item.attributes, "answer_value");
    const retrievedValue = getRecordString(item.attributes, "retrieved_value");

    if (answerValue && retrievedValue) {
      return {
        answerValue,
        retrievedValue,
      };
    }
  }

  return null;
}

function getRecordString(
  value: Record<string, unknown> | null | undefined,
  key: string,
): string {
  if (!value) {
    return "";
  }

  const raw = value[key];

  if (typeof raw === "string") {
    return raw;
  }

  if (typeof raw === "number") {
    return String(raw);
  }

  return "";
}

function renderEvidencePreview(evidence: EvidenceItem[]) {
  if (evidence.length === 0) {
    return null;
  }

  return (
    <div className="warning-evidence-preview">
      <div className="warning-section-label">Evidence</div>
      <ul>
        {evidence.slice(0, 2).map((item, index) => (
          <li key={item.evidence_id ?? `${item.type}-${index}`}>
            <strong>{item.label}</strong>
            {item.snippet ? `: ${item.snippet}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatWarningType(type: string): string {
  return type.split("_").join(" ");
}

function getWarningHelpText(type: string): string {
  switch (type) {
    case "no_retrieved_chunks":
      return "The retriever did not return usable evidence for the query.";

    case "low_retrieval_score":
      return "The retrieved chunks may be weakly related to the query.";

    case "duplicate_chunks":
      return "The context contains repeated evidence, which can waste context window space or over-weight one source.";

    case "conflicting_chunks":
      return "The retrieved chunks appear to contain conflicting information.";

    case "numeric_mismatch":
      return "The final answer contains a numeric value that differs from retrieved context with similar local wording.";

    case "answer_not_grounded":
      return "The answer appears to include a claim that is not supported by the retrieved context.";

    default:
      return "SledTrace detected a potential issue in this trace.";
  }
}
