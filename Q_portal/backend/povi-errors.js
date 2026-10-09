// Never return/log upstream messages: they may contain sensitive request details.
const QUOTA_CODES = new Set([
    "insufficient_quota", "credit_balance_exhausted", "billing_hard_limit_reached",
    "project_spend_limit_exceeded", "organization_spend_limit_exceeded",
    "organization_usage_limit_exceeded", "usage_limit_exceeded"
]);
function classifyPoviError(error, aborted = false, provider = "openai") {
    if (provider === "ollama") {
        if (aborted || error.name === "AbortError" || error.name === "TimeoutError") {
            return { status: 504, code: "povi_timeout", message: "The local AI took too long to reply. Please try again once the model has loaded." };
        }
        if (error.status === 404) {
            return { status: 503, code: "povi_local_model_missing", message: "Povi's local model is unavailable. Ask the portal administrator to install the configured Ollama model." };
        }
        return { status: 503, code: "povi_local_unavailable", message: "Povi's local AI is unavailable. Please check that Ollama is running and try again." };
    }
    const code = error.code || error.error?.code;
    const type = error.type || error.error?.type;
    if (QUOTA_CODES.has(code) || type === "insufficient_quota") {
        return { status: 503, code: "povi_quota_unavailable",
            message: "Povi is unavailable because its API credits or usage limit have been reached. The portal administrator needs to check OpenAI billing and limits." };
    }
    if (aborted || error.name === "APIConnectionTimeoutError") {
        return { status: 504, code: "povi_timeout", message: "Povi took too long to reply. Please try again." };
    }
    if (error.status === 429) {
        const header = error.headers?.get?.("retry-after");
        const seconds = header && /^\d+$/.test(header) ? Number(header) : 60;
        const retryAfter = Math.max(1, Math.min(seconds, 3600));
        return { status: 429, code: "povi_rate_limited", retryAfter,
            message: `Povi has reached a temporary request limit. Please try again in ${retryAfter} seconds.` };
    }
    if ([400, 401, 403, 404].includes(error.status)) {
        return { status: 503, code: "povi_configuration_error",
            message: "Povi could not connect with its current API configuration. The portal administrator needs to check the API key and model access." };
    }
    return { status: 503, code: "povi_unavailable", message: "Povi is temporarily unavailable. Please try again later." };
}
module.exports = { classifyPoviError };
