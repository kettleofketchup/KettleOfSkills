# Domain Verification Procedures

## Email Domain Analysis

### Character-by-Character Comparison

Compare the sender domain against the known legitimate domain one character at a time. Do not rely on visual pattern matching -- it misses homoglyph attacks.

Common substitutions to catch:
- `rn` replacing `m` (e.g., `rnicrosoft.com` vs `microsoft.com`)
- `l` (lowercase L) replacing `I` (uppercase i)
- `0` (zero) replacing `O`
- `vv` replacing `w`
- `cl` replacing `d`

### TLD Swaps

Check for domain variants that swap the top-level domain:
- `.co` instead of `.com`
- `.net` instead of `.org`
- `.io` instead of `.com`
- Country-code TLDs mimicking generic ones (`.com.br` vs `.com`)

### Subdomain Tricks

Watch for legitimate-looking domains used as subdomains of attacker-controlled domains:
- `login.microsoft.com.attacker.xyz` -- the registrable domain is `attacker.xyz`
- `support-google.com` -- entirely different domain from `google.com`

## URL Domain Analysis

### Read Right-to-Left from the TLD

To identify the actual domain a URL points to:

1. Find the TLD (`.com`, `.org`, `.co.uk`, etc.)
2. Move left one label -- this is the second-level domain
3. Together, these form the **registrable domain** (e.g., `example.com`)
4. Everything to the left of the registrable domain is a subdomain and does not determine ownership

Example breakdown:
```
https://secure.login.accounts.example.com/auth
         ^      ^       ^        ^       ^
         |      |       |        |       +-- TLD
         |      |       |        +-- second-level domain
         |      |       +-- subdomain (not relevant to ownership)
         |      +-- subdomain
         +-- subdomain

Registrable domain: example.com
```

### Path-Based Deception

Attackers may place legitimate-looking domain names in the URL path:
- `https://attacker.com/google.com/login` -- the domain is `attacker.com`
- `https://attacker.com/?redirect=https://legitimate.com` -- still `attacker.com`

Always identify the registrable domain from the authority section of the URL, never from the path or query string.

## Account Compromise Indicators

Even when the sender domain is verified as legitimate, watch for signs of account compromise:

- Message tone, style, or language deviates from the sender established patterns
- Unexpected requests for credentials, payments, or sensitive data
- Links to external domains that the sender would not normally reference
- Unusual sending times or frequency
- Requests to change communication channels ("text me instead", "use this personal email")
- Attachments with executable extensions or password-protected archives

A legitimate domain does not guarantee a legitimate sender. Compromised accounts send from correct domains.
