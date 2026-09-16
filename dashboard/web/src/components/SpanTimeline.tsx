import type { Span } from "../types";
import { formatDurationMs, getDurationMs } from "../utils/timing";

type Props = {
  spans: Span[];
  selectedSpanId: string | null;
  onSelectSpan: (spanId: string) => void;
};

export default function SpanTimeline({
  spans,
  selectedSpanId,
  onSelectSpan,
}: Props) {
  if (spans.length === 0) {
    return <div className="empty-card compact">No spans recorded.</div>;
  }

  return (
    <div className="span-timeline">
      {spans.map((span) => (
        <button
          key={span.span_id}
          className={
            span.span_id === selectedSpanId
              ? "span-timeline-item selected"
              : "span-timeline-item"
          }
          onClick={() => onSelectSpan(span.span_id)}
        >
          <div className="span-type">{span.type}</div>
          <div className="span-name">{span.name}</div>
          <div className="span-meta">
            {formatDurationMs(getDurationMs(span))} · {span.status}
          </div>
        </button>
      ))}
    </div>
  );
}
