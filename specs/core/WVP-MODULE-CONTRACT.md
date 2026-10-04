# WVP Module Contract

## Required CLI Behavior

Every WVP reference tool must support:

- help output
- target input
- machine-readable JSON output
- explicit limitations
- non-zero exit code on invalid usage

## Required JSON Fields

- tool
- version
- target
- status
- classification
- summary
- limitations

## Required Engineering Rules

- deterministic output where possible
- no false security claims
- no secret access
- reproducible command for every reportable claim
- explicit out_of_scope labeling
