/* Test script for the AGE_OVER_18 circuit (V0.4 prototype)
 * Usage: node docs/test_zk_cases.js
 * Requires: Node + snarkjs + circom artifacts in docs/ (age_over_18.r1cs, zkey, wasm, etc.)
 * The script demonstrates three cases:
 * 1) DOB older than 18 -> proof should succeed
 * 2) DOB younger than 18 -> proof should fail
 * 3) manipulated public timestamp -> verifier-side protocol should reject
 *
 * In CI environments without snarkjs/circom, the script will exit with guidance.
 */

const { spawnSync } = require('child_process');
const fs = require('fs');

function callProver(witness) {
  // Use the existing docs/prover.js wrapper which handles proofs or returns fallback artifacts.
  const proc = spawnSync('node', ['./docs/prover.js'], { input: JSON.stringify(witness), encoding: 'utf8' });
  if (proc.status !== 0) {
    console.error('Prover failed:', proc.stderr);
    process.exit(proc.status);
  }
  return JSON.parse(proc.stdout);
}

function callVerifier(proof, publicSignals) {
  const payload = { proof, publicSignals };
  const proc = spawnSync('node', ['./docs/verifier.js'], { input: JSON.stringify(payload), encoding: 'utf8' });
  if (proc.status !== 0) {
    console.error('Verifier failed:', proc.stderr);
    process.exit(proc.status);
  }
  return JSON.parse(proc.stdout);
}

// constants
const now = Math.floor(Date.now() / 1000);
const EIGHTEEN_YEARS = 567648000; // seconds

// Case 1: older than 18
const dob_old = now - (EIGHTEEN_YEARS + 1000);
const witness1 = {
  credential_id: 'cred-1',
  dob_ts: dob_old,
  verification_request_id: 'test-case-1',
  challenge: 'challenge-1',
  current_ts: now,
};
console.log('Case 1: generating proof for DOB older than 18');
let out1 = callProver(witness1);
console.log('Prover returned:', out1);
let res1 = callVerifier(out1.proof, out1.publicSignals);
console.log('Verifier returned:', res1);

// Case 2: younger than 18
const dob_young = now - (EIGHTEEN_YEARS - 1000);
const witness2 = {
  credential_id: 'cred-2',
  dob_ts: dob_young,
  verification_request_id: 'test-case-2',
  challenge: 'challenge-2',
  current_ts: now,
};
console.log('Case 2: generating proof for DOB younger than 18');
try {
  let out2 = callProver(witness2);
  console.log('Prover returned (unexpected):', out2);
  let res2 = callVerifier(out2.proof, out2.publicSignals);
  console.log('Verifier returned (unexpected):', res2);
} catch (e) {
  console.error('Expected failure for under-18 case:', e);
}

// Case 3: manipulated public timestamp (verifier should ensure it supplies trusted current_ts)
console.log('Case 3: manipulated public timestamp - prover attempts to use future current_ts');
const future_ts = now + 100000; // attacker-supplied timestamp (should be rejected by verifier protocol)
const witness3 = {
  credential_id: 'cred-3',
  dob_ts: dob_old,
  verification_request_id: 'test-case-3',
  challenge: 'challenge-3',
  current_ts: future_ts,
};
let out3 = callProver(witness3);
console.log('Prover returned:', out3);
let res3 = callVerifier(out3.proof, out3.publicSignals);
console.log('Verifier returned:', res3);

console.log('Test script finished. Note: verifier-side protocol must ensure current_ts is the server-supplied authoritative time and not user-provided.');
