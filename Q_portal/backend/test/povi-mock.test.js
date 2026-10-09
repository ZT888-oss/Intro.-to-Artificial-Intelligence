const { test } = require("node:test");
const assert = require("node:assert/strict");
const { createDevelopmentMock } = require("../povi-mock");
const { createPoviRouter } = require("../povi");

test("mock is disabled by default, including in development", () => {
    assert.equal(createDevelopmentMock({}), null);
    assert.equal(createDevelopmentMock({ NODE_ENV: "development" }), null);
    assert.equal(createDevelopmentMock({ NODE_ENV: "development", POVI_MOCK_MODE: "false" }), null);
});
for (const mode of ["production", "test", undefined]) {
    test(`mock fails closed when NODE_ENV is ${mode}`, () => {
        assert.throws(() => createDevelopmentMock({ NODE_ENV: mode, POVI_MOCK_MODE: "true" }), /requires NODE_ENV=development/);
    });
}
test("development mock uses bounded input history and labels the response", async () => {
    const mock = createDevelopmentMock({ NODE_ENV: "development", POVI_MOCK_MODE: "true" });
    const result = await mock.responses.create({ input: [
        { role: "user", content: "first" }, { role: "assistant", content: "reply" }, { role: "user", content: "second" }
    ] });
    assert.equal(result.status, "completed");
    assert.match(result.output_text, /Development mock.*no AI request sent/);
    assert.match(result.output_text, /message 2/);
});
test("production router rejects mock even if a client is injected", t => {
    setEnv(t, { NODE_ENV: "production", POVI_MOCK_MODE: "true" });
    assert.throws(() => createPoviRouter({ client: { responses: {} } }), /forbidden in production/);
});
test("development mock bypasses SDK creation even with an invalid key", async t => {
    setEnv(t, { NODE_ENV: "development", POVI_MOCK_MODE: "true", OPENAI_API_KEY: "not-a-real-key" });
    const router = createPoviRouter({ client: { responses: { create() { throw new Error("Client must never run"); } } } });
    assert.ok(router.router);
});

function setEnv(t, values) {
    const previous = Object.fromEntries(Object.keys(values).map(key => [key, process.env[key]]));
    Object.assign(process.env, values);
    t.after(() => {
        for (const [key, value] of Object.entries(previous)) {
            if (value === undefined) delete process.env[key];
            else process.env[key] = value;
        }
    });
}
