// One minimal live request. Never print keys, request bodies, or raw upstream errors.
const path = require("node:path");
require("dotenv").config({ path: path.join(__dirname, "../.env"), quiet: true });
const OpenAI = require("openai");
const instructions = require("../povi-instructions");
async function main() {
    if ((process.env.LLM_PROVIDER || "openai") !== "openai" || process.env.POVI_MOCK_MODE === "true") {
        console.log(JSON.stringify({ ok: false, reason: "openai_diagnostic_disabled_for_local_or_mock_mode" }));
        process.exitCode = 1;
        return;
    }
    if (!process.env.OPENAI_API_KEY) {
        console.log(JSON.stringify({ ok: false, reason: "missing_api_key" }));
        process.exitCode = 1;
        return;
    }
    const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";
    const client = new OpenAI({ timeout: 25000, maxRetries: 0 });
    const start = Date.now();
    try {
        const response = await client.responses.create({
            model, instructions, input: "Say hello in one short sentence.",
            store: false, max_output_tokens: 600
        });
        console.log(JSON.stringify({ ok: Boolean(response.output_text), model,
            responseStatus: response.status, elapsedMs: Date.now() - start }));
    } catch (error) {
        const safe = value => typeof value === "string" && /^[a-zA-Z0-9_.-]{1,100}$/.test(value) ? value : undefined;
        console.log(JSON.stringify({ ok: false, model, status: error.status,
            code: safe(error.code), type: safe(error.type), name: safe(error.name),
            causeCode: safe(error.cause?.code), elapsedMs: Date.now() - start }));
        process.exitCode = 1;
    }
}
main();
