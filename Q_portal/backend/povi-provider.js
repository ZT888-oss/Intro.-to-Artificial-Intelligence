const OpenAI = require("openai");
const { createDevelopmentMock } = require("./povi-mock");

const OLLAMA_CHAT_URL = "http://localhost:11434/api/chat";

// Adapts local chat output to the existing Responses-shaped interface.
function createOllamaClient(fetchImpl = globalThis.fetch) {
    return { responses: { async create({ model, instructions, input, max_output_tokens }, { signal } = {}) {
        const response = await fetchImpl(OLLAMA_CHAT_URL, {
            method: "POST",
            redirect: "error",
            headers: { "Content-Type": "application/json" },
            signal,
            body: JSON.stringify({
                model,
                messages: [{ role: "system", content: instructions }, ...input],
                stream: false,
                options: { num_predict: max_output_tokens, num_ctx: 8192 }
            })
        });
        if (!response.ok) {
            // Discard upstream error bodies rather than logging potentially private text.
            await response.body?.cancel();
            throw Object.assign(new Error("Local model request failed"), { status: response.status });
        }
        const data = await response.json();
        if (data.error || data.done !== true || typeof data.message?.content !== "string") {
            throw Object.assign(new Error("Invalid local model response"), { status: 502 });
        }
        return {
            status: data.done_reason === "length" ? "incomplete" : "completed",
            output_text: data.message.content
        };
    } } };
}

function createPoviProvider({ env = process.env, client, model, fetchImpl } = {}) {
    const provider = env.LLM_PROVIDER || "openai";
    if (!["openai", "ollama"].includes(provider)) {
        throw new Error("LLM_PROVIDER must be openai or ollama.");
    }
    const selectedModel = model || (provider === "ollama" ? env.OLLAMA_MODEL || "llama3.2:3b" : env.OPENAI_MODEL || "gpt-4.1-mini");
    if (provider === "ollama" && selectedModel.endsWith(":cloud")) {
        throw new Error("Povi's Ollama provider requires a local model, not a :cloud model.");
    }
    const mock = createDevelopmentMock(env);
    if (mock) return { provider, model: selectedModel, api: mock };
    // Ollama must never instantiate or fall back to the OpenAI client.
    if (provider === "ollama") {
        return { provider, model: selectedModel, api: createOllamaClient(fetchImpl) };
    }
    return { provider, model: selectedModel, api: client || (env.OPENAI_API_KEY ? new OpenAI({
        apiKey: env.OPENAI_API_KEY, timeout: 25000, maxRetries: 0
    }) : null) };
}
module.exports = { createPoviProvider, createOllamaClient, OLLAMA_CHAT_URL };
