# gh CLI Reference

Complete reference for GitHub CLI operations.

## Authentication

```bash
gh auth login                     # Interactive OAuth/token login
gh auth login --with-token < token.txt  # Non-interactive
gh auth logout                    # Remove credentials
gh auth status                    # Show auth state
gh auth token                     # Print current token
gh auth refresh -s write:packages # Add scope to token
```

## Pull Requests

```bash
# Create
gh pr create                      # Interactive
gh pr create --fill               # Auto-fill from commits
gh pr create --draft              # Draft PR
gh pr create -B main -t "Title" -b "Body"
gh pr create --reviewer user1,user2
gh pr create --label bug,priority

# List/View
gh pr list                        # Open PRs
gh pr list --state all            # All states
gh pr list --author @me           # My PRs
gh pr list --search "is:open review:required"
gh pr view 123                    # View PR
gh pr view 123 --comments         # Include comments
gh pr diff 123                    # Show diff

# Checkout/Review
gh pr checkout 123                # Switch to PR branch
gh pr review 123 --approve
gh pr review 123 --request-changes -b "Needs work"
gh pr review 123 --comment -b "LGTM"

# Merge
gh pr merge 123                   # Interactive merge
gh pr merge 123 --squash          # Squash merge
gh pr merge 123 --rebase          # Rebase merge
gh pr merge 123 --auto --squash   # Auto-merge when checks pass
gh pr merge 123 --delete-branch   # Delete branch after merge

# Update
gh pr edit 123 --title "New Title"
gh pr edit 123 --add-label enhancement
gh pr ready 123                   # Mark ready for review
gh pr close 123
gh pr reopen 123
```

## Issues

```bash
# Create
gh issue create                   # Interactive
gh issue create --title "Bug" --body "Description"
gh issue create --label bug,urgent --assignee @me
gh issue create --project "Board Name"

# List/View
gh issue list                     # Open issues
gh issue list --assignee @me
gh issue list --label "bug,priority"
gh issue list --milestone "v1.0"
gh issue list --search "is:open no:assignee"
gh issue view 123

# Update
gh issue edit 123 --title "New Title"
gh issue edit 123 --add-label wontfix
gh issue close 123 --reason completed
gh issue close 123 --reason "not planned"
gh issue reopen 123
gh issue transfer 123 owner/other-repo
gh issue pin 123
gh issue unpin 123
```

## Releases

```bash
# Create
gh release create v1.0.0                    # Tag only
gh release create v1.0.0 ./dist/*           # With assets
gh release create v1.0.0 --generate-notes   # Auto release notes
gh release create v1.0.0 --draft            # Draft release
gh release create v1.0.0 --prerelease
gh release create v1.0.0 --target branch-name
gh release create v1.0.0 -t "Title" -n "Notes"

# List/View
gh release list
gh release view v1.0.0
gh release download v1.0.0          # Download all assets
gh release download v1.0.0 -p "*.tar.gz"

# Update
gh release upload v1.0.0 ./new-asset.zip
gh release edit v1.0.0 --draft=false
gh release delete v1.0.0
```

## Repository

```bash
gh repo create name               # Create new repo
gh repo create name --public
gh repo create name --clone       # Create and clone
gh repo clone owner/repo
gh repo fork owner/repo
gh repo view                      # Current repo
gh repo view owner/repo --web     # Open in browser
gh repo sync                      # Sync fork with upstream
gh repo archive owner/repo
gh repo delete owner/repo --yes
```

## Workflows (Actions)

```bash
# List/View
gh run list                       # Recent runs
gh run list --workflow=ci.yml
gh run list --branch main
gh run view 123456                # Run details
gh run view 123456 --log          # Full logs
gh run view 123456 --log-failed   # Only failed logs

# Control
gh run watch 123456               # Watch in real-time
gh run rerun 123456               # Rerun workflow
gh run rerun 123456 --failed      # Rerun failed jobs only
gh run cancel 123456
gh run download 123456            # Download artifacts

# Workflows
gh workflow list
gh workflow view ci.yml
gh workflow run ci.yml            # Trigger workflow_dispatch
gh workflow run ci.yml -f input=value
gh workflow enable ci.yml
gh workflow disable ci.yml
```

## API (Advanced)

```bash
# REST API
gh api repos/{owner}/{repo}
gh api repos/{owner}/{repo}/issues
gh api -X POST repos/{owner}/{repo}/issues -f title="Bug"
gh api repos/{owner}/{repo}/actions/runs --jq '.workflow_runs[].status'

# GraphQL
gh api graphql -f query='{ viewer { login } }'
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      issues(first: 10) {
        nodes { title number }
      }
    }
  }
' -f owner='{owner}' -f repo='{repo}'

# Pagination
gh api repos/{owner}/{repo}/issues --paginate

# Output formatting
gh api repos/{owner}/{repo} --jq '.stargazers_count'
gh api repos/{owner}/{repo} --template '{{.full_name}}'
```

## Extensions

```bash
gh extension list
gh extension install owner/gh-extension
gh extension upgrade --all
gh extension remove extension-name
gh extension search keyword
```

## Configuration

```bash
gh config set editor vim
gh config set git_protocol ssh
gh config set prompt disabled
gh config get git_protocol
gh config list
```

## Secrets

```bash
gh secret list
gh secret set SECRET_NAME
gh secret set SECRET_NAME < secret.txt
gh secret set SECRET_NAME --env production
gh secret delete SECRET_NAME
```

## Common Patterns

```bash
# Get PR number from current branch
gh pr view --json number -q .number

# List open PRs as JSON
gh pr list --json number,title,author

# Wait for checks to pass
gh pr checks 123 --watch

# Create issue from template
gh issue create --template bug_report.md

# Bulk close stale issues
gh issue list --label stale --json number -q '.[].number' | xargs -I{} gh issue close {}
```
