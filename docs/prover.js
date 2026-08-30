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
    console.error("[1] Prover started");
    const inputPath = path.join(__dirname, "tmp_input.json");
    const wasmPath = path.join(__dirname, "zk_build", "age_over_18_js", "age_over_18.wasm");
    const zkeyPath = path.join(__dirname, "zk_build", "age_over_18.zkey");
    const legacyZkeyPath = path.join(__dirname, "age_over_18.zkey");

    console.error("[1a] Resolving file paths", {
        __dirname,
        inputPath,
        wasmPath,
        zkeyPath,
        legacyZkeyPath,
        inputExists: fs.existsSync(inputPath),
        wasmExists: fs.existsSync(wasmPath),
        zkeyExists: fs.existsSync(zkeyPath),
        legacyZkeyExists: fs.existsSync(legacyZkeyPath),
    });
    
    if (!fs.existsSync(inputPath)) {
        console.error("ERROR: tmp_input.json not found!");
        process.exit(1);
    }
    let inputData;
    if (process.stdin.isTTY) {
        inputData = JSON.parse(fs.readFileSync(inputPath, "utf8"));
    } else {
        const stdinChunks = [];
        for await (const chunk of process.stdin) {
            stdinChunks.push(chunk);
        }
        const stdinData = Buffer.concat(stdinChunks).toString("utf8").trim();
        inputData = JSON.parse(stdinData || fs.readFileSync(inputPath, "utf8"));
    }

    const circuitInput = {
        dob_ts: inputData.dob_ts,
        current_ts: inputData.current_ts,
        challenge: encodeFieldElement(inputData.challenge),
        verification_request_id: encodeFieldElement(inputData.verification_request_id),
        claim_id: inputData.claim_id || "1",
    };

    const activeZkeyPath = fs.existsSync(zkeyPath) ? zkeyPath : legacyZkeyPath;
    console.error("[2] Starting fullProve with zkey:", activeZkeyPath);

    try {
        const { proof, publicSignals } = await snarkjs.plonk.fullProve(
            circuitInput,
            wasmPath,
            activeZkeyPath
        );

        console.error("[3] Proof generated successfully!");

        const proofJson = JSON.stringify(proof, null, 2);
        const publicSignalsJson = JSON.stringify(publicSignals, null, 2);

        fs.writeFileSync(path.join(__dirname, "proof.json"), proofJson);
        fs.writeFileSync(path.join(__dirname, "public.json"), publicSignalsJson);

        console.error("[4] Files written. Forcing exit.");
        process.stdout.write(JSON.stringify({ proof, publicSignals }));
        process.exit(0);
    } catch (err) {
        console.error("[PROVER ERROR]", err.message, err.stack);
        process.exit(1);
    }
}

run().catch((err) => {
    console.error("[!] FATAL ERROR:", err && err.message ? err.message : err);
    console.error(err && err.stack ? err.stack : "No stack trace available");
    process.exit(1);
});
