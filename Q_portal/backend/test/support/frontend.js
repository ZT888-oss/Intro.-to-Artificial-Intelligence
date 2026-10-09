const vm = require("node:vm");
const fs = require("node:fs");
const path = require("node:path");

// Minimal DOM adapter: executes the actual frontend script against real HTTP.
// These tests verify behavior; they do not verify browser layout or CSS.
async function loadFrontend(fetch) {
    class Element {
        constructor() { this.children = []; this.listeners = {}; this.value = ""; this.textContent = ""; this.disabled = false; this.scrollHeight = 100; this.clientHeight = 100; this.scrollTop = 0; }
        addEventListener(name, callback) { this.listeners[name] = callback; }
        setAttribute(name, value) { this[name] = value; }
        append(...children) { children.forEach(child => { child.parent = this; this.children.push(child); }); }
        replaceChildren() { this.children = []; }
        remove() { this.parent.children = this.parent.children.filter(child => child !== this); }
        focus() { this.focused = true; }
        get firstElementChild() { return this.children[0]; }
        requestSubmit() { this.pendingSubmit = this.listeners.submit({ preventDefault() {} }); }
    }
    const elements = Object.fromEntries(["povi-form", "student-message", "povi-response", "submit-button", "reset-chat", "povi-status", "povi-error"].map(id => [id, new Element()]));
    let ready;
    const document = {
        getElementById: id => elements[id], createElement: () => new Element(),
        addEventListener: (name, callback) => { if (name === "DOMContentLoaded") ready = callback; }
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../../../frontend/Dashboard/povi-chat.js"), "utf8"), {
        document, fetch, AbortController, setTimeout, clearTimeout, TypeError, SyntaxError
    });
    await ready();
    return { elements, submit: () => elements["povi-form"].listeners.submit({ preventDefault() {} }),
        reset: () => elements["reset-chat"].listeners.click(),
        text: () => elements["povi-response"].children.map(bubble => bubble.children[1].textContent) };
}
module.exports = { loadFrontend };
