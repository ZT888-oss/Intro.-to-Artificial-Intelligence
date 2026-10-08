# Povi setup

Requires Node.js 20 or newer. From Q_portal:

```sh
npm install --prefix backend
node backend/server.js
```

Open http://localhost:3000/login.html and sign in. Keep the working directory
consistent with existing usage: SQLite still opens `users.db` relative to it.
`npm start --prefix backend` instead uses backend/users.db.

The ignored `backend/.env` has already been created without an API key. Set:

```dotenv
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4.1-mini
SESSION_SECRET=your-long-random-secret
PORT=3000
```

If recreating configuration, copy backend/.env.example to backend/.env and replace
the session-secret placeholder. Never put credentials in frontend files or commit .env.
Existing environment variables override .env. Model availability depends on the account.
Without an API key, the rest of the app works and chat returns a safe 503 message.

## Request flow and privacy

Dashboard JavaScript sends only `{ message }` with its session cookie to
POST /api/povi/chat. The backend validates authentication and input (2000 characters),
then uses the official OpenAI Node SDK's Responses API with the separate
povi-instructions.js prompt. No tools, SQLite records, or wellbeing scores are supplied.
Responses use `store: false`; this disables response storage, but is not a guarantee
of zero provider retention. Review your OpenAI account's data controls before real use.
Messages and upstream errors are not logged by the chat module.

History is in the existing in-memory session store, isolated by session. At most six
exchanges and approximately 12000 characters are retained. After 30 minutes of chat
inactivity, previous context is no longer returned or used (old session data is removed
on the next successful message/reset or session expiry). Sessions expire after eight
hours without requests. Login regenerates the session; logout destroys it. Server
restart loses all sessions and histories. GET /api/povi/chat restores recent context
when reloading; POST /api/povi/reset clears it. New conversation is disabled during
requests; the server also rejects concurrent chat/reset requests within a session.

The backend limits Povi requests to ten per minute per user in this server process,
sets a 25-second deadline, and disables SDK retries. Errors return generic JSON;
rate limits return 429, deadlines 504, and unavailable services 503. Failed calls
are not added to history. The frontend renders text with textContent, supports Enter
and Shift+Enter, and disables submission while a request is pending.

## Verification deferred

No tests or server startup verification have been run, per the requested stopping
point. After authorization, run mocked endpoint tests plus login, registration,
mood, and wellbeing regressions using a temporary database. Verify invalid input,
401, upstream errors/429/timeouts, user isolation, context limits, concurrent requests,
reset, and logout. Do not run repeated paid calls. This repository does not yet have
a working automated test command; backend's original test placeholder remains.

This is a local development integration. The existing in-memory session store and
rate limiter do not support multiple server processes. Production needs a shared
session/limiter store and HTTPS configuration (secure cookies are enabled with
NODE_ENV=production; configure trusted proxies deliberately if terminating TLS).
Povi provides general AI support and cannot diagnose, guarantee safety, or contact
emergency help. On frontend network timeout the server may have processed a message;
reload to reconcile session history before retrying.

Installed openai, dotenv, express-rate-limit, and backend-local express-session.
The install audit identified two existing transitive issues; compatible proxy-addr
and qs updates were applied. npm then reported zero known vulnerabilities.
Application tests and startup checks remain deferred.
