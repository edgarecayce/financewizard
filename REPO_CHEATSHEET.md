# Repo-Ops Cheat Sheet

## What This System Is For

ChatGPT (in the UI) can:
- read repo files
- create new files

But it cannot reliably:
- update existing files
- overwrite files

This system works around that by staging changes for a write-enabled agent (Cursor) to apply.

---

## The Three Roles

### 1) ChatGPT (this chat)
- reads the repo
- creates staging files when changes require updates/overwrites
- follows `REPO_STAGING_SPEC.md`

### 2) Cursor / VS Code
- processes staged files
- applies updates/overwrites
- follows `REPO_MERGE_SPEC.md`

### 3) You
- tell ChatGPT what to change
- tell Cursor to apply it

---

## Basic Workflow

### Step 1 — Ask ChatGPT

Tell ChatGPT what you want to change in the repo.

- If it’s a new file → it can create it directly
- If it requires updating/overwriting → it should stage it using `REPO_STAGING_SPEC.md`

---

### Step 2 — Run Merge in Cursor

In Cursor / VS Code:

Run your slash command:

`/repomerge`

This should:
- read `_repo-ops` staging files
- apply updates to the repo
- move processed files out of staging

---

### Step 3 — Review

- sanity check the changes
- commit if everything looks correct

---

## When To Use Staging

Use staging when:
- updating an existing file
- overwriting content
- making multi-file changes

Do NOT worry about staging for:
- small new files
- simple additions

---

## Rules of Thumb

- If ChatGPT says “I can’t modify files” → it should use staging instead
- If a change feels risky → stage it
- If unsure → stage it

---

## Mental Model

- ChatGPT = planner + stager
- Cursor = executor
- You = control and validation

---

## Goal

Make repo changes safely without relying on direct file overwrite capability in ChatGPT.