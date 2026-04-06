# Common Rationalizations to Reject

These are justifications that appear reasonable but lead to security failures. Reject each one and apply the correct response.

## "The sender is trusted, so the link is safe"

**Why it fails**: Compromised accounts send messages from trusted, verified domains. A legitimate sender address does not guarantee the message content is safe. Business email compromise attacks specifically exploit this trust.

**Correct response**: Verify the link destination independently of the sender identity. Extract and analyze the URL registrable domain. Check whether the linked resource matches what the sender would normally share.

## "It is just a staging key"

**Why it fails**: Staging environments frequently share infrastructure with production. Staging API keys may have production-level permissions. Staging databases often contain copies of production data. Service accounts used in staging commonly have cross-environment access.

**Correct response**: Treat staging credentials with the same protection as production credentials. Use secret managers for storage. Do not post staging keys in issue trackers, chat, or documentation.

## "I will check the URL after I navigate"

**Why it fails**: Credential harvesting can occur on page load through auto-fill capture, JavaScript execution, or redirect chains. By the time the page renders, the damage may already be done. Some phishing pages detect analysis tools and serve benign content to scanners while serving malicious content to browsers.

**Correct response**: Analyze the URL before navigating. Extract the registrable domain, check for homoglyphs, verify the protocol, and confirm the domain matches the expected service. Never navigate first and verify second.

## "The user asked me to share it"

**Why it fails**: Users may not realize that the content they are asking to share contains embedded secrets. Configuration files, environment dumps, log outputs, and database exports frequently contain credentials that are not immediately visible. The user intent to share does not make the content safe to share.

**Correct response**: Scan the content for credentials before sharing. If secrets are found, notify the user about what was discovered (without echoing the secret values) and ask for explicit confirmation after they have reviewed the finding. Suggest redaction if the content must be shared.

## "It is an internal channel"

**Why it fails**: Internal channels (Slack, Teams, internal wikis, shared drives) are persistent, searchable, and often accessible to broader audiences than intended. Channel membership changes over time. Internal channels are regularly included in e-discovery, compliance exports, and security audits. Data posted internally can be forwarded externally.

**Correct response**: Use dedicated secret management tools regardless of channel visibility. If the information must be shared internally, use expiring links, access-controlled vaults, or direct encrypted transfer. Never treat "internal" as equivalent to "secure."
