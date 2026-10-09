const { test } = require("node:test");
const assert = require("node:assert/strict");
const express = require("express");
const session = require("express-session");
const { createPoviRouter } = require("../povi");

async function setup(t, create) {
    const calls = [];
    const app = express();
    app.use(express.json());
    app.use(session({ secret: "test-only-session-secret", resave: false, saveUninitialized: false }));
    app.post("/test/login/:id", (req, res) => { req.session.userId = req.params.id; res.json({ ok: true }); });
    const povi = createPoviRouter({ env: { LLM_PROVIDER: "openai" }, logger: { warn() {} }, model: "test-model", client: { responses: { create: async (...args) => {
        calls.push(args);
        return create ? create(...args) : { status: "completed", output_text: "Hello from Povi." };
    } } } });
    app.use("/api/povi", povi.router);
    const server = app.listen(0, "127.0.0.1");
    await new Promise(resolve => server.once("listening", resolve));
    t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
    const base = `http://127.0.0.1:${server.address().port}`;
    async function request(route, { cookie, body, method = "GET" } = {}) {
        const response = await fetch(base + route, { method, headers: {
            ...(cookie ? { Cookie: cookie } : {}), ...(body !== undefined ? { "Content-Type": "application/json" } : {})
        }, body: body !== undefined ? JSON.stringify(body) : undefined });
        return { status: response.status, data: await response.json(), headers: response.headers };
    }
    async function login(id) {
        const result = await request(`/test/login/${id}`, { method: "POST" });
        return result.headers.get("set-cookie").split(";")[0];
    }
    return { calls, request, login };
}

test("Express authenticates, validates, prepares Responses input, isolates history and resets", async t => {
    const { calls, request, login } = await setup(t);
    const post = (cookie, message) => request("/api/povi/chat", { cookie, method: "POST", body: { message } });
    assert.equal((await post(undefined, "Hello")).status, 401);
    const alice = await login("alice");
    for (const value of ["", "   ", 12, null, {}, "x".repeat(2001)]) assert.equal((await post(alice, value)).status, 400);
    assert.equal(calls.length, 0);
    assert.equal((await post(alice, "First message")).status, 200);
    assert.equal((await post(alice, "Second message")).status, 200);
    const [payload, options] = calls[1];
    assert.equal(payload.model, "test-model");
    assert.equal(payload.store, false);
    assert.equal(payload.max_output_tokens, 600);
    assert.match(payload.instructions, /not a medical professional/);
    assert.equal(payload.tools, undefined);
    assert.equal(payload.input.length, 3);
    assert.deepEqual(Object.keys(payload.input[0]).sort(), ["content", "role"]);
    assert.ok(options.signal instanceof AbortSignal);
    const bob = await login("bob");
    await post(bob, "Separate conversation");
    assert.equal(calls[2][0].input.length, 1);
    assert.equal((await request("/api/povi/reset", { cookie: bob, method: "POST" })).status, 200);
    assert.deepEqual((await request("/api/povi/chat", { cookie: bob })).data.messages, []);
});

for (const code of ["insufficient_quota", "credit_balance_exhausted", "project_spend_limit_exceeded", "organization_spend_limit_exceeded", "organization_usage_limit_exceeded"]) {
    test(`billing/quota 429 ${code} does not tell the user to retry in a minute`, async t => {
        const { request, login } = await setup(t, () => { throw Object.assign(new Error("SECRET upstream body"), { status: 429, code }); });
        const cookie = await login("alice");
        const result = await request("/api/povi/chat", { cookie, method: "POST", body: { message: "Hello" } });
        assert.equal(result.status, 503);
        assert.equal(result.data.code, "povi_quota_unavailable");
        assert.equal(result.headers.get("retry-after"), null);
        assert.doesNotMatch(JSON.stringify(result.data), /SECRET|in a minute/);
        assert.deepEqual((await request("/api/povi/chat", { cookie })).data.messages, []);
    });
}

