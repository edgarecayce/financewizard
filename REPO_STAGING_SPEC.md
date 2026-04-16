# Agent Staging Instructions

## Purpose

These instructions define how Agent prepares repository updates using a staging workflow.

These instructions are a fully self-contained executable specification.

No behavior may be implied by reference to prior versions.
All behavior must be explicitly defined in this file.

Agent must:
- inspect the repo
- verify file existence from the repo before deciding how to write
- reason from the effective working state
- decide whether to create directly or stage into `/_repo-ops/_inbox/`
- generate precise, deterministic staged files

Agent must NOT edit existing files directly.

---

## Instruction Integrity Rule (CRITICAL)

When updating this file:

- do NOT compress behavior by reference to prior versions
- do NOT state that behavior is unchanged from a previous version instead of restating it
- ALL behavior must be explicitly restated
- prefer redundancy over ambiguity
- this file must always remain fully self-contained

Violation of this rule introduces system risk.

---

## Core Model

This system separates:
- planning + staging by Agent
- deterministic execution + merge by a desktop agent

Agent prepares intent.
The merge agent applies it.

---

## First Step: Inspect the Repo (MANDATORY)

Before proposing or creating ANY change, Agent must:

1. Inspect repository structure and file existence at target paths
2. Verify from the repo whether the destination file exists
3. Identify relevant sections if the change is section-scoped
4. Check for staged files in `/_repo-ops/_inbox/` that affect the same destination
5. Reason from the effective working state before deciding the next action

Do not guess.
Do not assume file existence.
Do not assume section names are unique.
Always inspect first.

---

## File Existence Rule (CRITICAL)

Before creating a plan, before staging, and before deciding on direct creation, Agent must verify from the repo whether the destination file already exists.

Rules:
- Agent must check the actual repo state
- Agent must not infer file existence from memory, prior chat context, or naming assumptions
- Agent must not attempt to stage an append, replace, replace_in_section, replace_section, insert_after, prepend, or overwrite_file change against a destination unless repo inspection confirms the destination already exists
- if the destination does not exist, Agent must treat the file as new and write it directly at the destination path rather than staging a change against a non-existent file

This rule is mandatory and applies even when the requested change seems obvious.

---

## Effective Working State (CRITICAL)

When reasoning about a file, Agent must consider:

- the current repo version of the file
- plus all staged files in `/_repo-ops/_inbox/` whose `destination` points to that file

Agent must reason from this effective working state, not just from the repo file.

This prevents future chats from planning against stale state when inbox items exist but have not yet been merged.

---

## Overwrite Checkpoint Rule (CRITICAL)

If a staged file for a destination uses:

- `action: overwrite_file`

then that staged overwrite acts as a checkpoint.

For effective-state reasoning:

- all earlier staged files for that same destination are superseded
- only:
  - the last overwrite for that destination
  - and any later staged files for that destination
  remain active

Implication:

If a file has older append, replace, or section edits in `/_repo-ops/_inbox/`, and then a later `overwrite_file` for the same destination exists, Agent must ignore the earlier staged edits for reasoning purposes.

---

## Decision Rule

### If the destination file does NOT exist

Create the file directly at the destination path.

This is allowed for truly new files.

Agent must reach this decision only after verifying from the repo that the destination does not exist.

### If the destination file DOES exist

Do NOT modify it directly.

Instead:
- create a staged file in `/_repo-ops/_inbox/`

Agent must reach this decision only after verifying from the repo that the destination does exist.

---

## Direct Create and Subsequent Staged Operations

If Agent creates a new file directly because the destination does not exist, that newly created file becomes the base state for any later staged operations targeting that same destination.

Agent must not treat the file as absent after direct creation has already occurred.

When later reasoning about staged operations for that destination, Agent must use the created file plus any applicable staged files as the effective working state.

---

## Operating Mode

### Step 1 — Plan (ALWAYS)

When the user gives a command that implies repo changes, Agent must first respond with a SHORT plan.

The plan should briefly list, for each intended change:
- target file
- action type
- high-level summary

Example plan format:

    Planned updates:

    1) /docs/decisions.md
    - append_section -> ## Decision Log
    - add the newly agreed decision

    2) /docs/current-status.md
    - replace_in_section -> ## Current State
    - update status text to reflect what we learned

Requirements:
- keep it short
- do not write pages of explanation
- do not silently stage changes for vague commands
- wait for explicit approval before staging

### Step 2 — Stage (AFTER APPROVAL)

After approval:
- create one staged file per change
- place each staged file in `/_repo-ops/_inbox/`
- follow filename and metadata rules exactly
- ensure the staged instruction is deterministic and non-interpretive

---

## Staging Folder

All staged files go in:

`/_repo-ops/_inbox/`

Do not stage files anywhere else.

---

## Filename Format (STRICT)

Use this format:

`YYYY-MM-DD_HH-MM-SS__NN__<target>__<action>__<description>.md`

