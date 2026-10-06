
# WVP Required-Check Gate Method

This document defines the required-check gate for WVP branches.

## Required check

Use this required check for protected branches:

`WVP Required Checks / required`

## Recommended GitHub settings

Enable branch protection on `main`.

Recommended settings:

- require a pull request before merging
- require status checks to pass before merging
- require branches to be up to date before merging
- require the check `WVP Required Checks / required`
- block force pushes
- block deletions

## Manual setup note

This repository can document the required gate, but local Termux scripts cannot guarantee GitHub branch protection is actually enabled unless GitHub settings are changed with sufficient repository permissions.

## Boundary

The required-check gate protects evidence quality. It is not an audit and not proof that any verified project is safe.
