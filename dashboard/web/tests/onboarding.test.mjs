import assert from "node:assert/strict";
import test from "node:test";

import { firstTraceSnippet } from "../src/utils/onboarding.ts";

test("the default collector needs no URL in the snippet", () => {
  for (const url of ["http://127.0.0.1:4319", "http://localhost:4319/"]) {
    const snippet = firstTraceSnippet(url);
    assert.match(snippet, /print\(t\.flush\(\)\)/);
    assert.doesNotMatch(snippet, /collector_url/);
  }
});

test("another port is written into the snippet", () => {
  const snippet = firstTraceSnippet("http://127.0.0.1:4400");
  assert.match(snippet, /t\.flush\(collector_url="http:\/\/127\.0\.0\.1:4400"\)/);
});

test("the snippet is the README example that triggers two warnings", () => {
  const snippet = firstTraceSnippet("http://127.0.0.1:4319");
  assert.match(snippet, /from sledtrace import trace/);
  assert.match(snippet, /within 30 days/);
  assert.match(snippet, /within 14 days/);
  assert.match(snippet, /45 days/);
});
