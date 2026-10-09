const { test } = require("node:test");
const assert = require("node:assert/strict");
const express = require("express");
const session = require("express-session");
const { createPoviProvider, OLLAMA_CHAT_URL } = require("../povi-provider");
const { createPoviRouter } = require("../povi");
const instructions = require("../povi-instructions");

const localEnv = { LLM_PROVIDER: "ollama", OPENAI_API_KEY: "not-a-real-key" };
const forbiddenClient = { responses: { create() { throw new Error("OpenAI must never be called"); } } };

test("OpenAI remains the default and missing credentials disable it", () => {
    assert.equal(createPoviProvider({ env: {} }).provider, "openai");
    assert.equal(createPoviProvider({ env: {} }).api, null);
    assert.equal(createPoviProvider({ env: { LLM_PROVIDER: "openai" }, client: forbiddenClient }).api, forbiddenClient);
});
test("invalid provider and Ollama cloud model fail closed", () => {
    assert.throws(() => createPoviProvider({ env: { LLM_PROVIDER: "typo" } }), /LLM_PROVIDER/);
    assert.throws(() => createPoviProvider({ env: { LLM_PROVIDER: "ollama", OLLAMA_MODEL: "example:cloud" } }), /local model/);
});
test("Ollama sends safety instructions and history only to localhost without API credentials", async () => {
    let calls = 0;
    const input = [{ role: "user", content: "First" }, { role: "assistant", content: "Reply" }, { role: "user", content: "Second" }];
    const signal = new AbortController().signal;
    const { api, model } = createPoviProvider({ env: localEnv, client: forbiddenClient, fetchImpl: async (url, options) => {
        calls++;
        assert.equal(url, "http://localhost:11434/api/chat");
        assert.equal(options.method, "POST");
        assert.equal(options.redirect, "error");
        assert.equal(options.signal, signal);
        assert.deepEqual(options.headers, { "Content-Type": "application/json" });
        const body = JSON.parse(options.body);
        assert.equal(body.model, "llama3.2:3b");
        assert.equal(body.stream, false);
        assert.equal(body.options.num_predict, 600);
        assert.deepEqual(body.messages, [{ role: "system", content: instructions }, ...input]);
        assert.doesNotMatch(options.body, /not-a-real-key/);
        assert.equal(body.tools, undefined);
        return new Response(JSON.stringify({ done: true, message: { role: "assistant", content: "Local reply" } }));
    } });
    const result = await api.responses.create({ model, instructions, input, max_output_tokens: 600 }, { signal });
    assert.equal(result.output_text, "Local reply");
    assert.equal(calls, 1);
});

async function setup(t, provider, respond) {
    const calls = [];
    const app = express();
    app.use(express.json());
    app.use(session({ secret: "test-only-session-secret", resave: false, saveUninitialized: false }));
    app.post("/login/:id", (req, res) => { req.session.userId = req.params.id; res.json({ success: true }); });
    const route = createPoviRouter({ env: { ...localEnv, LLM_PROVIDER: provider }, logger: { warn() {} },
        client: provider === "ollama" ? forbiddenClient : { responses: { async create(payload) {
            calls.push(payload); return { status: "completed", output_text: "OpenAI test reply" };
        } } },
        fetchImpl: async (url, options) => {
            assert.equal(url, OLLAMA_CHAT_URL);
            const body = JSON.parse(options.body); calls.push(body);
            return respond ? respond(body, options) : new Response(JSON.stringify({ done: true, message: { content: "Ollama test reply" } }));
        }
    });
    app.use("/api/povi", route.router);
    app.post("/logout", (req, res) => { route.cancelSession(req.sessionID); req.session.destroy(() => res.json({ success: true })); });
    const server = app.listen(0, "127.0.0.1");
    await new Promise(resolve => server.once("listening", resolve));
    t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
    const base = `http://127.0.0.1:${server.address().port}`;
    async function request(url, { cookie, body, method = "GET" } = {}) {
        const response = await fetch(base + url, { method, headers: { ...(cookie ? { Cookie: cookie } : {}), ...(body !== undefined ? { "Content-Type": "application/json" } : {}) }, body: body !== undefined ? JSON.stringify(body) : undefined });
        return { status: response.status, data: await response.json(), headers: response.headers };
    }
    async function login(id) { return (await request(`/login/${id}`, { method: "POST" })).headers.get("set-cookie").split(";")[0]; }
    return { request, login, calls };
}
for (const provider of ["openai", "ollama"]) {
    test(`${provider}: authenticated chat, multi-turn isolation, reset, validation and logout`, async t => {
        const { request, login, calls } = await setup(t, provider);
        const post = (cookie, message) => request("/api/povi/chat", { cookie, method: "POST", body: { message } });
        assert.equal((await post(undefined, "hello")).status, 401);
        const alice = await login("alice");
        assert.equal((await post(alice, " ")).status, 400);
        assert.equal((await post(alice, {})).status, 400);
        assert.equal((await post(alice, "x".repeat(2001))).status, 400);
        assert.equal((await post(alice, "first")).status, 200);
        assert.equal((await post(alice, "second")).status, 200);
        const history = provider === "ollama" ? calls[1].messages.slice(1) : calls[1].input;
        assert.equal(history.length, 3);
        assert.equal(history[0].content, "first");
        const bob = await login("bob");
        assert.equal((await post(bob, "isolated")).status, 200);
        assert.equal(provider === "ollama" ? calls[2].messages.length : calls[2].input.length, provider === "ollama" ? 2 : 1);
        assert.equal((await request("/api/povi/reset", { cookie: bob, method: "POST" })).status, 200);
        assert.deepEqual((await request("/api/povi/chat", { cookie: bob })).data.messages, []);
        assert.equal((await request("/logout", { cookie: alice, method: "POST" })).status, 200);
        assert.equal((await post(alice, "after logout")).status, 401);
    });
}
for (const [label, respond, status, code] of [
    ["server offline", () => { throw new TypeError("SECRET connection details"); }, 503, "povi_local_unavailable"],
    ["model missing", () => new Response("SECRET model details", { status: 404 }), 503, "povi_local_model_missing"],
    ["timeout", () => { throw Object.assign(new Error("SECRET timeout"), { name: "TimeoutError" }); }, 504, "povi_timeout"],
    ["invalid JSON", () => new Response("not JSON"), 503, "povi_local_unavailable"],
    ["malformed response", () => new Response(JSON.stringify({ done: true })), 503, "povi_local_unavailable"],
    ["provider failure", () => new Response("SECRET", { status: 500 }), 503, "povi_local_unavailable"]
]) {
    test(`Ollama ${label}: safe error, no OpenAI fallback, no saved failed turn`, async t => {
        const { request, login, calls } = await setup(t, "ollama", respond);
        const cookie = await login("alice");
        const result = await request("/api/povi/chat", { cookie, method: "POST", body: { message: "Hi" } });
        assert.equal(result.status, status);
        assert.equal(result.data.code, code);
        assert.doesNotMatch(JSON.stringify(result.data), /SECRET|OpenAI/);
        assert.equal(calls.length, 1);
        assert.deepEqual((await request("/api/povi/chat", { cookie })).data.messages, []);
    });
}
