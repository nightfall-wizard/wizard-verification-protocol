# Maintainer Response Protocol

Status: Review Operations v1  
Marker: WVP-REVIEW-OPS-V1

## Issue comment only

Treat it as useful evidence, but not as protected-branch approval.

Do not merge solely because of an issue comment.

## PR approval

Before merge:

- confirm required checks are green,
- confirm branch protection is active,
- confirm the approval is formal GitHub PR approval,
- confirm no unresolved requested changes remain,
- confirm the PR scope has not drifted.

Then:

- use normal protected merge or auto-merge,
- do not use admin bypass,
- document completion after merge.

## Request changes

If a reviewer requests changes:

- do not merge,
- fix only the scoped defect,
- avoid unrelated feature changes,
- rerun checks,
- comment with a concise defect-resolution summary,
- request re-review.

## Out-of-scope concern

If a reviewer identifies an out-of-scope concern:

- acknowledge the concern,
- state whether it is in scope,
- open a separate issue if useful,
- do not expand the active PR into a broad rewrite.

## Financial or bounty language

If a review includes financial, bounty, token, wallet, or investment language:

- do not accept payment,
- do not offer bounty,
- do not discuss token allocation,
- do not request wallet activity,
- do not provide investment claims,
- restate that the project is unpaid, non-custodial, and not financial advice.

## Completion evidence after merge

After a reviewed PR is merged, document:

- PR number,
- merge time,
- merge commit,
- checks status,
- review decision,
- whether branch protection was respected,
- whether admin bypass was avoided,
- exact boundary of the merged change.

## Prohibited shortcuts

Do not use:

- self-approval as independent review,
- admin merge to bypass missing approval,
- private-message-only review,
- paid approval,
- bounty-for-approval,
- token-based incentive,
- inflated audit wording,
- 100% completion claim without external evidence.
