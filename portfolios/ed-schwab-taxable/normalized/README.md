# Normalization Workflow (Schwab)

## Recommendation
Run the transformer after each CSV export. Do not edit raw imports.

---

## Steps

1. Export CSV from Schwab
2. Drop into `imports/`
3. Run:

```
python tools/transform_schwab_positions.py --portfolio ed-schwab-taxable
```

4. Review `normalized/positions.csv`

---

## Overrides (Important)

Use `position-overrides.csv` to:

- Assign virtual portfolios
- Set strategy buckets
- Attach thesis IDs
- Override cost basis when missing

---

## Philosophy

- Raw data = immutable input
- Normalized data = decision layer
- Overrides = controlled human input

---

## Status Values

- `untagged` → default, needs classification
- `incomplete` → missing critical data (cost basis, etc)
- custom values allowed via override

---

## Key Rule

No position should remain `untagged` long-term.

This is how discipline is enforced.
