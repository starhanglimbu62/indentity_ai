const snarkjs = require("snarkjs");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const FIELD_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;

function encodeFieldElement(value) {
    const text = String(value);
    if (/^\d+$/.test(text)) {
        return text;
    }

    const digest = crypto.createHash("sha256").update(text, "utf8").digest("hex");
    return (BigInt(`0x${digest}`) % FIELD_PRIME).toString();
}

async function run() {
    const wasmPath = path.join(__dirname, "zk_build", "age_over_18_js", "age_over_18.wasm");
    const zkeyPath = path.join(__dirname, "zk_build", "age_over_18.zkey");
    const legacyZkeyPath = path.join(__dirname, "age_over_18.zkey");
    const stdinChunks = [];
    for await (const chunk of process.stdin) {
        stdinChunks.push(chunk);
    }
    const stdinData = Buffer.concat(stdinChunks).toString("utf8").trim();
    if (!stdinData) {
        throw new Error("Prover input is required.");
    }
    const inputData = JSON.parse(stdinData);

    const circuitInput = {
        dob_ts: inputData.dob_ts,
        current_ts: inputData.current_ts,
        challenge: encodeFieldElement(inputData.challenge),
        verification_request_id: encodeFieldElement(inputData.verification_request_id),
        claim_id: inputData.claim_id || "1",
    };

    const activeZkeyPath = fs.existsSync(zkeyPath) ? zkeyPath : legacyZkeyPath;
    const { proof, publicSignals } = await snarkjs.plonk.fullProve(
        circuitInput,
        wasmPath,
        activeZkeyPath
    );
    process.stdout.write(
        JSON.stringify({ proof, publicSignals }),
        () => process.exit(0)
    );
}

run().catch((err) => {
    process.stderr.write(
        `Proof generation failed: ${err && err.message ? err.message : "unknown error"}\n`,
        () => process.exit(1)
    );
});