Rules:
- use double underscore `__` as the structural delimiter
- include real time down to the second
- include a zero-padded sequence number `NN`
- sequence number is required when multiple staged files are created in the same second
- within a single second, sequence number defines intended execution order
- if the second changes, sequence resets to `01`
- do not use underscore-only structural naming
- `<target>` should be a short identifier for the destination file
- `<action>` should be the exact action name
- `<description>` should be a short human-readable summary
- keep the filename boring, stable, and readable

Ordering rule:
- filename order is execution order
- Agent must assign timestamps and per-second sequence values so lexicographic sort preserves intended processing order
- when multiple changes in a batch affect the same destination, Agent must ensure the filenames encode the intended order explicitly

Example:

`2026-04-08_17-12-03__01__readme__append__marker-1.md`

`2026-04-08_17-12-03__02__readme__overwrite_file__checkpoint-reset.md`

`2026-04-08_17-12-03__03__readme__append__post-overwrite-marker.md`

---

## Required Front Matter

Every staged file must begin with YAML front matter containing the fields needed for deterministic merge.

Use this shape:

    ---
    id: <unique-id>
    created: YYYY-MM-DD HH:MM:SS
    source: agent-chat
    destination: /path/to/file.md
    action: <action>

    section: optional exact header text
    section_path: optional ordered header path list

    find: optional exact text to find
    replace_with: optional replacement text
    after: optional exact anchor text

    confirm_overwrite: optional boolean
    reason: optional explanation for overwrite choice

    topic: short description
    review_note: optional explanation if action is review
    ---

Rules:
- include only fields that are relevant
- keep values precise
- do not include narrative outside the markdown body
- the markdown body is the content to be applied

---

## Action Definitions (STRICT)

All actions except direct file creation require the destination file to already exist in the repository.

### append

Append content to the END of the file.

Use when:
- adding a new section at file level
- adding file-level notes at the end
- the operation is intentionally not section-scoped

Do not use when:
- the change should be applied inside a specific section

---

### prepend

Insert content at the BEGINNING of the file.

Use when:
- content belongs at top-of-file scope
- the file should start with the new block

---

### append_section

Append content INSIDE a section.

Required targeting:
- `section` or `section_path`

Behavior:
- locate the section
- interpret the section using section semantics defined below
- append the new content at the end of that section

Placeholder cleanup rule:
If the target section contains only placeholder bullets such as:
- `- `
- `* `
- `1. `

then those placeholders should be treated as scaffolding and replaced by the real appended content rather than preserved.

Use when:
- adding new bullets, paragraphs, or subsections inside a known section

---

### replace

Replace ALL exact matches in the ENTIRE file.

Required fields:
- `find`
- `replace_with`

Rules:
- exact match only
- case-sensitive
- replace all occurrences in the full file

Use when:
- the replacement is intentionally global for the file

Do not use when:
- the replacement should be limited to one section
- section scoping matters

In those cases, use `replace_in_section`.

---

### replace_in_section

Replace text only WITHIN a specific section.

Required fields:
- `section` or `section_path`
- `find`
- `replace_with`

Rules:
- exact match only
- case-sensitive
- only replace within the bounds of the targeted section

Use when:
- the same text may appear elsewhere in the file
- the change must be scoped safely to one section

If the section name is ambiguous:
- use `section_path`
- or fall back to `review`

---

### replace_section

Replace an ENTIRE section, including its nested subsections.

Required fields:
- `section` or `section_path`

Rules:
- the targeted section must resolve exactly
- the replacement body must include the header for the section being replaced
- the replacement replaces the whole section block, not just lines within it

Use when:
- the section is being rewritten as a unit
- nested content must be replaced together

---

### insert_after

Insert content after a unique anchor string.

Required fields:
- `after`

Rules:
- the anchor text must match exactly
- the anchor must resolve exactly once

If:
- zero matches are found -> use `review`
- multiple matches are found -> use `review`

Use when:
- the file structure is best addressed by a literal anchor rather than header targeting

---

### overwrite_file

Replace the entire file contents.

Required fields:
- `confirm_overwrite: true`
- `reason`

Use rarely.

Preferred use cases:
- the change is effectively a rewrite
- the file is small
- a clean checkpoint is more valuable than replaying many deltas
- the rewrite is clearer and safer than composing multiple staged edits

Heuristic:
- prefer scoped edits when multiple staged changes need to compose in the same file
- prefer `overwrite_file` when the file is being substantially rewritten and checkpoint behavior is desirable

Critical meaning:
- this acts as a checkpoint for effective-state reasoning
- earlier staged files for the same destination are superseded by the last overwrite

---

### review

Do NOT merge automatically.

Use when:
- the target is ambiguous
- multiple matches exist
- section targeting cannot be resolved safely
- the anchor is not unique
- staged state is conflicting
- Agent is uncertain about correct placement

Purpose:
- preserve safety by explicitly routing uncertain changes to manual review rather than improvising

---

## Section Targeting Rules

### section

`section` means an exact markdown header text match.

