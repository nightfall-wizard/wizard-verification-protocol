# Reviewer Checklist

Status: Review Operations v1  
Marker: WVP-REVIEW-OPS-V1

## Scope check

Confirm that the PR scope is clear.

The PR should say whether it concerns repository hygiene, maintainer triage evidence, release-candidate evidence, security-invariant evidence, public verification documentation, conformance, or reference implementation behavior.

## Boundary check

Confirm that the PR does not claim:

- Nightfall safety certification,
- cryptographic audit status,
- consensus-correctness proof,
- legal advice,
- custody,
- financial advice,
- investment advice,
- bounty availability,
- token sale,
- guaranteed outcome,
- 100% project completion.

## Verification check

If the PR provides a verification command, run it when practical.

Only report commands actually run.

## Evidence quality check

Look for:

- clear test output,
- deterministic checks,
- linked evidence files,
- fail-closed behavior where applicable,
- explicit limitations,
- reproducible instructions,
- no hidden dependency on private infrastructure.

## Formal review action

If acceptable:

1. Open the PR.
2. Go to Files changed.
3. Click Review changes.
4. Select Approve.
5. Submit the review.

If changes are needed:

1. Use Request changes.
2. State the specific file, line, or claim that needs correction.
3. Avoid broad unrelated feature requests.

If not fully reviewed:

1. Use Comment.
2. State what was and was not checked.
3. Do not imply approval.

## Suggested approval wording

Approved within the stated scope.

I reviewed the changed files and the stated non-goals. I found no claim of Nightfall safety certification, cryptographic audit status, consensus correctness, custody, legal advice, financial advice, investment advice, token sale, bounty, or paid review.

This approval is limited to the stated PR scope.
