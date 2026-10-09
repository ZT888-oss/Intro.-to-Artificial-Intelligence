// Local development only: deterministic responses, no SDK and no network access.
function createDevelopmentMock(env = process.env) {
    if (env.POVI_MOCK_MODE !== "true") return null;
    if (env.NODE_ENV !== "development") {
        throw new Error("POVI_MOCK_MODE requires NODE_ENV=development and is forbidden in production.");
    }
    return {
        responses: {
            async create({ input }, { signal } = {}) {
                if (signal?.aborted) throw new Error("Mock request cancelled");
                const turns = input.filter(item => item.role === "user").length;
                return {
                    status: "completed",
                    output_text: `[Development mock — no AI request sent] Thanks for sharing. This is message ${turns} in our current conversation. Try choosing one small, manageable next step. What would help you right now?`
                };
            }
        }
    };
}
module.exports = { createDevelopmentMock };
