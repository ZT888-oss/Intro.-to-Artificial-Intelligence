const { test } = require("node:test");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const { mkdtemp, rm } = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const net = require("node:net");

async function startServer(t, environment = {}) {
    const cwd = await mkdtemp(path.join(os.tmpdir(), "q-portal-test-"));
    const reservation = net.createServer();
    await new Promise(resolve => reservation.listen(0, "127.0.0.1", resolve));
    const port = reservation.address().port;
    await new Promise(resolve => reservation.close(resolve));
    const child = spawn(process.execPath, [path.join(__dirname, "../server.js")], {
        cwd, env: { ...process.env, LLM_PROVIDER: "openai", PORT: String(port), NODE_ENV: "test", OPENAI_API_KEY: "", POVI_MOCK_MODE: "false", SESSION_SECRET: "test-only-secret", ...environment },
        stdio: ["ignore", "pipe", "pipe"]
    });
    const exited = new Promise(resolve => child.once("exit", resolve));
    t.after(async () => { child.kill(); await exited; await rm(cwd, { recursive: true, force: true }); });
    await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error("Server startup timed out")), 5000);
        child.stdout.on("data", data => { if (String(data).includes("Server running")) { clearTimeout(timeout); resolve(); } });
        child.once("exit", () => { clearTimeout(timeout); reject(new Error("Server exited before startup")); });
    });
    let cookie;
    async function request(route, method = "GET", body, headers = {}) {
        const res = await fetch(`http://127.0.0.1:${port}${route}`, { method,
            headers: { ...headers, ...(cookie ? { Cookie: cookie } : {}), ...(body ? { "Content-Type": "application/json" } : {}) },
            body: body ? JSON.stringify(body) : undefined });
        if (res.headers.get("set-cookie")) cookie = res.headers.get("set-cookie").split(";")[0];
        return { status: res.status, data: await res.json(), headers: res.headers };
    }
    return { request, base: `http://127.0.0.1:${port}` };
}

test("real server starts; registration, login, mood, wellbeing, and logout work", async t => {
    const { request } = await startServer(t);
    assert.equal((await request("/api/povi/chat", "POST", { message: "Hi" })).status, 401);
    assert.equal((await request("/api/register", "POST", { username: "regression", email: "regression@example.invalid", password: "test-password-123" })).status, 201);
    assert.equal((await request("/api/login", "POST", { username: "regression", password: "wrong" })).status, 401);
    assert.equal((await request("/api/login", "POST", { username: "regression", password: "test-password-123" })).status, 200);
    assert.equal((await request("/api/mood-checkins", "POST", { moodLevel: 4 })).status, 201);
    assert.equal((await request("/api/mood-checkins")).data.checkedInToday, true);
    assert.equal((await request("/api/mood-checkins", "POST", { moodLevel: 4 })).status, 409);
    assert.equal((await request("/api/wellbeing-index")).data.index, 75);
    assert.equal((await request("/api/povi/chat", "POST", { message: "Hi" })).status, 503);
    assert.equal((await request("/api/logout", "POST")).status, 200);
    assert.equal((await request("/api/povi/chat")).status, 401);
});


test("public root serves login and its assets without affecting other pages or API 404s", async t => {
    const { base } = await startServer(t);
    const root = await fetch(base + "/");
    const login = await fetch(base + "/login.html");
    assert.equal(root.status, 200);
    assert.match(root.headers.get("content-type"), /text\/html/);
    assert.equal(await root.text(), await login.text());
    for (const route of ["/Login/login_UI.css", "/Login/login.js", "/register.html", "/dashboard.html"]) {
        assert.equal((await fetch(base + route)).status, 200);
    }
    assert.equal((await fetch(base + "/api/nonexistent")).status, 404);
});

test("production login behind local HTTPS tunnel issues secure cookie and authenticates subsequent requests", async t => {
    const { request } = await startServer(t, { NODE_ENV: "production" });
    const proxy = { "X-Forwarded-Proto": "https" };
    assert.equal((await request("/api/register", "POST", { username: "tunnel", email: "tunnel@example.invalid", password: "test-password-123" }, proxy)).status, 201);
    const credentials = { username: "tunnel", password: "test-password-123" };
    const plainLogin = await request("/api/login", "POST", credentials);
    assert.equal(plainLogin.status, 200);
    assert.equal(plainLogin.headers.get("set-cookie"), null, "production must not issue a secure session cookie over plain HTTP");
    const login = await request("/api/login", "POST", credentials, proxy);
    assert.equal(login.status, 200);
    const cookie = login.headers.get("set-cookie");
    assert.ok(cookie, "secure session cookie must be issued behind HTTPS tunnel");
    assert.match(cookie, /; Secure(?:;|$)/);
    assert.match(cookie, /; HttpOnly(?:;|$)/);
    assert.match(cookie, /; SameSite=Lax(?:;|$)/);
    assert.doesNotMatch(cookie, /; Domain=/);
    assert.equal((await request("/api/mood-checkins", "GET", undefined, proxy)).status, 200);
    assert.equal((await request("/api/logout", "POST", undefined, proxy)).status, 200);
    assert.equal((await request("/api/mood-checkins", "GET", undefined, proxy)).status, 401);
});
