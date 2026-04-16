# Merge Instructions

## Purpose

These instructions define how the Merge Agent processes staged files from `/_repo-ops/_inbox/` and applies them to the repository deterministically.

This file is a fully self-contained executable specification.

No behavior may be implied by prior versions.
All behavior must be explicitly defined here.

---

## Instruction Integrity Rule (CRITICAL)

When updating this file:

- do NOT compress behavior by reference
- do NOT state "unchanged"
- ALL behavior must be explicitly restated
- prefer redundancy over ambiguity

---

## High-Level Flow

1. Read ALL staged files in `/_repo-ops/_inbox/`
2. Validate filename format
3. Sort lexicographically
4. Group by destination
5. Apply overwrite compaction
6. Execute actions sequentially per destination
7. Archive staged files
8. Commit once

---

## Spec Path Resolution (CRITICAL)

All paths defined in this specification must be treated as exact and authoritative.

Rules:
- the Merge Agent must use only the paths defined in this specification
- if a required path does not exist, the operation must fail
- the Merge Agent must not attempt to infer, correct, or substitute alternative paths
- no fallback to "real" or discovered paths is allowed
- the Merge Agent must not create, recreate, rename, repair, or auto-correct required paths in order to continue processing
- the Merge Agent must not move files into substitute folders or repair folder names in order to complete a run
- any failure due to missing or invalid paths must route the staged item to `/_repo-ops/_needs-review/`
- if routing to `/_repo-ops/_needs-review/` is itself impossible because that required path is missing or invalid, the Merge Agent must fail without mutating repository state further

This preserves determinism and prevents silent divergence.

---

## Filename Format (STRICT)

`YYYY-MM-DD_HH-MM-SS__NN__<target>__<action>__<description>.md`

- ordering is determined strictly by filename sort
- `NN` resolves ordering within the same second

---

## Overwrite Compaction Rule (CRITICAL)

Within a destination group:

- locate the LAST `overwrite_file`
- discard (do not apply) all earlier staged files for that destination
- apply the overwrite and any later items only

Discarded items must still be archived as DONE.

---

## Execution Rules

For each destination (in order):

Process actions in filename order.

---

## Overwrite Safety Protocol (CRITICAL)

For `overwrite_file` actions, the following order is mandatory and must NOT be violated:

1. Read the current destination file contents
2. Write a backup file to `/_repo-ops/_overwritten/`
3. VERIFY the backup file was successfully written and is readable
4. ONLY AFTER successful backup, apply the overwrite

If ANY step fails:

- DO NOT overwrite the destination file
- route the staged item to `/_repo-ops/_needs-review/`
- record a clear failure reason

It is strictly forbidden to:

- overwrite before backup
- attempt to "fix" backup after overwrite
- proceed if backup verification fails

This is a hard safety boundary.

---

## YAML Handling

- strip YAML front matter
- apply only markdown body

---

## Action Handling

Apply actions exactly as specified:

- append
- prepend
- append_section
- replace
- replace_in_section
- replace_section
- insert_after
- overwrite_file
- review

All matching rules must be exact and case-sensitive.

---

## Review Routing

If an action cannot be safely applied:

- move to `/_repo-ops/_needs-review/`
- do NOT partially apply

---

## Archiving

After processing:

- move processed items to `/_repo-ops/_processed/` with DONE_ prefix
- move review items to `/_repo-ops/_needs-review/`

---

## Backup Storage

All overwrite backups must be stored in:

`/_repo-ops/_overwritten/`

Format:

`<filename>_<timestamp>.bak`

---

## Commit Rules

- perform a single commit per inbox run
- include all file changes, archives, and backups

---

## Summary

The Merge Agent must:

- follow filename ordering exactly
- enforce overwrite compaction
- enforce backup-before-overwrite strictly
- never apply unsafe operations
- enforce strict adherence to spec-defined paths
- remain deterministic and non-interpretive

## Destination Resolution Clarification (ADDITION)

- Filename validation is strictly structural and must pass before processing
- The `<target>` field in the filename is NOT used for path resolution
- The YAML `destination` field is the ONLY source of truth for file paths

The merge agent must:
- validate filename format first
- then use YAML `destination` for grouping and execution

The merge agent must NOT:
- infer destination from filename
- reconstruct paths from filename