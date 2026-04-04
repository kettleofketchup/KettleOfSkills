# Sharing Open WebUI

**Deploy once, give your entire team access.**

Open WebUI is built to be shared. A single instance can serve your whole organization. Users just open a browser and start chatting. No per-seat installs, no client-side dependencies, no fragmented data across machines.

---

## Built for Teams

### Frictionless Onboarding

End users don't need to install anything, manage Docker, or touch a terminal. They open a browser, navigate to your instance URL, and log in.

### Collaborative Intelligence

A shared instance means shared knowledge.

| Feature | Description |
| :--- | :--- |
| **Channels** | Persistent spaces where your team and AI models work together in real time |
| **Shared Chats** | Send an exact conversation snapshot to a colleague |
| **Global Prompts & Knowledge** | Build specialized agents and make them instantly available to everyone |

### Shared Compute

When running local models, a single powerful server (or cluster) serves your entire team instead of requiring capable hardware on every desk.

### Centralized Administration

Manage everything from one place: control which models users can access, configure **Role-Based Access Control (RBAC)**, review audit logs, and restrict features as needed.

---

## Opening Your Instance to the Team

### 1. Zero-Config LAN (Local Network)

If your team is on the same local network or VPN, they can reach Open WebUI using your machine's local IP address and port.

> `http://192.168.1.100:3000`

### 2. Secure Private Networks (Recommended)

For remote teams that don't need public internet exposure:

| Solution | Description |
| :--- | :--- |
| **Tailscale** | Private mesh network with MagicDNS (`https://open-webui.tailnet-name.ts.net`) |
| **Cloudflare Tunnels** | Expose via Cloudflare's edge, protected by Cloudflare Access (Zero Trust) |
| **ngrok** | Quick temporary sharing for development or testing |

### 3. Public HTTPS (Reverse Proxy)

For production deployments with SSL/TLS termination on your own domain:

| Solution | Description |
| :--- | :--- |
| **Nginx** | Industry standard web server and reverse proxy |
| **Caddy** | Automatic HTTPS with minimal configuration |
| **HAProxy** | High-performance load balancing and proxying |

---

## Onboarding Your Team

### The Pending Queue

The first user to register becomes the **Administrator**. All subsequent sign-ups are placed in a **Pending** state and cannot access models or use the platform until an admin approves their account from the Admin Panel.

### Enterprise Single Sign-On (SSO)

| Method | Description |
| :--- | :--- |
| **OAuth / OIDC** | Authenticate via **Google**, **Microsoft**, **Okta**, or **Keycloak** |
| **Group mapping** | Map IdP groups directly to Open WebUI groups |
| **SCIM 2.0** | Automated user and group provisioning and deprovisioning |
