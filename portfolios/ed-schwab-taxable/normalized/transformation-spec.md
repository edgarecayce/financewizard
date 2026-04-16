# Schwab Positions CSV → Normalized Transformation Spec

## Recommendation
Use aggregated (ticker-level) normalization. Ignore lot-level distinctions.

---

## Source

Input file:

`imports/*.csv`

Example:

`EC Main-Positions-2026-04-01-202522.csv`

---

## Transformation Rules

### 1. Skip Non-Data Rows

Ignore:

- First metadata line
- Blank lines
- Summary rows ("Positions Total")

---

### 2. Column Mapping

| Schwab Column | Normalized Field |
|--------------|-----------------|
| Symbol | ticker |
| Description | security_name |
| Qty (Quantity) | quantity |
| Price | price |
| Mkt Val (Market Value) | market_value |
| Cost Basis | cost_basis |
| % of Acct (% of Account) | weight_pct |
| Asset Type | asset_type |

---

### 3. Data Cleaning

Apply:

- Remove `$` and `,` from numeric fields
- Convert percentages by removing `%`
- Treat "N/A" and "Incomplete" as NULL

---

### 4. Row Filtering

Exclude:

- Asset Type = Cash and Money Market
- Asset Type = Option

Keep:

- Equity
- ETFs & Closed End Funds

---

### 5. Aggregation (Key Rule)

Group by:

`ticker`

Aggregate:

- quantity → SUM
- market_value → SUM
- cost_basis → SUM (ignore NULLs; if all NULL → NULL)
- weight_pct → SUM

Security name:

- Take first non-null value

Asset type:

- Take first value

---

### 6. Derived Fields

- unrealized_gain = market_value - cost_basis (if cost_basis present)

---

### 7. Output Schema

Write to:

`normalized/positions.csv`

Columns:

as_of_date,ticker,security_name,asset_type,total_quantity,total_market_value,total_cost_basis,unrealized_gain,weight_pct,strategy_bucket,thesis_id,target_weight_pct,status,notes

---

## Manual Overrides

### Cost Basis

If missing:

- Leave NULL
- status = "incomplete"

User may manually backfill later.

---

## Philosophy

- Broker data is raw input, not truth
- Normalized file is the decision layer
- Simplicity > perfect accounting

We intentionally ignore lot complexity to keep system usable.

---

## Future Enhancements

- Add lot-level tracking if needed
- Add options handling separately
- Add cash tracking separately

