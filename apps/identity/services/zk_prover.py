import os
import json
import subprocess
from typing import Dict, Any, Tuple

# Wrapper around a Node/snarkjs-based prover helper.

NODE_PROVER = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs', 'prover.js')


def _call_node_prover(witness: Dict[str, Any]) -> Dict[str, Any]:
    """Call the Node prover helper via subprocess. Pass witness JSON via stdin.
    Returns parsed JSON proof object. Raises subprocess.CalledProcessError when node/snarkjs fails.
    """
    node_script = NODE_PROVER
    if not os.path.exists(node_script):
        raise FileNotFoundError("Node prover helper not found")

    proc = subprocess.run(
        ["node", node_script],
        input=json.dumps(witness).encode(),
        capture_output=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout, stderr=proc.stderr)
    return json.loads(proc.stdout.decode())


class Prover:
    @staticmethod
    def generate_age_proof(credential_id: str, dob_ts: int, verification_request_id: str, challenge: str, current_ts: int) -> Dict[str, Any]:
        """Generates a proof for AGE_OVER_18.

        dob_ts and current_ts are integers (seconds since epoch).
        This function will not persist the witness; it will pass the witness to the prover process and
        return the resulting proof object.
        """
        witness = {
            "credential_id": str(credential_id),
            "dob_ts": int(dob_ts),
            "verification_request_id": str(verification_request_id),
            "challenge": str(challenge),
            "current_ts": int(current_ts),
        }

        return _call_node_prover(witness)
