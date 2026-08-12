# CI/CD Integration

Integrate Claude Code into development pipelines.

- **GitHub Actions** — workflows for code review, test-and-fix, documentation, conditional execution, security, caching: `references/cicd-github.md`
- **GitLab CI/CD** — pipelines for lint/test/review/deploy, automated fixes, parallel jobs, monitoring: `references/cicd-gitlab.md`

## Quick Reference

**GitHub Actions:**
```yaml
- uses: anthropic/claude-code-action@v1
  with:
    command: '/fix:types && /test'
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

**GitLab CI:**
```yaml
script:
  - npm install -g @anthropic-ai/claude-code
  - claude login --api-key $ANTHROPIC_API_KEY
  - claude '/fix:types && /test'
```

## Security

Store API key as a secret/masked variable. Never expose in logs.

## See Also

- GitHub Actions docs: https://docs.github.com/actions
- GitLab CI docs: https://docs.gitlab.com/ee/ci/
