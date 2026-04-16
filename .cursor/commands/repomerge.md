Read `REPO_MERGE_SPEC.md` and execute it exactly.

Process all staged files from `/_repo-ops/_inbox/` deterministically.

Requirements:
- Follow `REPO_MERGE_SPEC.md` as the only authority
- Do not infer behavior from chat history or prior runs
- Do not substitute paths
- Do not repair missing paths
- Route unsafe or unprocessable items to `/_repo-ops/_needs-review/` per spec
- Enforce backup-before-overwrite strictly
- Archive processed files to `/_repo-ops/_processed/` with `DONE_` prefix
- Perform a single commit for the inbox run

Before applying changes:
- Read all files currently in `/_repo-ops/_inbox/`
- Validate filename format
- Sort lexicographically
- Group by destination
- Apply overwrite compaction exactly as specified

After processing:
- Summarize what was applied
- Summarize what was routed to review
- Report the commit created

Do not make any changes outside what `REPO_MERGE_SPEC.md` authorizes.