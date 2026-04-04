# Slash Commands: Development & Fix

Development, debugging, testing, and fix commands.

## Development Commands

### /cook [task]
Implement features step by step.
```bash
/cook implement user authentication with JWT
/cook add payment integration with Stripe
```
**When to use**: Feature implementation with iterative development

### /plan [task]
Research, analyze, and create implementation plans.
```bash
/plan implement OAuth2 authentication
/plan migrate from SQLite to PostgreSQL
```
**When to use**: Before starting complex implementations

### /debug [issue]
Debug technical issues and provide solutions.
```bash
/debug the API returns 500 errors intermittently
/debug authentication flow not working
```
**When to use**: Investigating and diagnosing problems

### /test
Run test suite.
```bash
/test
```
**When to use**: Validate implementations, check for regressions

### /refactor [target]
Improve code quality.
```bash
/refactor the authentication module
/refactor for better performance
```
**When to use**: Code quality improvements

## Fix Commands

### /fix:fast [issue]
Quick fixes for small issues.
```bash
/fix:fast the login button is not working
/fix:fast typo in error message
```
**When to use**: Simple, straightforward fixes

### /fix:hard [issue]
Complex issues requiring planning and subagents.
```bash
/fix:hard database connection pooling issues
/fix:hard race condition in payment processing
```
**When to use**: Complex bugs requiring deep investigation

### /fix:types
Fix TypeScript type errors.
```bash
/fix:types
```
**When to use**: TypeScript compilation errors

### /fix:test [issue]
Fix test failures.
```bash
/fix:test the user service tests are failing
/fix:test integration tests timing out
```
**When to use**: Test suite failures

### /fix:ui [issue]
Fix UI issues.
```bash
/fix:ui button alignment on mobile
/fix:ui dark mode colors inconsistent
```
**When to use**: Visual or interaction issues

### /fix:ci [url]
Analyze GitHub Actions logs and fix CI/CD issues.
```bash
/fix:ci https://github.com/owner/repo/actions/runs/123456
```
**When to use**: Build or deployment failures

### /fix:logs [issue]
Analyze logs and fix issues.
```bash
/fix:logs server error logs showing memory leaks
```
**When to use**: Production issues with log evidence
