// AGE_OVER_18 circuit (V0.4)
// This circuit proves that: current_ts - dob_ts >= AGE_THRESHOLD
// Implementation notes:
// - Use a safe unsigned comparator via bit decomposition (Num2Bits) to prevent field wraparound.
// - The circuit constrains the difference to be representable in `N_BITS` bits, ensuring non-negativity.
// - dob_ts is private; current_ts, challenge, verification_request_id, claim_id are public.
// - The claim_id is constrained to the expected constant for AGE_OVER_18 to avoid claim-forging.

pragma circom 2.0.0;

include "../node_modules/circomlib/circuits/bitify.circom";

template AgeOver18() {
    // Inputs
    signal input dob_ts; // private
    signal input current_ts; // public
    signal input challenge; // public (field element encoding of nonce)
    signal input verification_request_id; // public (field element encoding)
    signal input claim_id; // public (must equal expected claim identifier)

    // Parameters
    // Use 40 bits for timestamp arithmetic safety (covers many millennia of seconds)
    var N_BITS = 40;
    // threshold: 18 years in seconds (conservative integer)
    var AGE_THRESHOLD = 567648000;
    // claim id constant for AGE_OVER_18
    var CLAIM_AGE_OVER_18 = 1;

    // Compute dob + threshold
    signal dob_plus_thresh;
    dob_plus_thresh <== dob_ts + AGE_THRESHOLD;

    // Compute difference = current_ts - (dob + threshold)
    signal diff;
    diff <== current_ts - dob_plus_thresh;

    // Enforce diff is non-negative and small by representing it in N_BITS bits.
    // If diff is negative, modulo field arithmetic produces a large value that cannot be represented in N_BITS bits,
    // so Num2Bits will fail — this prevents wraparound attacks.
    component diffBits = Num2Bits(N_BITS);
    diffBits.in <== diff;

    // Constrain claim_id to expected constant to avoid claiming arbitrary assertions
    claim_id === CLAIM_AGE_OVER_18;

    // Expose binding public outputs (these will be part of publicSignals)
    signal output out_current_ts;
    signal output out_verification_request_id;
    signal output out_claim_id;
    signal output out_challenge;

    out_current_ts <== current_ts;
    out_verification_request_id <== verification_request_id;
    out_claim_id <== claim_id;
    out_challenge <== challenge;
}

component main = AgeOver18();
