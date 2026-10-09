# Povi setup

Requires Node.js 20 or newer. Run commands from Q_portal unless stated otherwise.

```sh
npm install --prefix backend
node backend/server.js
```

Open http://localhost:3000/login.html and sign in. SQLite opens `users.db` relative
to the working directory. `npm start --prefix backend` uses backend/users.db instead
of Q_portal/users.db; keep the working directory consistent with your existing data.

## Choose a provider

Configuration is read from the ignored `backend/.env` and server environment.
Existing environment variables take precedence. Restart after configuration changes.
Provider selection is backend-only; browser messages cannot change it.

OpenAI remains the default when LLM_PROVIDER is omitted:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4.1-mini
POVI_MOCK_MODE=false
SESSION_SECRET=your-long-random-secret
PORT=3000
```

The OpenAI integration still uses the official Node SDK and Responses API. Missing
credentials return a safe 503. Never put the key in frontend code or commit .env.
Use `.env.example` when creating new configuration and replace its secret placeholder.

## Ollama: real local conversation without OpenAI token fees

Install Ollama for your OS from https://ollama.com/download. Start the Ollama app,
or run `ollama serve` in a separate terminal if it is not already running. Download
the initial model (requires internet access and local disk space):

```sh
ollama pull llama3.2:3b
```

Set these values in backend/.env, preserving the session secret and other settings:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
POVI_MOCK_MODE=false
```

An OpenAI key is not needed for this provider. If an existing key is present it is
ignored; it is never sent to Ollama. For a one-run override without editing .env:

```sh
LLM_PROVIDER=ollama POVI_MOCK_MODE=false node backend/server.js
```

The Express backend sends a non-streaming POST to the fixed local address
http://localhost:11434/api/chat with the safety system prompt and bounded history.
There is no OpenAI request or fallback in Ollama mode. Redirects are rejected.
Unknown provider values and Ollama `:cloud` model tags fail at startup.
Use locally downloaded models, not cloud-backed custom aliases.

The frontend continues calling only the authenticated Q Portal endpoint. No Ollama
URL, API credentials, generic proxy, or model tools are exposed in the frontend.
Keep Ollama bound to loopback (its default); do not expose port 11434 publicly, set
OLLAMA_HOST to 0.0.0.0, configure wildcard browser origins, or publicly tunnel it.
For strict local-only operation, Ollama also supports OLLAMA_NO_CLOUD=1; configure
that on the Ollama service itself, not just in Q Portal's .env.

If Ollama is stopped, the UI reports that local AI is unavailable. If the model is
missing, it asks the administrator to install the configured model. The shared
25-second request deadline is preserved. First-load latency or CPU-only inference
may exceed it; load the model with `ollama run llama3.2:3b` first, then exit the CLI
conversation and try Povi again. Empty or incomplete replies are not saved.

Local generation uses your hardware and has no OpenAI token charge. The 3B model
may produce less reliable advice than larger models. Existing AI limitations and
crisis instructions still apply; those instructions cannot guarantee safe answers.

API documentation: https://docs.ollama.com/api/chat
Local binding/cloud settings: https://docs.ollama.com/faq
Initial model: https://ollama.com/library/llama3.2:3b

## Development mock: deterministic replies, no inference

Mock mode is disabled by default and takes precedence over either provider:

```sh
NODE_ENV=development POVI_MOCK_MODE=true node backend/server.js
```

No key, credits, or Ollama installation is needed. Replies are explicitly labelled
“Development mock — no AI request sent”; they are test fixtures, not LLM advice.
Authentication, validation, rate limits, history, reset, and logout use normal routes.
Both POVI_MOCK_MODE=true and NODE_ENV=development are required. Enabling mock mode
in production, test, or with unset NODE_ENV fails startup. To use real Ollama, set
POVI_MOCK_MODE=false. No actual .env credentials were changed by this integration.

## Request flow, privacy, and memory

Dashboard JavaScript sends only `{ message }` with its session cookie to
POST /api/povi/chat. The backend authenticates and validates input (2000 characters),
then invokes the selected provider with povi-instructions.js and conversation messages.
No SQLite mood records, wellbeing scores, server files, or tools are supplied.
OpenAI requests use `store: false`; this is not a guarantee of zero provider retention.
With a local Ollama model, messages go only to the local Ollama service. Q Portal
never logs full chat messages, credentials, or raw provider error bodies.

History stays in the existing in-memory session store, isolated by session, with
at most six exchanges and approximately 12000 retained characters. After 30 minutes
of chat inactivity previous context is no longer returned or used; the old data is
removed on the next successful message/reset or session expiry. Sessions expire
after eight hours without requests. Login regenerates the session; logout destroys
it. Server restart loses all sessions and history, including when switching providers.
GET /api/povi/chat restores recent history; POST /api/povi/reset clears it.
Concurrent chat/reset requests in a session are rejected while a reply is pending.

All Povi routes share ten requests per minute per user in this server process and
a 25-second inference deadline. The frontend timeout is 35 seconds. SDK retries
are disabled. Failed calls do not enter history. Billing failures return 503 with
povi_quota_unavailable, while temporary OpenAI rate limits return 429 and numeric
Retry-After. Timeout errors return 504. Local failures return safe 503 errors.
Only fixed error categories, provider names, and numeric statuses are logged.
Text is rendered with textContent; Enter sends, Shift+Enter adds a line, and the
frontend prevents duplicate submission and preserves drafts when requests fail.

## Automated testing

```sh
npm test --prefix backend
```

Latest execution: **38 passed, 0 failed, 0 skipped**. No live Ollama or OpenAI
inference requests were made. Both providers use injected/mocked clients or fetch.
The real-server smoke tests use temporary SQLite databases, dummy/empty API keys,
and explicit provider configurations. The mock-server child blocks outbound fetch.

Coverage includes provider selection, default OpenAI behavior, localhost-only
Ollama requests, system prompt and history translation, absence of credentials,
no OpenAI fallback, offline/missing-model/malformed/timeout failures, and safe
billing/quota errors through the official SDK. Both providers are tested through
Express for authentication, validation, multi-turn isolation, reset, and logout.
The existing frontend, history bounds, concurrency, rate limiting, registration,
login, mood check-ins, and wellbeing regression tests also pass.

Frontend tests execute the actual frontend script in a minimal DOM adapter against
real Express HTTP. CSS/layout and native browser behavior are not visually tested.
Live Ollama inference is unverified: the Ollama CLI was not available in this shell.
After installation, use the normal authenticated dashboard to test local generation.
There are no automatic model downloads or repeated inference probes.

The existing `npm run check:povi --prefix backend` is explicitly an OpenAI live
check and may incur fees. It refuses to run in Ollama or mock mode. It was not run
for this change. A previous OpenAI diagnostic returned credit_balance_exhausted /
insufficient_quota; successful OpenAI generation still requires API credits.

## Remaining deployment limitations

The existing in-memory session store and rate limiter do not support multiple
server processes. Production needs shared stores and HTTPS configuration; secure
cookies are enabled with NODE_ENV=production. Configure trusted proxies deliberately
if terminating TLS. Povi cannot diagnose, guarantee safety, or contact emergency help.
If the browser times out, the backend may have processed the message: reload to
reconcile history before retrying. No commit, push, deployment, new SQLite schema,
or additional npm dependency was introduced for Ollama.
