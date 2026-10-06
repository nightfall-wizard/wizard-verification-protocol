
# WVP Merge-Readiness Checklist

Use this checklist before merging a WVP evidence branch.

## Required local checks

- [ ] Unit tests pass
- [ ] Nightfall verifier passes
- [ ] Codepath binding checker passes
- [ ] Semantic regression checker passes
- [ ] Command probe checker passes
- [ ] Release integrity checker passes
- [ ] Supply invariant checker passes
- [ ] Negative vector checker passes
- [ ] Triage workflow checker passes
- [ ] Conformance score checker passes
- [ ] Release pack checker passes
- [ ] CI hardening checker passes
- [ ] Handoff readiness checker passes

## Required repository checks

- [ ] Pull request opened
- [ ] Required workflow has run
- [ ] Required workflow is green
- [ ] Branch protection settings reviewed
- [ ] Public report is sanitized
- [ ] Release pack hash is current
- [ ] PROJECT-STATE.md is current

## Safety checks

- [ ] No real seed committed
- [ ] No private key committed
- [ ] No wallet file committed
- [ ] No live funds referenced
- [ ] No exploit payload committed
- [ ] No weaponized reproduction steps committed
- [ ] Non-audit language preserved

## Merge boundary

Merge readiness means evidence quality is acceptable for WVP. It does not mean the verified project is safe.
