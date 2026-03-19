---
name: review-pr-comments
description: Fetch PR comments, assess each one, and apply fixes if needed. Use when you want to review and address feedback on the current branch's pull request.
user-invocable: true
argument-hint: "[PR number (optional, defaults to current branch PR)]"
---

# Review PR Comments

Fetch all comments from a GitHub pull request, assess whether each requires action, and apply fixes automatically.

## Workflow

Follow these steps in order:

### Step 1: Identify the PR

- If a PR number is provided as an argument, use it directly
- Otherwise, detect the PR from the current branch:
  ```bash
  gh pr view --json number,headRefName,baseRefName,headRepository
  ```
- If no PR is found, inform the user and stop

### Step 2: Fetch all comments

Fetch both PR-level and review comments in parallel:

```bash
# PR-level comments
gh api --paginate /repos/{owner}/{repo}/issues/{number}/comments

# Review comments (inline code comments)
gh api --paginate /repos/{owner}/{repo}/pulls/{number}/comments
```

### Step 3: Display and assess each comment

For each comment, display in this format:

~~~
- @author file.ts#line:
  ```diff
  [diff_hunk]
  ```
  > comment body
~~~

Then create an assessment table:

| # | Comment | Judgment | Action |
|---|---------|----------|--------|
| 1 | Summary of comment | Needs fix / No action needed / Already addressed | Planned action or reason for skipping |

**Assessment criteria:**
- **Needs fix**: The comment points out a valid bug, security issue, performance problem, or style violation that should be addressed
- **No action needed**: The comment is a question, praise, FYI, or a suggestion you disagree with (explain why)
- **Already addressed**: The issue was already fixed in a subsequent commit

### Step 4: Apply fixes

For each comment marked "Needs fix":

1. Read the relevant file(s) to understand the full context
2. Make the minimal necessary change to address the feedback
3. Verify the fix doesn't break anything (run tests/lint if applicable)

### Step 5: Commit and push

After all fixes are applied:

1. Stage only the modified files
2. Create a single commit with message format:
   ```
   fix: address PR review comments

   - Summary of fix 1
   - Summary of fix 2
   ```
3. Push to the current branch

### Step 6: Report

Provide a final summary of what was done:
- How many comments were reviewed
- How many required fixes
- What changes were made
- Any comments that need human decision (if applicable)
