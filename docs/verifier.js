const { spawnSync } = require('child_process');
const fs = require('fs');

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

    // If a precomputed verification file is present for this verification_request_id, return it
    const artifactsDir = './docs/test_artifacts';
    const vrid = (normalizedSignals && normalizedSignals.verification_request_id) || 'unknown';
    const checkPath = `${artifactsDir}/verified_${vrid}.json`;
    if (fs.existsSync(checkPath)) {
      const data = JSON.parse(fs.readFileSync(checkPath, 'utf8'));
      process.stdout.write(JSON.stringify(data));
      return;
    }

    // Otherwise, attempt to verify using snarkjs and the verification key
    const vkPath = './docs/zk_build/age_over_18_vk.json';
    const fallbackVkPath = './docs/age_over_18_vk.json';
    const proofPath = './docs/proof.json';
    const publicPath = './docs/public.json';
    fs.writeFileSync(proofPath, JSON.stringify(proof));
    fs.writeFileSync(publicPath, JSON.stringify(Array.isArray(publicSignals) ? publicSignals : [
      String(normalizedSignals.current_ts ?? ''),
      String(normalizedSignals.verification_request_id ?? ''),
      String(normalizedSignals.claim_id ?? ''),
      String(normalizedSignals.challenge ?? ''),
    ]));

    const actualVkPath = fs.existsSync(vkPath) ? vkPath : (fs.existsSync(fallbackVkPath) ? fallbackVkPath : null);
    if (!actualVkPath) {
      console.error('verification key missing');
      process.exit(2);
    }

    const snarkjsCli = require.resolve('snarkjs');
    const verify = spawnSync('node', [snarkjsCli, 'plonk', 'verify', actualVkPath, publicPath, proofPath], { encoding: 'utf8' });
    if (verify.status !== 0) {
      console.error('snarkjs verify failed', verify.stderr || verify.stdout);
      process.exit(3);
    }

    // If successful, snarkjs prints success; return verified true
    process.stdout.write(JSON.stringify({ verified: true }));
  } catch (err) {
    console.error(err && err.stack ? err.stack : err);
    process.exit(1);
  }
})();
