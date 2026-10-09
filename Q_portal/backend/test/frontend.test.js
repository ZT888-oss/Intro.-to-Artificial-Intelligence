const { test } = require("node:test");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const { mkdtemp, rm } = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const net = require("node:net");
const { loadFrontend } = require("./support/frontend");
const { classifyPoviError } = require("../povi-errors");

async function mockServer(t) {
    const cwd = await mkdtemp(path.join(os.tmpdir(), "q-povi-mock-test-"));
    const reservation = net.createServer();
    await new Promise(resolve => reservation.listen(0, "127.0.0.1", resolve));
    const port = reservation.address().port;
    await new Promise(resolve => reservation.close(resolve));
    const child = spawn(process.execPath, ["--require", path.join(__dirname, "support/block-network.js"), path.join(__dirname, "../server.js")], {
        cwd, env: { ...process.env, LLM_PROVIDER: "openai", PORT: String(port), NODE_ENV: "development", POVI_MOCK_MODE: "true", OPENAI_API_KEY: "not-a-real-key", SESSION_SECRET: "test-only-session-secret" },
        stdio: ["ignore", "pipe", "pipe"]
    });
    const exited = new Promise(resolve => child.once("exit", resolve));
    t.after(async () => { child.kill(); await exited; await rm(cwd, { recursive: true, force: true }); });
    await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error("Mock server startup timed out")), 5000);
        child.stdout.on("data", data => { if (String(data).includes("Server running")) { clearTimeout(timeout); resolve(); } });
        child.once("exit", () => { clearTimeout(timeout); reject(new Error("Mock server exited before startup")); });
    });
    const base = `http://127.0.0.1:${port}`;
    function browserSession() {
        let cookie;
        const calls = [];
        async function browserFetch(url, options = {}) {
            assert.ok(String(url).startsWith("/"), "only local endpoints allowed");
            calls.push({ url, options });
            const response = await fetch(base + url, { ...options, headers: { ...options.headers, ...(cookie ? { Cookie: cookie } : {}) } });
            if (response.headers.get("set-cookie")) cookie = response.headers.get("set-cookie").split(";")[0];
            return response;
        }
        async function post(url, body) { return browserFetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); }
        async function login(name) {
            assert.equal((await post("/api/register", { username: name, email: `${name}@example.invalid`, password: "test-password-123" })).status, 201);
            assert.equal((await post("/api/login", { username: name, password: "test-password-123" })).status, 200);
        }
        return { fetch: browserFetch, post, calls, login };
    }
    return { browserSession };
}

