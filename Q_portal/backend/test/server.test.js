const { test } = require("node:test");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const { mkdtemp, rm } = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const net = require("node:net");

test("real server starts; registration, login, mood, wellbeing, and logout work", async t => {
    const cwd = await mkdtemp(path.join(os.tmpdir(), "q-portal-test-"));
    const reservation = net.createServer();
    await new Promise(resolve => reservation.listen(0, "127.0.0.1", resolve));
    const port = reservation.address().port;
    await new Promise(resolve => reservation.close(resolve));
    const child = spawn(process.execPath, [path.join(__dirname, "../server.js")], {
        cwd, env: { ...process.env, LLM_PROVIDER: "openai", PORT: String(port), NODE_ENV: "test", OPENAI_API_KEY: "", POVI_MOCK_MODE: "false", SESSION_SECRET: "test-only-secret" },
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
    async function request(route, method = "GET", body) {
        const res = await fetch(`http://127.0.0.1:${port}${route}`, { method,
            headers: { ...(cookie ? { Cookie: cookie } : {}), ...(body ? { "Content-Type": "application/json" } : {}) },
            body: body ? JSON.stringify(body) : undefined });
        if (res.headers.get("set-cookie")) cookie = res.headers.get("set-cookie").split(";")[0];
        return { status: res.status, data: await res.json() };
    }
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
