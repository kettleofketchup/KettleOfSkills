# gh CLI: Advanced Usage

## API

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

## Secrets

```bash
gh secret list
gh secret set SECRET_NAME
gh secret set SECRET_NAME < secret.txt
gh secret set SECRET_NAME --env production
gh secret delete SECRET_NAME
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
