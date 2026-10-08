// Conversation content stays in server-side sessions; no browser storage is used.
document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("povi-form");
    const input = document.getElementById("student-message");
    const log = document.getElementById("povi-response");
    const send = document.getElementById("submit-button");
    const reset = document.getElementById("reset-chat");
    const status = document.getElementById("povi-status");
    const error = document.getElementById("povi-error");
    let busy = false;

    function setBusy(value, label = "") {
        busy = value;
        send.disabled = reset.disabled = input.disabled = value;
        status.textContent = label;
        log.setAttribute("aria-busy", String(value));
    }
    function append(role, content) {
        const bubble = document.createElement("div");
        bubble.className = `chat-message chat-${role}`;
        const name = document.createElement("strong");
        name.textContent = role === "user" ? "You" : "Povi";
        const text = document.createElement("p");
        text.textContent = content;
        bubble.append(name, text);
        log.append(bubble);
        // Bound browser memory too, while preserving more of the visible conversation.
        while (log.children.length > 100) log.firstElementChild.remove();
        log.scrollTop = log.scrollHeight;
        return bubble;
    }
    async function request(url, options = {}) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 35000);
        try {
            const response = await fetch(url, { credentials: "include", ...options, signal: controller.signal });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || "Unable to reach Povi. Please try again.");
            return data;
        } catch (failure) {
            if (failure.name === "AbortError") throw new Error("The request timed out. Reload before retrying to check whether Povi replied.");
            if (failure instanceof TypeError || failure instanceof SyntaxError) {
                throw new Error("Unable to reach Povi. Check your connection and try again.");
            }
            throw failure;
        } finally {
            clearTimeout(timeout);
        }
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        if (busy) return;
        const message = input.value.trim();
        if (!message || input.value.length > 2000) {
            error.textContent = "Enter a message of 1–2000 characters.";
            return;
        }
        error.textContent = "";
        const bubble = append("user", message);
        setBusy(true, "Povi is thinking…");
        try {
            const data = await request("/api/povi/chat", {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });
            append("assistant", data.reply);
            input.value = "";
        } catch (failure) {
            bubble.remove();
            error.textContent = failure.message;
        } finally {
            setBusy(false);
            input.focus();
        }
    });
    input.addEventListener("keydown", event => {
        if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            if (!busy) form.requestSubmit();
        }
    });
    reset.addEventListener("click", async () => {
        if (busy) return;
        setBusy(true, "Starting a new conversation…");
        error.textContent = "";
        try {
            await request("/api/povi/reset", { method: "POST" });
            log.replaceChildren();
            input.value = "";
            append("assistant", "Hi, I'm Povi. What would you like to talk about?");
        } catch (failure) {
            error.textContent = failure.message;
        } finally {
            setBusy(false);
            input.focus();
        }
    });
    setBusy(true, "Loading conversation…");
    try {
        const data = await request("/api/povi/chat");
        if (data.messages.length) data.messages.forEach(item => append(item.role, item.content));
        else append("assistant", "Hi, I'm Povi. What has been on your mind?");
    } catch (failure) {
        error.textContent = failure.message;
    } finally {
        setBusy(false);
    }
});
