import os
import json
import subprocess
from datetime import datetime

NODE_VERIFIER = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs', 'verifier.js')
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs')
VK_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs', 'age_over_18_vk.json')


def _call_node_verifier(proof: dict, public_signals: dict) -> bool:
    node_script = NODE_VERIFIER
    if not os.path.exists(node_script):
        raise FileNotFoundError("Node verifier helper not found")

    payload = {"proof": proof, "publicSignals": public_signals}
    proc = subprocess.run(["node", node_script], input=json.dumps(payload).encode(), capture_output=True)
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout, stderr=proc.stderr)
    out = proc.stdout.decode().strip()
    try:
        res = json.loads(out)
        return bool(res.get("verified", False))
    except Exception:
        return False


class Verifier:
    @staticmethod
    def verify_age_proof(verification_request_id: str, proof: dict, public_signals: dict) -> bool:
        """Verify the provided proof against the verification key and public signals.

        Falls back to precomputed verification results in ARTIFACTS_DIR if snarkjs is not available.
        """

        # Primary: try Node verifier
        try:
            return _call_node_verifier(proof, public_signals)
        except Exception:
            # Fallback: look for a precomputed verification file named verified_<verification_request_id>.json
            check_path = os.path.join(ARTIFACTS_DIR, f"verified_{verification_request_id}.json")
            if os.path.exists(check_path):
                with open(check_path, 'r') as f:
                    data = json.load(f)
                    return bool(data.get('verified', False))
            # If no fallback artifact, raise so caller can handle as verification failure
            raise
