# AUNEYA Provable Web Scope

## Purpose

This document defines the initial scope of the provable web for AUNEYA.

AUNEYA does not claim absolute truth.

AUNEYA verifies specific public digital claims.

## Core Boundary

AUNEYA may verify public or lawfully accessible digital reality.

AUNEYA must not verify private, hacked, unlawfully accessed or access-controlled data.

## Claim Status Values

A claim may be classified as:

- verified
- false
- unverifiable
- stale
- dangerous
- conflicting

## Initial Claim Types

### 001 — Release Reality

Checks whether a public software release exists and whether its expected metadata and assets are present.

### 002 — Build Provenance

Checks whether build evidence exists and what it can and cannot prove.

### 003 — Download Integrity

Checks whether a public download is reachable and whether hashes or signatures match.

### 004 — Website Claim Reality

Checks whether a public webpage made or still makes a specific claim.

### 005 — Domain / DNS / TLS Reality

Checks public domain, DNS and TLS state.

### 006 — Audit Claim Reality

Checks whether a claimed public audit exists and what it covers.

### 007 — Blockchain Claim Reality

Checks public blockchain-related claims, such as verified contracts, supply claims, burns or token distribution evidence.

### 008 — App Store Reality

Checks public app-store metadata, publisher identity and version claims.

### 009 — AI Model Reality

Checks public AI model files, versions, hashes and origin evidence.

### 010 — Media / File Origin Reality

Checks public file metadata, origin evidence and integrity signals.

## Expiry Principle

Digital reality expires.

Evidence must be rechecked.

Example expiry windows:

- wallet download: 24 hours
- website claim: 6 to 24 hours
- release metadata: 7 days
- audit claim: 30 days
- supply claim: until new commit, release or contract change
- AI model claim: until new model version
- domain / TLS claim: time-window or state-change based

## Safety Rule

If a claim cannot be checked lawfully, it is out of scope.