Rules:
- must match the full header text exactly
- matching is case-sensitive
- it is only safe if it resolves to exactly ONE section in the file

If the same header text appears in multiple places:
- do not guess
- use `section_path`
- or use `review`

Example of ambiguity:
A file may contain multiple `## Justification` sections under different parents.

In that case, plain `section: "## Justification"` is not safe by itself.

---

### section_path (PREFERRED WHEN NEEDED)

`section_path` is an ordered path of headers from parent to child.

Example shape:

    section_path:
      - "# Decisions"
      - "## Justification"

Rules:
- resolve step-by-step
- each path level must match exactly one section under the current parent scope
- if any level fails or is ambiguous, do not guess
- use `review` if uniqueness cannot be established

Use `section_path` when:
- duplicate section names exist
- there is any risk that plain `section` is not unique
- precision matters more than brevity

---

## Section Semantics (STRICT)

A section includes:
- its own header
- all content beneath it
- all nested subsections
- until the next header of equal or higher level

This section definition applies to:
- `append_section`
- `replace_in_section`
- `replace_section`

Do not treat a section as only the lines immediately below its header.
Nested subsections are part of the parent section until a header of equal or higher level begins a new section boundary.

---

## Exact Matching Rules (STRICT)

For all text-matching operations:
- matching must be exact
- matching must be case-sensitive
- no fuzzy matching
- no best-guess substitutions
- no semantic reinterpretation of anchors or search strings

This applies to:
- `replace`
- `replace_in_section`
- `insert_after`
- section header matching
- section path resolution

If an exact match cannot be established safely:
- use `review`

---

## Content Rules

The markdown body of the staged file must:
- contain only the content to be applied
- be valid markdown
- preserve intentional formatting
- allow headings, bullets, tables, and code blocks if needed
- include the full replacement structure when replacing a section or whole file

Do not:
- add explanatory prose for the merge agent
- mix instructions into the markdown body
- include commentary that belongs in the YAML instead of the content

---

## Behavior Rules

Agent must:
- always inspect the repo first
- always verify destination file existence from the repo before deciding between direct create and staged update
- always check staged inbox files affecting the same destination
- reason from the effective working state
- decide correctly between direct create and staged update
- provide a short plan before staging
- wait for approval
- create one staged file per change
- assign filename timestamps and sequence values so intended execution order is explicit
- prefer scoped operations when possible
- use `review` when uncertainty exists
- preserve precision rather than over-simplify

Agent must NOT:
- directly edit existing files
- stage changes against a non-existent destination when the file should be created directly instead
- silently stage vague commands without approval
- ignore pending staged state
- weaken exact-match rules
- guess at ambiguous targets
- compress instructions at the cost of losing operational precision
- create same-second filenames without a sequence rule that preserves ordering intent

---

## Examples

### Example: replace text globally in a file

Front matter:

    action: replace
    destination: /README.md
    find: Hello Sailor!
    replace_with: Greetings Fellow Kids

Meaning:
- replace every exact, case-sensitive occurrence of `Hello Sailor!` in `/README.md`

### Example: replace text only within a section

Front matter:

    action: replace_in_section
    destination: /docs/current-status.md
    section_path:
      - "# Status"
      - "## Current State"
    find: old wording
    replace_with: new wording

Meaning:
- replace only the exact matches inside the resolved section

### Example: append to a section

Front matter:

    action: append_section
    destination: /docs/decisions.md
    section: "## Decision Log"

Meaning:
- resolve the `## Decision Log` section
- remove placeholder bullets first if the section only contains placeholders
- append the staged markdown body inside that section

### Example: overwrite a file

Front matter:

    action: overwrite_file
    destination: /REPO_STAGING_SPEC.md
    confirm_overwrite: true
    reason: restore full explicit instructions and checkpoint the file cleanly

Meaning:
- replace the file contents entirely
- future effective-state reasoning should treat this overwrite as the active checkpoint for that destination

---

## Summary

The rules are:

- inspect the repo first
- verify destination file existence from the repo before deciding direct create vs staged update
- check inbox state before planning
- reason from the effective working state
- last overwrite acts as a checkpoint
- new file -> create directly
- existing file -> stage in `/_repo-ops/_inbox/`
- a directly created file becomes base state for later staged operations targeting that destination
- always give a short plan before staging
- wait for approval
- use deterministic action types
- encode execution order in filenames using second-level time plus per-second sequence
- keep replace logic exact and case-sensitive
- treat section boundaries strictly
- use `section_path` or `review` when ambiguity exists
- preserve precision over simplification

## Filename Target Rules (ADDITION)

The `<target>` portion of the staged filename must follow these rules:

- MUST be a short identifier
- MUST NOT contain `/`
- MUST NOT contain `__`
- MUST NOT attempt to encode full file paths

The actual file path MUST be defined only in YAML:

    destination: /full/path/to/file.md

The filename exists only for:
- ordering
- grouping
- human readability

It is NOT a source of truth for path resolution.