# Understanding Settings

Open WebUI has two separate settings areas, not one. The architecture assumes multi-user from day one.

## The Two Settings Areas

### Admin Settings (Global)

| | |
|---|---|
| **Location** | Profile avatar > **Admin Settings**, or **Admin Panel > Settings** |
| **Access** | Administrators only |
| **Scope** | The entire instance and all users |

Controls everything about the Open WebUI instance: API connections, feature toggles, security policies, and default behaviors.

**Examples:**
- Connections to Ollama, OpenAI, and other providers
- Enabling or disabling web search, image generation, and code execution
- Default model selection and parameter presets
- RBAC policies, SSO configuration, and signup restrictions

### User Settings (Personal)

| | |
|---|---|
| **Location** | Profile avatar > **Settings** |
| **Access** | Every user (including admins) |
| **Scope** | Only the individual user |

Controls personal preferences within what the admin has enabled.

**Examples:**
- Preferred default model and system prompt
- Interface theme and language
- Personal API keys (if Direct Connections are enabled)
- Per-feature toggles like autocomplete or rich text input

## How They Work Together

Many features follow a two-layer pattern:
1. The admin decides whether a feature is available (Admin Settings)
2. Each user decides whether they personally want to use it (User Settings)

**Example: Autocomplete**

| Layer | Setting Location | Effect |
|-------|-----------------|--------|
| Admin enables it | Admin Settings > Interface | Makes autocomplete available on the instance |
| User enables it | Settings > Interface | Turns autocomplete on for you personally |

If an admin disables a feature globally, users cannot enable it for themselves. The admin setting is always the ceiling.

## Quick Reference

| | Admin Settings | User Settings |
|---|---|---|
| **Scope** | Entire instance (all users) | Individual user only |
| **Access** | Admins only | Everyone |
| **Controls** | API connections, feature toggles, security, defaults | Theme, default model, personal preferences |
| **Override behavior** | Cannot be overridden by users | Can customize within admin-allowed boundaries |

## Common Scenarios

**"I enabled a feature in my settings but it is not working."**
Check whether the admin has enabled it globally first.

**"I am the admin. Where do I configure connections to OpenAI or Ollama?"**
Admin Settings > Connections. These are instance-wide and shared by all users.

**"I want to use my own API key without sharing it with the server."**
If the admin has enabled Direct Connections, you can add personal API keys in User Settings > Connections.

**"I set a system prompt but my admin's model settings override it."**
Model-level settings configured by admins in the Workspace take precedence over personal settings.

**First-Time Admin?** Start with Admin Settings > Connections to connect your model providers, then explore Admin Settings > Interface to enable or disable features.
