# WVP-SEC-011 - CI Hardening and Required-Check Gate

This report defines CI hardening controls for WVP Nightfall evidence branches.

Boundary: this is not an audit and does not itself enable GitHub branch protection.

Controls: 12

PASS: 12

WARN: 0

Required workflow: `.github/workflows/wvp-required-checks.yml`

Recommended required check: `WVP Required Checks / required`

## Control summary

| ID | Control | Status | Risk |
|---|---|---|---|
| CI-001 | `least_privilege_permissions` | `PASS` | Overbroad CI token permissions increase supply-chain blast radius. |
| CI-002 | `checkout_credentials_not_persisted` | `PASS` | Persisted credentials can be abused by later steps. |
| CI-003 | `job_timeout_defined` | `PASS` | Missing timeout can allow CI resource exhaustion. |
| CI-004 | `concurrency_defined` | `PASS` | Unbounded concurrent runs waste resources and obscure signal. |
| CI-005 | `unit_tests_required` | `PASS` | Missing test gate allows broken evidence artifacts. |
| CI-006 | `security_checkers_required` | `PASS` | Missing checker steps reduce verification coverage. |
| CI-007 | `release_pack_required` | `PASS` | Evidence bundle can drift from manifest. |
| CI-008 | `ci_hardening_self_check_required` | `PASS` | CI hardening policy can silently regress. |
| CI-009 | `branch_protection_template_exists` | `PASS` | Required checks may not be configured consistently. |
| CI-010 | `required_check_documentation_exists` | `PASS` | Maintainers may not know which check must be required. |
| CI-011 | `non_audit_boundary_preserved` | `PASS` | Evidence checks may be misrepresented as audit certification. |
| CI-012 | `no_secret_or_live_fund_dependency` | `PASS` | CI should remain safe for public forks and pull requests. |

## Safety boundary

- no_real_seed: `True`
- no_private_key: `True`
- no_live_funds: `True`
- no_exploit_payloads: `True`
- no_write_token_required: `True`
- non_audit_boundary_required: `True`

## Non-audit boundary

CI passing means the WVP evidence checks ran successfully. It does not mean Nightfall is safe, audited, certified, or free of vulnerabilities.
