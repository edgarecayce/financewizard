# History Model

## Recommendation

Use `normalized/positions.csv` as the current working snapshot.

That file is overwritten on each successful import run.

Use `history/positions_history.csv` as the append-only historical record.

Use `history/positions_delta_latest.csv` as the latest derived change report.

Optional dated delta files may also be written under `history/deltas/`.

---

## Lifecycle Per Import Run

1. Save raw broker CSV into `imports/`
2. Transform raw CSV into `normalized/positions.csv`
3. Append the transformed rows to `history/positions_history.csv`
4. Compare new snapshot to prior snapshot
5. Write `history/positions_delta_latest.csv`
6. Optionally write a dated delta file

---

## Canonical Roles

### Current working file
`normalized/positions.csv`

Purpose:
- latest usable portfolio state
- file used by downstream thesis and review workflows

Behavior:
- replaced on each run
- does not preserve prior rows once superseded

### Historical snapshot file
`history/positions_history.csv`

Purpose:
- append-only time series of normalized snapshots
- source for trend analysis and reconstruction

Behavior:
- new rows appended on each run
- never rewritten except for explicit repair

### Delta file
`history/positions_delta_latest.csv`

Purpose:
- fastest way to review what changed since prior import

Behavior:
- regenerated on each run
- convenience layer, not canonical history

---

## Important Rule

Do not rely on delta files as the only evidence of prior state.

Snapshots are the source of truth for historical analysis.

---

## Agent Guidance

Any local coding agent working in Cursor or VS Code should preserve this model exactly unless the schema is intentionally revised across the repo.
