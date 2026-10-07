const fs = require('fs');
const path = require('path');
const snarkjs = require('snarkjs');

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', d => data += d);
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', reject);
  });
}

(async () => {
  try {
    const input = await readStdin();
    const payload = JSON.parse(input);
    const proof = payload.proof;
    const publicSignals = payload.publicSignals;

    let normalizedSignals = publicSignals;
    if (Array.isArray(publicSignals)) {
      normalizedSignals = {
        current_ts: publicSignals[0],
        verification_request_id: publicSignals[1],
        claim_id: publicSignals[2],
        challenge: publicSignals[3],
      };
    }

    const baseDirectory = __dirname;
    const keyPaths = [
      path.join(baseDirectory, 'zk_build', 'age_over_18_vk.json'),
      path.join(baseDirectory, 'age_over_18_vk.json'),
    ];
    const keyPath = keyPaths.find(candidate => fs.existsSync(candidate));
    if (!keyPath) {
      throw new Error('Verification key is unavailable.');
    }

    const verificationKey = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
    const verified = await snarkjs.plonk.verify(
      verificationKey,
      _asArray(publicSignals, normalizedSignals),
      proof,
    );
    process.stdout.write(
      JSON.stringify({ verified: verified === true }),
      () => process.exit(0),
    );
  } catch (err) {
    process.stderr.write(
      `Proof verification failed: ${err && err.message ? err.message : 'unknown error'}\n`,
      () => process.exit(1),
    );
  }
})();

function _asArray(publicSignals, normalizedSignals) {
  if (Array.isArray(publicSignals)) {
    return publicSignals.map(String);
  }
  return [
    String(normalizedSignals.current_ts ?? ''),
    String(normalizedSignals.verification_request_id ?? ''),
    String(normalizedSignals.claim_id ?? ''),
    String(normalizedSignals.challenge ?? ''),
  ];
}
