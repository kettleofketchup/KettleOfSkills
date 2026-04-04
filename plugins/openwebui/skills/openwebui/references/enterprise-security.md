# Enterprise Security

### Enterprise-Grade Security Without Compromise

For enterprise organizations, AI adoption isn't just a technology decision, it's a security decision. Every model query, every document uploaded, and every workflow automated represents data that needs protection.

Open WebUI is built with security as a foundational principle.

### Security Architecture

#### Your Data, Your Infrastructure

| Deployment Model | Description |
| :--- | :--- |
| **On-Premise** | Run entirely within your own data centers, nothing leaves your network. |
| **Private Cloud** | Deploy in your organization's cloud tenancy (AWS, Azure, GCP) with full infrastructure control. |
| **Air-Gapped** | Complete network isolation for environments with the strictest security requirements. |
| **Hybrid** | Flexible configurations that balance accessibility with security boundaries. |

### Compliance Frameworks

The platform's architecture and controls align with major compliance frameworks:

* **SOC 2** - Operational compliance demonstrating reliability, integrity, and security.
* **HIPAA** - Healthcare data protection requirements for covered entities.
* **GDPR** - European data protection and privacy regulations.
* **FedRAMP** - Federal security standards for cloud services used by US government agencies.
* **ISO 27001** - International standard for information security management systems.

Open WebUI provides the **technical controls and architecture** to support these frameworks. Achieving certification requires proper configuration, organizational policies, and often third-party audits specific to your deployment.

### Identity & Access Management

#### Enterprise Identity Integration

* **LDAP & Active Directory** - Connect directly to your existing directory services for user authentication and management.
* **Single Sign-On (SSO)** - Support for SAML and OIDC protocols, enabling users to access Open WebUI with their existing corporate credentials.
* **Multi-Factor Authentication (MFA)** - Layer additional security on top of primary authentication.

#### Access Control & Permissions

* **Role-Based Access Control (RBAC)** - Define roles that align with your organizational structure to limit administrative access.
* **Model-Level Permissions** - Control which users or groups can access specific models.
* **Workspace Isolation** - Separate teams or departments to prevent unauthorized data access.

### Data Governance

#### Audit & Accountability

* **Infrastructure-Level Logging** - Containerized architecture allows standard output streams to be piped directly to your logging infrastructure (Splunk, Datadog, ELK).
* **Event Tracking** - Track API usage and system events to monitor for anomalies.
* **Retention Controls** - Because you own the database, you control the data retention policies, ensuring data is purged or archived according to your compliance schedules.

#### Data Residency

For organizations with geographic data requirements, whether driven by GDPR, data sovereignty laws, or internal policy, Open WebUI's deployment options ensure your data stays physically located where it is legally required to be.

---

## Architecture & High Availability

### Built for Mission-Critical Reliability

Open WebUI is architected from the ground up to support enterprise-scale deployments where reliability isn't optional. Whether you're supporting a pilot team of 15 or a global workforce of hundreds of thousands of users, Open WebUI's architecture scales with you.

### Stateless, Container-First Design

* **Horizontal Scaling:** Add more instances as demand grows, rather than upgrading to larger hardware.
* **Flexible Deployment:** Run on-premise, in private clouds, or hybrid environments without architectural changes.
* **Container Orchestration Compatibility:** Full support for Kubernetes, Docker Swarm, and other orchestration platforms.

### High Availability Configuration

| Component | Capability |
| :--- | :--- |
| **Load Balancing** | Multiple container instances behind a load balancer for resilience and optimal performance. |
| **External Databases** | PostgreSQL for the main database (SQLite is not supported for multi-instance). |
| **External Vector Database** | A client-server vector database (PGVector, Milvus, Qdrant) or ChromaDB in HTTP server mode. The default ChromaDB local mode uses SQLite which is not safe for multi-process access. |
| **Redis** | Required for session management, WebSocket coordination, and configuration sync across instances. |
| **Persistent Storage** | Flexible storage backends to meet your data residency and performance requirements. |
| **Observability** | Integration with modern logging and metrics tools for proactive monitoring. |

### Scalability in Practice

The platform is already trusted in deployments supporting extremely high user counts:

* **Universities** managing institution-wide AI access.
* **Multinational Enterprises** deploying across regions and business units.
* **Major Organizations** requiring consistent performance under heavy load.

With the right infrastructure configuration, Open WebUI scales from pilot projects to mission-critical worldwide rollouts.
