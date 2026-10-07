import os
import json
import subprocess

NODE_VERIFIER = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs', 'verifier.js')


def _as_public_signals_array(public_signals):
    if isinstance(public_signals, list):
        return [str(v) for v in public_signals]

    if isinstance(public_signals, dict):
        return [
            str(public_signals.get('current_ts', '')),
            str(public_signals.get('verification_request_id', '')),
            str(public_signals.get('claim_id', '')),
            str(public_signals.get('challenge', '')),
        ]

    return [str(public_signals)]


def _call_node_verifier(proof: dict, public_signals) -> bool:
    node_script = NODE_VERIFIER
    if not os.path.exists(node_script):
        raise FileNotFoundError("Node verifier helper not found")

    payload = {"proof": proof, "publicSignals": _as_public_signals_array(public_signals)}
    proc = subprocess.run(
        ["node", node_script],
        input=json.dumps(payload).encode(),
        capture_output=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout, stderr=proc.stderr)
    out = proc.stdout.decode().strip()
    try:
        res = json.loads(out)
        return res.get("verified") is True
    except (json.JSONDecodeError, AttributeError, TypeError):
        raise ValueError("Verifier returned an invalid response.")


class Verifier:
    @staticmethod
    def verify_age_proof(verification_request_id: str, proof: dict, public_signals: dict) -> bool:
        """Verify the provided proof against the verification key and public signals.

        Missing dependencies, invalid responses, and timeouts fail closed.
        """
        return _call_node_verifier(proof, public_signals)
