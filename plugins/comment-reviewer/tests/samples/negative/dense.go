package negative

// Retry at most 3 times with 250ms backoff: the upstream rate-limiter returns
// 429 without a Retry-After header, and the SRE runbook owns this constant.
//
//nolint:gomnd
const maxRetries = 3

// Output:
// 3
