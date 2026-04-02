# Finance Wizard Agent Instructions

This repository is a structured investing system. Work from files in this repo, not from chat memory.

## Primary Objective

Help maintain a disciplined portfolio process by:

- importing broker data into normalized files
- preserving history over time
- maintaining theses, rules, and signals
- highlighting thesis drift, sizing problems, and broken assumptions

## Working Principles

1. Do not edit raw broker imports.
2. Preserve every import file exactly as received.
3. Treat normalized files as the decision layer.
4. Prefer append-only history files over destructive rewrites when history matters.
5. When a value is unknown, leave it blank or null. Do not invent data.
6. If cost basis is missing, preserve null and flag the row as incomplete.
7. Aggregate duplicate ticker rows unless the repository later adopts lot-level tracking.
8. Use override files for human classification such as virtual portfolio, strategy bucket, thesis linkage, and manual cost basis corrections.

## Current Import Pattern

For Schwab taxable:

- raw imports go in `portfolios/ed-schwab-taxable/imports/`
- normalized current snapshot goes in `portfolios/ed-schwab-taxable/normalized/positions.csv`
- manual classification and overrides go in `portfolios/ed-schwab-taxable/normalized/position-overrides.csv`

## Recommended Import Workflow

When a new broker file arrives:

1. Save the raw file in the appropriate `imports/` folder.
2. Parse the file using the portfolio transformation spec.
3. Generate a current normalized snapshot.
4. Append the snapshot rows to a history file.
5. Generate a delta file by comparing the new snapshot to the previous snapshot.
6. Do not force the user to reprocess old raw files just to answer change-over-time questions.

## Canonical Historical Model

Use this hierarchy:

### 1. Raw imports
Immutable source evidence.

### 2. Snapshot history
Canonical analytical history. Each import run should append rows to a snapshot history file.

### 3. Deltas
Derived convenience output. Useful for review and automation, but not the canonical source of truth.

## Recommendation on History vs Delta

Prefer this design:

- Store a full normalized snapshot for each run
- Append all rows to a history file
- Derive a delta file from the newest snapshot versus the prior snapshot

Do not use deltas as the only history mechanism.

Reason:

- snapshots are easier to audit
- snapshots are easier to rebuild analytics from
- deltas are easy to regenerate
- delta-only designs become brittle quickly

## Files Agents Should Maintain

### Current snapshot
`portfolios/<portfolio_id>/normalized/positions.csv`

### Snapshot history
`portfolios/<portfolio_id>/history/positions_history.csv`

### Latest delta
`portfolios/<portfolio_id>/history/positions_delta_latest.csv`

### Optional dated deltas
`portfolios/<portfolio_id>/history/deltas/YYYY-MM-DD-to-YYYY-MM-DD.csv`

## Expected Delta Semantics

A delta should classify each ticker as one of:

- new
- removed
- increased
- reduced
- unchanged
- metadata_changed

Recommended delta fields:

`from_date,to_date,ticker,change_type,quantity_before,quantity_after,market_value_before,market_value_after,weight_before,weight_after,cost_basis_before,cost_basis_after,notes`

## Virtual Portfolios

A single brokerage account may contain positions belonging to different logical portfolios.

Do not force one account file to equal one investment strategy.

Use `virtual_portfolio` in override and normalized files so the user can classify positions into categories such as:

- core
- growth
- speculative
- metals
- income
- international
- education
- retirement

Default to `untagged` until the user explicitly classifies the position.

## When Using Cursor or VS Code Agents

Agents working locally should:

1. Read `AGENTS.md` first.
2. Read the portfolio-specific transformation spec before changing import code.
3. Show the exact files they plan to update.
4. Prefer deterministic scripts over one-off notebook logic.
5. Avoid destructive edits to historical files.
6. Keep scripts idempotent where possible.
7. When changing a schema, update all related docs and templates in the same commit.

## Near-Term Automation Goal

Today imports are manual. In the future, retrieval may be automated.

Design all import tooling so retrieval and parsing are separate concerns:

- retrieval step gets raw files and stores them
- transform step normalizes them
- history step appends snapshots and computes deltas

This separation will make later automation far easier.
