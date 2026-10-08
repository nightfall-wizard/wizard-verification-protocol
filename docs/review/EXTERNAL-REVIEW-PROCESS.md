# External Review Process

Status: Review Operations v1  
Marker: WVP-REVIEW-OPS-V1

## Purpose

Wizard Verification Protocol uses external review gates for repository hygiene, maintainer triage, and release-candidate evidence.

The purpose of this process is to make external review repeatable, unpaid, bounded, and clear.

## Core rule

A review only satisfies protected-branch review policy when it is submitted as a formal GitHub pull request review.

Issue comments, PR comments, reactions, and informal confirmations may be useful evidence, but they are not the same as formal GitHub PR approval.

## Required reviewer action

A reviewer should:

1. Open the relevant pull request.
2. Review the changed files.
3. Open Files changed.
4. Select Review changes.
5. Choose Approve, Comment, or Request changes.
6. Submit the review.

## Acceptable evidence

Acceptable review evidence includes:

- formal GitHub PR approval,
- formal GitHub PR comment review,
- formal GitHub request-changes review,
- reproducible local verification output,
- clearly scoped public issue comment,
- specific defect report with file or line reference.

## Not sufficient by itself

The following are not sufficient by themselves for protected-branch approval:

- issue-only comment,
- PR conversation comment without formal review,
- emoji reaction,
- verbal confirmation outside GitHub,
- self-approval by the maintainer,
- admin merge,
- private message.

## Maintainer rules

The maintainer should:

- preserve branch protection,
- avoid admin bypass,
- avoid self-approval as independent review,
- respond to defects with a focused fix,
- keep review scope narrow,
- avoid unrelated feature work while a review gate is open,
- document completion after merge.

## Boundary

This process does not claim:

- WVP is externally audited,
- Nightfall is safe,
- Nightfall consensus is correct,
- any wallet, bounty, payment, or custody flow is endorsed,
- any asset has market value,
- any investment decision is recommended,
- the project is 100% complete.

## Completion condition

A review-gated PR is complete only when:

1. required checks are green,
2. formal GitHub PR review requirements are satisfied,
3. branch protection is respected,
4. merge occurs without admin bypass,
5. completion evidence is documented,
6. related review issues are closed or updated.
