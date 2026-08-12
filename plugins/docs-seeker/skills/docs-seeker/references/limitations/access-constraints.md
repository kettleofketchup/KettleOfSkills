# Limitations: Access Constraints

Understanding hard boundaries where documentation discovery cannot retrieve content.

## Password-Protected Documentation

**Limitation:**
- No access to authentication-required content
- Cannot log in to platforms
- Cannot access organization-internal docs

**Impact:**
- Enterprise documentation inaccessible
- Premium content unavailable
- Private beta docs unreachable

**Workarounds:**
```
- Ask user for public alternatives
- Search for public subset of docs
- Use publicly available README/marketing
- Note limitation in report
```

**Report template:**
```markdown
Access Limitation

Documentation requires authentication.

What we can access:
- Public README: [url]
- Package registry info: [url]
- Marketing site: [url]

Cannot access:
- Full documentation (requires login)
- Internal guides

Recommendation: Contact vendor for access or check if public docs available.
```

## Rate-Limited APIs

**Limitation:**
- No API credentials for authenticated access
- Subject to anonymous rate limits (e.g., GitHub: 60/hour)
- May hit limits during comprehensive search

**Workarounds:**
```
- Add delays between requests
- Use alternative sources (cached, mirrors)
- Prioritize critical pages
- Switch to repository analysis
```

**Detection:**
```
Symptoms: 429 Too Many Requests, X-RateLimit-Remaining: 0

Response:
- Immediately switch to alternative method
- Don't retry same endpoint
- Note in report which method used
```

## Real-Time Documentation

**Limitation:**
- Uses snapshot at time of access
- Cannot monitor for updates
- May miss very recent changes

**Workarounds:**
```
- Note access date in report
- Recommend user verify if critical
- Check last-modified headers
- Suggest official site for latest
```

**Report template:**
```markdown
Snapshot Information

Documentation retrieved: [date] UTC
Last-Modified (if available): [date]

Note: For real-time updates, check official site: [url]
```

## Interactive Documentation

**Limitation:**
- Cannot run interactive examples
- Cannot execute code playgrounds
- Cannot test API calls

**Workarounds:**
```
- Provide code examples as-is
- Note: "Example provided, not tested"
- Recommend user run examples
- Include caveats about untested code
```

## Video-Only Documentation

**Limitation:**
- Cannot process video content directly
- Limited transcript access
- Cannot extract code from video

**Workarounds:**
```
- Search for transcript if available
- Look for accompanying blog post
- Find text-based alternative
- Check for community notes
```

**Report template:**
```markdown
Video Content Detected

Primary documentation is video-based: [url]

Alternatives found:
- Blog post summary: [url]
- Community notes: [url]

Cannot extract: Detailed walkthrough, visual examples, demonstration steps.

Recommendation: Watch video directly for visual content.
```
