# AUNEYA Legal Review Gates

## Purpose

This document prevents AUNEYA from moving from research language into regulated or value-sensitive activity without explicit review.

## Gate 0 — Research-only baseline

Allowed:

- architecture documents;
- threat models;
- non-value simulation;
- boundary guards;
- toy models without real users, funds, wallets, tokens, or rewards.

Status: allowed.

## Gate 1 — Prohibited until legal review

The following are blocked until qualified Germany/EU legal review:

- token;
- sale;
- public offer;
- transferability;
- listing;
- market value;
- reward;
- yield;
- return;
- profit;
- staking;
- mining reward;
- wallet;
- custody;
- payment;
- exchange;
- brokerage;
- investment;
- advisory service;
- portfolio management;
- user funds;
- private-key handling;
- production witness network with economic meaning.

## Gate 2 — Required review record

Before any blocked item is introduced, the repository must contain a review record stating:

- what is changing;
- what jurisdiction was reviewed;
- what activity remains prohibited;
- what language is allowed;
- what language remains blocked;
- what implementation is allowed;
- what implementation remains blocked.

## Gate 3 — Implementation blocker

No code may implement token, value, wallet, custody, transfer, reward, sale, staking, yield, payment, exchange, or user-fund behavior before the legal review record exists.

## Gate 4 — Public communication blocker

No README, issue, PR, release note, website text, social text, or documentation may imply token, value, return, profit, launch, listing, reward, custody, payment, or financial-service activity before legal review.

## Final rule

When uncertain, AUNEYA must stay research-only.
