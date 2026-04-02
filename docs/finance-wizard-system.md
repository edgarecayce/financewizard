# Finance Wizard System

This repository is the source of truth for a disciplined investing system.

## Objectives

- Track multiple portfolios across custodians and account types
- Preserve raw broker exports by date
- Normalize holdings into structured position files
- Maintain written investment theses
- Define portfolio-specific rules and signals
- Record decisions so actions can be audited against prior reasoning

## Repository Design

Each portfolio gets its own folder under `/portfolios/<portfolio_id>/`.

That folder contains:

- `imports/` for dated raw CSV exports from Schwab or Fidelity
- `normalized/` for cleaned position data we can analyze consistently
- `thesis/` for portfolio-specific thesis files
- `rules/` for portfolio-specific discipline and sizing rules
- `signals/` for monitoring triggers
- `notes/` for decision logs

## Working Rules

1. Raw broker exports are preserved as received.
2. Normalized files are the analytical layer.
3. Every meaningful position should map to a thesis file.
4. Position sizing should reflect conviction and risk.
5. Sell decisions should reference what changed in the thesis.
