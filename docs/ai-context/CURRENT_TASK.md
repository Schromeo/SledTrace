# Current Task

Updated: 2026-09-11. Status: **S4 local network defaults implemented, validated, and locally committed; not pushed, merged, versioned, or released**.

## Current focus and authority

The user continued the bounded post-v0.7 reliability sequence. S1 timing is in
local commit `5b5d254`, S2 score semantics is in `ee0a812`, S3 trace delivery is
in `6562dc3`, and S4 is committed on `codex/s4-local-network-defaults`.

Do not redo S1-S4 or publish a release. The next bounded action requires a fresh
decision between grouping the reliability commits for integration/release and
starting the proposed Reliable First Integration work. v0.7.0 remains the
released version.

## S4 decision card

| Question | Current answer |
| --- | --- |
| User value | A normal local start does not unintentionally publish the unauthenticated Collector or Dashboard to every host interface, while intentional remote use remains possible through explicit configuration. |
| Confirmed blocker | Native Collector defaulted to `:4319`, Vite development used `0.0.0.0`, Compose published both ports on all host interfaces, and Collector CORS returned `*`. |
| Existing capability | Collector address overrides, Compose port overrides, Vite CLI overrides, a source startup helper, and Go HTTP tests already existed. |
| Smallest deliverable | Default native listeners and Compose host publishing to loopback; preserve container-internal listeners; replace wildcard CORS with exact local origins and an explicit override; document the complete remote configuration. |
| Non-goals | No authentication, TLS, firewall changes, network discovery, proxy, API redesign, SDK URL change, UI redesign, version bump, or release. |
| Validation | Default/override address tests, CORS allow/deny/preflight tests, all Go tests, Dashboard tests/build, default and remote Compose expansion, live listeners, SDK ingestion, and browser-visible Dashboard retrieval. |
| Visible evidence | A live `S4 loopback validation` trace is shown in the Dashboard at `127.0.0.1:5173`, backed by listeners on `127.0.0.1:4319` and `127.0.0.1:5173`. |

## Implemented contract

- A native Collector with no address environment variable listens on
  `127.0.0.1:4319`.
- `SLEDTRACE_COLLECTOR_ADDR` remains the preferred explicit override;
  `RAGLENS_COLLECTOR_ADDR` remains the temporary compatibility fallback.
- Vite development and preview scripts listen on `127.0.0.1:5173` by default.
  An explicit trailing Vite `--host` option supports intentional remote use.
- Compose publishes Collector and Dashboard ports through
  `SLEDTRACE_BIND_HOST`, defaulting to `127.0.0.1`. Container-internal
  Collector and Nginx listeners remain reachable inside Docker networking.
- CORS defaults to the exact origins `http://localhost:5173` and
  `http://127.0.0.1:5173`. `SLEDTRACE_ALLOWED_ORIGINS` replaces the defaults
  with a comma-separated exact list.
- Requests without `Origin` continue normally. An unconfigured browser origin
  receives the normal response but no `Access-Control-Allow-Origin` header.
- Remote access also requires the correct `VITE_SLEDTRACE_API_URL`; SDK clients
  on another machine require `SLEDTRACE_COLLECTOR_URL`. README documents the
  full boundary and warns that these services remain unauthenticated.

## Acceptance criteria

- [x] Native Collector default is loopback and explicit/legacy overrides work.
- [x] Source Dashboard development and preview defaults are loopback.
- [x] Compose host ports default to `127.0.0.1`.
- [x] Container-internal listeners remain compatible with Docker networking.
- [x] Wildcard CORS is removed; both standard local Dashboard origins work.
- [x] Explicit origins replace the default list and preflight headers are correct.
- [x] SDK/curl requests without `Origin` still work.
- [x] Intentional remote configuration is documented across binding, CORS, UI API URL, and SDK URL.
- [x] No auth/TLS/firewall, API, storage, warning, span, or UI behavior was added.

## Validation evidence

Completed on 2026-09-11:

- Focused Go tests for Collector address and API CORS packages: passed.
- `cd collector/go && go test ./... -count=1`: all packages passed.
- `cd dashboard/web && npm.cmd test`: 10 tests passed.
- `cd dashboard/web && npm.cmd run build`: passed; 38 modules transformed.
- `docker compose config`: passed without contacting the daemon; both published
  ports resolve to host IP `127.0.0.1`, Collector remains `:4319`, and the two
  local allowed origins are present.
- Remote Compose override expansion: both host IPs resolve to `0.0.0.0`, and the
  supplied allowed origin and Dashboard API URL are preserved.
- Live `netstat`: only `127.0.0.1:4319` and `127.0.0.1:5173` listened for the
  current Collector and Dashboard.
- Live HTTP: no-Origin health returned 200; both default local origins were
  allowed exactly; `https://example.invalid` received no allow-origin header
  and included `Vary: Origin`.
- Live Python SDK flush stored trace
  `trace_abc2dc4e6b494b6687a2472903863998`; the browser loaded its trace detail,
  retrieval span, LLM span, and warning through the loopback-only services.
- `git diff --check`: passed with line-ending conversion warnings only.

Docker runtime was not started because this host's Docker Desktop/WSL2 backend
is unavailable. Compose expansion validates configuration structure, not a
container runtime smoke test; that remains a separate host-capability check.

## Exit boundary

S4 is complete and committed only on the local branch. No push, PR, merge,
version bump, tag, package upload, or release exists for S1-S4. The temporary
live non-Docker services remain available so the user can inspect the S4 trace.
