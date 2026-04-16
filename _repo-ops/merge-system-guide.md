# Repo-Ops Merge System Guide

## Primary Purpose

This system exists to overcome a limitation in ChatGPT when using the GitHub repository connector:

- ChatGPT can read repository files
- ChatGPT can create new files
- ChatGPT cannot reliably update or overwrite existing files

This subsystem provides a structured way to stage those changes so they can be applied by a write-enabled agent (such as Cursor) or a human.

## Design Goals

- Enable safe updates and overwrites via staging
- Keep operational files self-contained under `_repo-ops/`
- Separate planning, staging, and application of changes
- Avoid silent corrections or hidden assumptions
- Make unsafe or ambiguous changes easy to review

## System Model

This system operates across three roles:

### ChatGPT (Staging Agent)
- Reads the repo
- Creates staging instructions instead of modifying files directly
- Follows `REPO_STAGING_SPEC.md`

### Write-Enabled Agent (Merge Agent)
- Applies staged changes to the repo
- Performs updates, overwrites, and deletes
- Follows `REPO_MERGE_SPEC.md`

### Human Operator
- Initiates changes
- Triggers merge operations
- Validates results

## Core Workflow

1. Request change
2. Detect that direct update/overwrite is not available
3. Create staging artifact under `_repo-ops/`
4. Merge agent applies change
5. Human validates

## Staging Behavior

When a change requires modifying an existing file:

- Do not attempt to describe the change only in chat
- Do not stop at “cannot modify file”
- Create a structured staging file

A staging file should include:
- target file path
- operation type (update / overwrite / delete)
- full intended result or clear patch
- reason for change

## Merge Behavior

The merge agent:

- Reads staging files
- Applies changes exactly as specified
- Avoids introducing additional logic or interpretation
- Routes ambiguous or unsafe changes to review

## Repo Structure

All subsystem operational content should live under `_repo-ops/`:

- inbox
- needs-review
- processed
- overwritten
- system documentation

Root-level files are limited to entry-point specifications:

- `REPO_STAGING_SPEC.md`
- `REPO_MERGE_SPEC.md`
- `REPO_CHEATSHEET.md`

## Portability

This subsystem is designed to be dropped into other repositories with minimal impact:

- do not restructure the host repo
- keep all operational files inside `_repo-ops/`
- avoid assumptions about project structure

## Guiding Principle

This system exists to bridge a capability gap.

All additional structure should serve that goal and not introduce unnecessary complexity.