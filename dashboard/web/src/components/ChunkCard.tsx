import type { Chunk } from "../types";
import {
  describeChunkScoreDirection,
  formatChunkScore,
} from "../utils/scoreSemantics";
import JsonViewer from "./JsonViewer";

type Props = {
  chunk: Chunk;
};

export default function ChunkCard({ chunk }: Props) {
  const formattedScore = formatChunkScore(chunk);
  const scoreDirection = describeChunkScoreDirection(chunk);

  return (
    <article className="chunk-card">
      <div className="chunk-card-top">
        <strong>Rank #{chunk.rank ?? "?"}</strong>

        {formattedScore && (
          <span className="score-pill" title={scoreDirection ?? undefined}>
            {formattedScore}
          </span>
        )}
      </div>

      <p className="chunk-text">{chunk.text || "No chunk text recorded."}</p>

      <div className="chunk-meta">
        {chunk.source && <span>Source: {chunk.source}</span>}
        {chunk.document_id && <span>Document: {chunk.document_id}</span>}
      </div>

      {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
        <details className="metadata-details">
          <summary>Metadata</summary>
          <JsonViewer value={chunk.metadata} />
        </details>
      )}
    </article>
  );
}
