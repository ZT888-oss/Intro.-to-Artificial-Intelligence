const express = require("express");
const OpenAI = require("openai");
const { rateLimit } = require("express-rate-limit");
const instructions = require("./povi-instructions");

const MAX_MESSAGE = 2000;
const HISTORY_TTL = 30 * 60 * 1000;

// Injectable client keeps automated tests independent of credentials and paid API calls.
function createPoviRouter({ client, model = process.env.OPENAI_MODEL || "gpt-4.1-mini" } = {}) {
    const router = express.Router();
    const active = new Map();
    const api = client || (process.env.OPENAI_API_KEY ? new OpenAI({
        apiKey: process.env.OPENAI_API_KEY,
        timeout: 25000,
        maxRetries: 0
    }) : null);

    function history(req) {
        const chat = req.session.povi;
        return chat && Date.now() - chat.updatedAt < HISTORY_TTL ? chat.messages : [];
    }

    function cancelSession(sessionId) {
        active.get(sessionId)?.abort();
    }

    router.use((req, res, next) => {
        res.set("Cache-Control", "no-store");
        if (!req.session?.userId) {
            return res.status(401).json({ success: false, message: "Please log in to talk to Povi." });
        }
        next();
    });
    router.use(rateLimit({
        windowMs: 60000,
        limit: 10,
        keyGenerator: req => String(req.session.userId),
        standardHeaders: "draft-8",
        legacyHeaders: false,
        message: { success: false, message: "Please wait a minute before sending more messages." }
    }));

    router.get("/chat", (req, res) => res.json({ success: true, messages: history(req) }));
    router.post("/reset", (req, res) => {
        if (active.has(req.sessionID)) {
            return res.status(409).json({ success: false, message: "Please wait for Povi's reply before resetting." });
        }
        active.set(req.sessionID, new AbortController());
        delete req.session.povi;
        req.session.save(error => {
            active.delete(req.sessionID);
            if (error) return res.status(500).json({ success: false, message: "Unable to reset this conversation." });
            res.json({ success: true });
        });
    });
    router.post("/chat", async (req, res) => {
        const message = req.body?.message;
        if (typeof message !== "string" || !message.trim() || message.length > MAX_MESSAGE) {
            return res.status(400).json({ success: false, message: `Enter a message of 1–${MAX_MESSAGE} characters.` });
        }
        if (!api) return res.status(503).json({ success: false, message: "Povi is not configured yet. Please try again later." });
        if (active.has(req.sessionID)) {
            return res.status(409).json({ success: false, message: "Povi is already replying. Please wait." });
        }
        const previousChat = req.session.povi;
        const controller = new AbortController();
        active.set(req.sessionID, controller);
        const timeout = setTimeout(() => controller.abort(), 25000);
        try {
            const input = [...history(req), { role: "user", content: message.trim() }];
            const result = await api.responses.create({
                model, instructions, input, store: false, max_output_tokens: 600
            }, { signal: controller.signal });
            const reply = result.output_text?.trim();
            if (!reply || result.status === "incomplete" || result.error) {
                return res.status(502).json({ success: false, message: "Povi could not complete a reply. Please try again." });
            }
            // Logout or a new login cancels this request; never save the old session again.
            if (controller.signal.aborted) throw new Error("Cancelled");
            const messages = [...input, { role: "assistant", content: reply }].slice(-12);
            while (messages.length > 2 && messages.reduce((sum, item) => sum + item.content.length, 0) > 12000) {
                messages.splice(0, 2);
            }
            req.session.povi = { messages, updatedAt: Date.now() };
            await new Promise((resolve, reject) => req.session.save(error => error ? reject(error) : resolve()));
            res.json({ success: true, reply });
        } catch (error) {
            if (previousChat) req.session.povi = previousChat;
            else delete req.session.povi;
            // Do not log request bodies, upstream errors, or credentials.
            const limited = error.status === 429;
            const timedOut = controller.signal.aborted || error.name === "APIConnectionTimeoutError";
            if (limited) res.set("Retry-After", "60");
            res.status(limited ? 429 : timedOut ? 504 : 503).json({
                success: false,
                message: limited ? "Povi is busy. Please try again in a minute." : timedOut ?
                    "Povi took too long to reply. Please try again." : "Povi is temporarily unavailable. Please try again later."
            });
        } finally {
            clearTimeout(timeout);
            active.delete(req.sessionID);
        }
    });
    return { router, cancelSession };
}
module.exports = { createPoviRouter };
