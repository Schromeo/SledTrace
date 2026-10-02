// The first-trace snippet shown on an empty dashboard. It mirrors the README
// quickstart and adds the collector URL only when it differs from the SDK
// default, so the copied code works as-is.

const SDK_DEFAULT_URLS = new Set([
  "http://localhost:4319",
  "http://127.0.0.1:4319",
]);

export function firstTraceSnippet(collectorUrl: string): string {
  const url = collectorUrl.replace(/\/+$/, "");
  const flush = SDK_DEFAULT_URLS.has(url)
    ? "print(t.flush())"
    : `print(t.flush(collector_url="${url}"))`;

  return `from sledtrace import trace

question = "How many days do customers have to return items after delivery?"

with trace(name="refund-question", query=question) as t:
    t.retrieval(
        query=question,
        chunks=[
            {"id": "policy-2024", "text": "Customers can return items within 30 days of delivery.",
             "score": 0.82, "metadata": {"source": "refund_policy.md"}},
            {"id": "policy-2021", "text": "Customers can return items within 14 days of delivery.",
             "score": 0.79, "metadata": {"source": "legacy_refund_policy.md"}},
        ],
    )
    t.llm(model="demo-model", prompt=question,
          response="Customers have 45 days to return items after delivery.")

${flush}
`;
}
