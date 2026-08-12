# CI/CD Integration — GitHub Actions

Integrate Claude Code into GitHub Actions workflows.

## Basic Workflow

**.github/workflows/claude.yml:**
```yaml
name: Claude Code CI
on: [push, pull_request]
jobs:
  claude-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: anthropic/claude-code-action@v1
        with:
          command: '/fix:types && /test'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Code Review on PR

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Review with Claude
        uses: anthropic/claude-code-action@v1
        with:
          command: |
            Review the changes: check for bugs, verify test coverage,
            assess performance, review security concerns
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Post Review Comment
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner, repo: context.repo.repo,
              body: process.env.CLAUDE_OUTPUT
            })
```

## Test and Fix Workflow

```yaml
steps:
  - uses: actions/checkout@v3
  - name: Run Tests
    id: test
    continue-on-error: true
    run: npm test
  - name: Fix Failures
    if: steps.test.outcome == 'failure'
    uses: anthropic/claude-code-action@v1
    with:
      command: '/fix:test check test output and fix failures'
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  - name: Commit Fixes
    if: steps.test.outcome == 'failure'
    run: |
      git config user.name "Claude Bot" && git config user.email "claude@anthropic.com"
      git add . && git commit -m "fix: auto-fix test failures" && git push
```

## Common Patterns

### Conditional Execution

```yaml
# Run on large PRs only (cost control)
- if: ${{ github.event.pull_request.changed_files > 10 }}
  uses: anthropic/claude-code-action@v1
# Skip for draft PRs
- if: ${{ !github.event.pull_request.draft }}
  uses: anthropic/claude-code-action@v1
```

### Matrix Builds

```yaml
strategy:
  matrix:
    task: [lint, test, review]
steps:
  - run: claude "/${{ matrix.task }}"
```

### Caching

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.claude/cache
    key: claude-cache-${{ hashFiles('package-lock.json') }}
```

## Security Best Practices

Store API key: `Settings → Secrets and variables → Actions → Add: ANTHROPIC_API_KEY`

```yaml
# Restrict permissions
permissions:
  contents: read
  pull-requests: write

# Prevent key exposure
- run: |
    if git diff | grep -i "ANTHROPIC_API_KEY"; then echo "API key detected!" && exit 1; fi

# Save artifacts; handle failure
- uses: actions/upload-artifact@v3
  with: { name: claude-results, path: claude-output.md }
- if: steps.claude.outcome == 'failure'
  run: echo "Claude task failed, continuing anyway"
```

## See Also

- GitLab CI: `references/cicd-gitlab.md`
- GitHub Actions docs: https://docs.github.com/actions
