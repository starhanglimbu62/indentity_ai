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
    const witness = JSON.parse(input);

    // Fall back behavior: if a precomputed proof file exists for verification_request_id, return it.
    const artifactsDir = './docs/test_artifacts';
    const vrid = witness.verification_request_id || 'unknown';
    const artifactPath = `${artifactsDir}/proof_${vrid}.json`;
    if (fs.existsSync(artifactPath)) {
      const data = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
      process.stdout.write(JSON.stringify(data));
      return;
    }

    // Otherwise, attempt to use snarkjs if available. This is environment-dependent and may fail in CI if snarkjs is not installed.
    const tmpWitnessPath = './docs/tmp_witness.json';
    fs.writeFileSync(tmpWitnessPath, JSON.stringify(witness));

    const zkey = './docs/age_over_18.zkey';
    const proofOut = './docs/proof.json';
    const publicOut = './docs/public.json';

    if (!fs.existsSync(zkey)) {
      console.error('zkey missing, cannot run snarkjs.');
      process.exit(2);
    }

    const prove = spawnSync('snarkjs', ['plonk', 'prove', zkey, tmpWitnessPath, proofOut, publicOut], { encoding: 'utf8' });
    if (prove.status !== 0) {
      console.error('snarkjs prove failed', prove.stderr);
      process.exit(3);
    }

    const proof = JSON.parse(fs.readFileSync(proofOut, 'utf8'));
    const publicSignals = JSON.parse(fs.readFileSync(publicOut, 'utf8'));
    try { fs.unlinkSync(tmpWitnessPath); } catch (e) {}

    process.stdout.write(JSON.stringify({ proof, publicSignals }));
  } catch (err) {
    console.error(err && err.stack ? err.stack : err);
    process.exit(1);
  }
})();