test("actual frontend exchanges authenticated mock chat with real server, restores history, resets and logs out", async t => {
    const { browserSession } = await mockServer(t);
    const alice = browserSession();
    assert.equal((await alice.post("/api/povi/chat", { message: "Hi" })).status, 401);
    await alice.login("alice");
    const ui = await loadFrontend(alice.fetch);
    assert.equal(ui.elements["povi-error"].textContent, "");
    const input = ui.elements["student-message"];
    const unsafe = '<img src=x onerror="alert(1)">';
    input.value = unsafe;
    const pending = ui.submit();
    assert.equal(ui.elements["submit-button"].disabled, true);
    assert.equal(ui.elements["povi-status"].textContent, "Povi is thinking…");
    await ui.submit(); // duplicate while pending must be ignored
    await pending;
    assert.equal(alice.calls.filter(call => call.url === "/api/povi/chat" && call.options.method === "POST").length, 2); // includes anonymous request
    assert.equal(ui.text()[1], unsafe); // rendered as literal text, not HTML
    assert.match(ui.text()[2], /Development mock.*message 1/);
    assert.equal(input.value, "");
    assert.equal(ui.elements["submit-button"].disabled, false);
    assert.equal(ui.elements["povi-status"].textContent, "");
    assert.equal(ui.elements["povi-response"].scrollTop, 100);
    input.value = "second turn";
    input.listeners.keydown({ key: "Enter", shiftKey: false, isComposing: false, preventDefault() {} });
    await ui.elements["povi-form"].pendingSubmit;
    assert.match(ui.text().at(-1), /message 2/);
    const reload = await loadFrontend(alice.fetch);
    assert.equal(reload.text().length, 4);
    assert.equal(reload.text()[0], unsafe);
    const before = alice.calls.length;
    input.value = "   "; await ui.submit();
    input.value = "x".repeat(2001); await ui.submit();
    assert.equal(alice.calls.length, before);
    assert.match(ui.elements["povi-error"].textContent, /1–2000/);
    const invalid = browserSession(); await invalid.login("invalid");
    for (const message of ["", 123, null, "x".repeat(2001)]) {
        assert.equal((await invalid.post("/api/povi/chat", { message })).status, 400);
    }
    const bob = browserSession(); await bob.login("bob");
    assert.deepEqual((await (await bob.fetch("/api/povi/chat")).json()).messages, []);
    await reload.reset();
    assert.equal(reload.text().length, 1);
    assert.deepEqual((await (await alice.fetch("/api/povi/chat")).json()).messages, []);
    reload.elements["student-message"].value = "new conversation";
    await reload.submit();
    assert.match(reload.text().at(-1), /message 1/);
    assert.equal((await alice.post("/api/logout", {})).status, 200);
    reload.elements["student-message"].value = "after logout";
    await reload.submit();
    assert.match(reload.elements["povi-error"].textContent, /log in/);
    assert.equal(reload.elements["submit-button"].disabled, false);
    assert.equal((await alice.fetch("/api/povi/chat")).status, 401);
    assert.equal((await alice.post("/api/povi/reset", {})).status, 401);
    assert.equal((await alice.post("/api/login", { username: "alice", password: "test-password-123" })).status, 200);
    assert.deepEqual((await (await alice.fetch("/api/povi/chat")).json()).messages, []);
});

test("frontend displays quota error, preserves draft, and clears thinking state", async () => {
    const failure = classifyPoviError({ status: 429, code: "credit_balance_exhausted", type: "insufficient_quota" });
    const calls = [];
    const ui = await loadFrontend(async (url, options = {}) => {
        calls.push({ url, options });
        return options.method === "POST" ? new Response(JSON.stringify({ success: false, code: failure.code, message: failure.message }), { status: failure.status }) :
            new Response(JSON.stringify({ success: true, messages: [] }));
    });
    ui.elements["student-message"].value = "my draft";
    await ui.submit();
    assert.equal(ui.elements["povi-error"].textContent, failure.message);
    assert.match(failure.message, /credits or usage limit/);
    assert.doesNotMatch(failure.message, /in a minute/);
    assert.equal(ui.elements["student-message"].value, "my draft");
    assert.equal(ui.elements["submit-button"].disabled, false);
    assert.equal(ui.elements["povi-status"].textContent, "");
    assert.equal(ui.text().length, 1);
    assert.equal(calls[1].options.credentials, "include");
    assert.deepEqual(JSON.parse(calls[1].options.body), { message: "my draft" });
});


test("incoming replies preserve older-message reading position and follow users near the bottom", async () => {
    let finish;
    const ui = await loadFrontend(async (url, options = {}) => {
        if (options.method === "POST") return new Promise(resolve => {
            finish = () => resolve(new Response(JSON.stringify({ success: true, reply: "New reply" })));
        });
        return new Response(JSON.stringify({ success: true, messages: [] }));
    });
    const log = ui.elements["povi-response"];
    const input = ui.elements["student-message"];
    log.scrollHeight = 1000;
    log.clientHeight = 300;
    log.scrollTop = 700;
    input.value = "first";
    const pending = ui.submit();
    log.scrollTop = 200; // User scrolls up while Povi is thinking.
    finish();
    await pending;
    assert.equal(log.scrollTop, 200);
    assert.equal(ui.text().at(-1), "New reply");
    assert.equal(ui.text().length, 3);
    log.scrollTop = 680; // Within 40px of the bottom.
    input.value = "second";
    const next = ui.submit();
    finish();
    await next;
    assert.equal(log.scrollTop, log.scrollHeight);
    assert.equal(ui.text().length, 5);
});
