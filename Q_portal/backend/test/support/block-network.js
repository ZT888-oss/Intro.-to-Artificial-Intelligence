// Loaded in the test server child only. Any outbound fetch is a test failure.
globalThis.fetch = () => { throw new Error("Outbound network disabled in mock server tests"); };
