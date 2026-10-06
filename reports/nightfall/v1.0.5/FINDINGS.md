# Nightfall v1.0.5 WVP Findings

## WVP-NF-INFO-001 - This is not an audit

Severity: Info
Class: process integrity
Status: open by design

This pack is a reproducible verification framework.
It is not a substitute for an independent audit.

## WVP-NF-WARN-001 - Light-client display risk

Severity: Warning
Class: display integrity
Status: documented limitation

A light client can display false information if its node lies.

## WVP-NF-WARN-002 - Release signing outside current proof

Severity: Warning
Class: release integrity
Status: documented limitation

This pack can check release evidence and checksums.
It does not prove code signing or binary reproducibility.
