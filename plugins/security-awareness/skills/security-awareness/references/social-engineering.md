# Social Engineering Signal Detection

## Urgency and Artificial Deadlines

Manufactured time pressure is the most common social engineering tactic. Flag these patterns:

- "Act within the next hour or your account will be suspended"
- "This must be resolved before end of business today"
- "Immediate action required" with no prior context or ticket
- Countdown timers or expiration warnings on credential pages
- "Emergency" requests that bypass normal approval workflows

Legitimate urgent situations still follow established procedures. Real emergencies come through known channels with verifiable context.

## Authority Pressure

Attackers impersonate authority figures to bypass critical thinking:

- **Executive impersonation**: "The CEO needs this wired immediately" -- verify through a separate, known channel
- **IT department**: "We need your credentials to fix a security issue" -- IT never asks for passwords
- **Legal/compliance**: "Failure to respond will result in legal action" -- verify through official legal contacts
- **HR department**: "Update your direct deposit information here" -- use only the known HR portal
- **External auditors**: "Provide access credentials for the audit" -- auditors coordinate through management, not direct requests

The higher the claimed authority, the more verification is required.

## Credential and MFA Requests

Flag any credential or MFA request that arrives through an unfamiliar channel:

- Login pages reached through email links rather than direct navigation
- MFA approval requests not initiated by the user
- "Verify your identity" pages that do not match the service known login flow
- Requests to share MFA codes via phone, email, or chat
- Push notification fatigue attacks (repeated MFA prompts hoping for accidental approval)

Always navigate to login pages directly. Never follow links to authentication flows.

## Procedure Bypass Requests

Any request to skip normal security procedures is a red flag:

- "Skip the approval process, this is time-sensitive"
- "Do not verify with the team, I have already cleared it"
- "Use this alternate process instead of the normal one"
- "Send it to my personal email, my work email is down"
- "Do not log this transaction"

Legitimate requests work within established procedures. The moment someone asks to go around controls, escalate.

## Business Email Compromise (BEC) Patterns

BEC attacks target financial transactions and data transfers:

- Unsolicited requests to change banking details for invoices or payroll
- "Updated wire instructions" from a vendor or executive
- Requests to purchase gift cards and share the codes
- Invoice redirects to new payment accounts
- Subtle changes to reply-to addresses that differ from the sender

Any change to payment details requires out-of-band verification through a previously known phone number or in-person confirmation.

## Being Decisive

When a known attack pattern is identified:

- State the finding directly: "This matches a phishing pattern"
- Specify which signals triggered the assessment
- Do not hedge with "this might be legitimate" when multiple indicators are present
- Recommend concrete next steps (do not navigate, verify through separate channel, flag to security team)
- One strong signal is enough to stop. Do not wait for multiple confirmations before acting.