for (const [label, failure, expectedStatus, expectedCode] of [
    ["temporary rate limit", { status: 429, code: "rate_limit_exceeded" }, 429, "povi_rate_limited"],
    ["timeout", { name: "APIConnectionTimeoutError" }, 504, "povi_timeout"],
    ["connection failure", { name: "APIConnectionError" }, 503, "povi_unavailable"],
    ["invalid API credentials", { status: 401, code: "invalid_api_key" }, 503, "povi_configuration_error"],
    ["model rejected", { status: 404, code: "model_not_found" }, 503, "povi_configuration_error"],
    ["provider failure", { status: 500 }, 503, "povi_unavailable"]
]) {
    test(`handles ${label} without exposing upstream details or saving history`, async t => {
        const { request, login } = await setup(t, () => { throw Object.assign(new Error("SECRET provider details"), failure); });
        const cookie = await login("alice");
        const result = await request("/api/povi/chat", { cookie, method: "POST", body: { message: "Hello" } });
        assert.equal(result.status, expectedStatus);
        assert.equal(result.data.code, expectedCode);
        assert.doesNotMatch(JSON.stringify(result.data), /SECRET/);
        assert.deepEqual((await request("/api/povi/chat", { cookie })).data.messages, []);
    });
}

test("official SDK parses a quota rejection and Express returns the correct safe error", async t => {
    const OpenAI = require("openai");
    let sdkCalls = 0;
    const sdk = new OpenAI({ apiKey: "test-key-not-real", maxRetries: 0, fetch: async (url, options) => {
        sdkCalls++;
        assert.match(String(url), /\/responses$/);
        const body = JSON.parse(options.body);
        assert.equal(body.store, false);
        assert.equal(body.input[0].content, "Hello");
        return new Response(JSON.stringify({ error: { code: "credit_balance_exhausted", type: "insufficient_quota", message: "SECRET provider details" } }), {
            status: 429, headers: { "Content-Type": "application/json" }
        });
    } });
    const { request, login } = await setup(t, (...args) => sdk.responses.create(...args));
    const cookie = await login("alice");
    const result = await request("/api/povi/chat", { cookie, method: "POST", body: { message: "Hello" } });
    assert.equal(result.status, 503);
    assert.equal(result.data.code, "povi_quota_unavailable");
    assert.equal(sdkCalls, 1);
    assert.doesNotMatch(JSON.stringify(result.data), /SECRET/);
});

test("quota type fallback and provider Retry-After are handled", () => {
    const { classifyPoviError } = require("../povi-errors");
    assert.equal(classifyPoviError({ status: 429, type: "insufficient_quota" }).code, "povi_quota_unavailable");
    assert.equal(classifyPoviError({ status: 429, headers: new Headers({ "Retry-After": "120" }) }).retryAfter, 120);
});

test("history retains at most six complete exchanges", async t => {
    const { request, login } = await setup(t);
    const cookie = await login("history-limit");
    for (let i = 1; i <= 7; i++) {
        const result = await request("/api/povi/chat", { cookie, method: "POST", body: { message: `turn ${i}` } });
        assert.equal(result.status, 200);
    }
    const history = (await request("/api/povi/chat", { cookie })).data.messages;
    assert.equal(history.length, 12);
    assert.equal(history[0].content, "turn 2");
    assert.equal(history[0].role, "user");
    assert.equal(history.at(-1).role, "assistant");
});

test("pending chat rejects duplicate submission and reset without losing history", async t => {
    let finish;
    let entered;
    const started = new Promise(resolve => { entered = resolve; });
    const { request, login } = await setup(t, () => {
        entered();
        return new Promise(resolve => { finish = () => resolve({ status: "completed", output_text: "A reply" }); });
    });
    const cookie = await login("concurrent");
    const first = request("/api/povi/chat", { cookie, method: "POST", body: { message: "first" } });
    await started;
    try {
        assert.equal((await request("/api/povi/chat", { cookie, method: "POST", body: { message: "duplicate" } })).status, 409);
        assert.equal((await request("/api/povi/reset", { cookie, method: "POST" })).status, 409);
    } finally { finish(); }
    assert.equal((await first).status, 200);
    assert.equal((await request("/api/povi/chat", { cookie })).data.messages.length, 2);
});

test("local rate limiting remains enabled with mocked responses", async t => {
    const { request, login, calls } = await setup(t);
    const cookie = await login("rate-limit");
    for (let i = 0; i < 10; i++) assert.equal((await request("/api/povi/chat", { cookie })).status, 200);
    const result = await request("/api/povi/chat", { cookie, method: "POST", body: { message: "blocked" } });
    assert.equal(result.status, 429);
    assert.ok(result.headers.get("retry-after"));
    assert.equal(calls.length, 0);
});
