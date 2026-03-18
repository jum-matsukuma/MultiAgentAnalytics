---
name: sync-template
description: Sync updates from the template repository into a derived project. Fetches only changes since the last sync, preserves project-specific customizations, and handles conflicts interactively. Use when you want to pull latest template improvements (skills, agents, configs) into your project.
user-invocable: true
argument-hint: "[template-repo-url (optional if already configured)]"
---

# Sync Template Repository

Pull updates from the upstream template repository into a derived project while preserving project-specific customizations.

## Prerequisites

- The derived project was created via GitHub's "Use this template"
- `gh` CLI is available and authenticated
- Working tree is clean (no uncommitted changes)

## Configuration File

This skill uses `.template-sync.json` at the project root to track sync state:

```json
{
  "templateRemote": "template",
  "templateUrl": "https://github.com/owner/template-repo.git",
  "templateBranch": "main",
  "lastSyncCommit": "abc1234...",
  "lastSyncDate": "2026-03-18T00:00:00Z",
  "protectedPaths": [
    "README.md",
    "package.json",
    "pyproject.toml",
    "CLAUDE.md"
  ]
}
```

### Field descriptions

| Field | Description |
|-------|-------------|
| `templateRemote` | Git remote name for the template repo (default: `template`) |
| `templateUrl` | Template repository URL |
| `templateBranch` | Branch to sync from (default: `main`) |
| `lastSyncCommit` | Last synced commit hash from the template (used to fetch only newer changes) |
| `lastSyncDate` | Timestamp of last sync |
| `protectedPaths` | Files/directories that should not be overwritten (project-specific customizations) |

## Workflow

Follow these steps in order:

### Step 1: Pre-flight checks

1. Verify the working tree is clean:
   ```bash
   git status --porcelain
   ```
   If dirty, warn the user and stop.

2. Check if `.template-sync.json` exists:
   - **Exists**: Read config and proceed to Step 3
   - **Does not exist**: Proceed to Step 2 (first-time setup)

### Step 2: First-time setup

Only runs when `.template-sync.json` does not exist.

1. Determine the template URL:
   - If provided as an argument, use it
   - Otherwise, ask the user for the template repository URL

2. Add the template as a git remote:
   ```bash
   git remote add template <url>
   ```

3. Fetch the template:
   ```bash
   git fetch template
   ```

4. Identify files that the project has already modified (these are likely project-specific):
   ```bash
   # Get the initial commit (template snapshot) and compare with current HEAD
   # Files modified by the project should be protected by default
   git diff --name-only $(git rev-list --max-parents=0 HEAD) HEAD
   ```

5. Create `.template-sync.json` with:
   - `templateUrl`: the URL provided
   - `templateRemote`: "template"
   - `templateBranch`: "main"
   - `lastSyncCommit`: the latest commit hash on `template/main`
   - `lastSyncDate`: current timestamp
   - `protectedPaths`: files identified in step 4 (present to user for confirmation)

6. Commit `.template-sync.json` and inform the user that initial setup is complete.
   - On first-time setup, do NOT merge any changes yet. The baseline is established. The next run will pick up new changes.

### Step 3: Fetch and identify new changes

1. Fetch latest from template:
   ```bash
   git fetch template
   ```

2. Read `lastSyncCommit` from `.template-sync.json`

3. Get the list of new commits since last sync:
   ```bash
   git log --oneline <lastSyncCommit>..template/<branch>
   ```

4. If no new commits, inform the user and stop.

5. Get the list of changed files:
   ```bash
   git diff --name-only <lastSyncCommit> template/<branch>
   ```

6. Categorize files:
   - **Safe to update**: Files NOT in `protectedPaths` and NOT modified by the project
   - **Protected (changed in template)**: Files in `protectedPaths` that have template updates
   - **Conflict risk**: Files modified by BOTH project and template since last sync

### Step 4: Display change summary

Present a table to the user:

```
## Template Updates Available

Commits since last sync (<lastSyncDate>):
- abc1234 feat: add new skill
- def5678 fix: improve statusline

### Files to update

| File | Status | Action |
|------|--------|--------|
| .claude/skills/new/SKILL.md | New file | Auto-apply |
| .claude/agents/team-lead.md | Template only | Auto-apply |
| CLAUDE.md | Protected | Skip (show diff) |
| .claude/settings.json | Both modified | Manual review needed |
```

### Step 5: Apply updates

Create a new branch for the sync:
```bash
git checkout -b sync/template-<date>
```

#### For safe files (auto-apply):
```bash
git checkout template/<branch> -- <file>
```

#### For protected files:
- Show the diff between `lastSyncCommit` and `template/<branch>` for each protected file:
  ```bash
  git diff <lastSyncCommit> template/<branch> -- <file>
  ```
- Ask the user if they want to:
  1. **Skip** - Keep project version as-is
  2. **Apply** - Overwrite with template version
  3. **Merge** - Attempt a three-way merge, then review conflicts manually

#### For conflict-risk files:
- Attempt three-way merge using the last sync point as base:
  ```bash
  TMPDIR=$(mktemp -d)
  trap 'rm -rf "$TMPDIR"' EXIT
  git show <lastSyncCommit>:<file> > "$TMPDIR/base"
  git show template/<branch>:<file> > "$TMPDIR/theirs"
  git merge-file <file> "$TMPDIR/base" "$TMPDIR/theirs"
  ```
- If merge succeeds cleanly, auto-apply
- If conflicts remain, show them to the user for manual resolution

### Step 6: Commit and update sync state

1. Stage all applied changes:
   ```bash
   git add -A
   ```

2. Update `.template-sync.json`:
   - `lastSyncCommit`: latest commit hash on `template/<branch>`
   - `lastSyncDate`: current timestamp

3. Commit:
   ```
   chore: sync template updates from <lastSyncCommit-short>..<newCommit-short>

   Applied N file(s), skipped M protected file(s)
   ```

4. Present the result and suggest next steps:
   - Review the changes: `git diff main..sync/template-<date>`
   - Merge to main when satisfied: `git checkout main && git merge sync/template-<date>`
   - Or create a PR: `gh pr create`

### Step 7: Report

```
## Sync Complete

- Commits synced: N
- Files updated: X
- Files skipped (protected): Y
- Files with conflicts resolved: Z
- Branch: sync/template-<date>

Next steps:
1. Review changes: git diff main
2. Run tests to verify nothing is broken
3. Merge or create PR when ready
```

## Managing Protected Paths

Users can edit `.template-sync.json` directly to add/remove protected paths:

```bash
# Common protected paths for derived projects:
"protectedPaths": [
  "README.md",           # Project-specific description
  "package.json",        # Project dependencies
  "pyproject.toml",      # Python project config
  "CLAUDE.md",           # Project-specific instructions
  "src/",                # Project source code
  "tests/"               # Project tests
]
```

Glob patterns are supported in `protectedPaths`:
- `"src/"` - Protect entire directory
- `"*.config.js"` - Protect all config files
- `".env*"` - Protect all env files
