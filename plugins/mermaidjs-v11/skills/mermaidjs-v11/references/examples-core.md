# Mermaid.js Examples: Core Diagrams

Real-world patterns for architecture, API, and state machine documentation.

## Software Architecture

**Microservices Architecture:**
```mermaid
flowchart TB
  Client[Web Client]
  Gateway[API Gateway]
  Auth[Auth Service]
  User[User Service]
  Order[Order Service]
  Payment[Payment Service]
  DB1[(Users DB)]
  DB2[(Orders DB)]
  Cache[(Redis Cache)]

  Client --> Gateway
  Gateway --> Auth
  Gateway --> User
  Gateway --> Order
  User --> DB1
  Order --> DB2
  Order --> Payment
  User --> Cache
```

## API Documentation

**Authentication Flow:**
```mermaid
sequenceDiagram
  participant C as Client
  participant A as API
  participant D as Database

  C->>A: POST /auth/login
  activate A
  A->>D: Verify credentials
  D-->>A: User found
  A->>A: Generate JWT
  A-->>C: 200 OK + token
  deactivate A

  C->>A: GET /protected (Bearer token)
  activate A
  A->>A: Validate JWT
  A->>D: Fetch data
  D-->>A: Data
  A-->>C: 200 OK + data
  deactivate A
```

## State Machines

**Order Processing:**
```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Processing : payment_received
  Pending --> Cancelled : timeout
  Processing --> Shipped : items_packed
  Processing --> Failed : error
  Shipped --> Delivered : confirmed
  Delivered --> [*]
  Failed --> Refunded : refund_processed
  Cancelled --> [*]
  Refunded --> [*]
```

**User Authentication States:**
```mermaid
stateDiagram-v2
  [*] --> LoggedOut
  LoggedOut --> LoggingIn : submit_credentials
  LoggingIn --> LoggedIn : success
  LoggingIn --> LoggedOut : failure
  LoggedIn --> VerifyingMFA : requires_2fa
  VerifyingMFA --> LoggedIn : mfa_success
  VerifyingMFA --> LoggedOut : mfa_failure
  LoggedIn --> LoggedOut : logout
  LoggedIn --> [*]
```

## CI/CD Pipeline

**Deployment Flow:**
```mermaid
flowchart LR
  Code[Push Code] --> CI{CI Checks}
  CI -->|Pass| Build[Build]
  CI -->|Fail| Notify1[Notify Team]
  Build --> Test[Run Tests]
  Test -->|Pass| Stage[Deploy Staging]
  Test -->|Fail| Notify2[Notify Team]
  Stage --> Manual{Manual Approval}
  Manual -->|Approved| Prod[Deploy Production]
  Manual -->|Rejected| End1[End]
  Prod --> Monitor[Monitor]
  Monitor --> End2[End]
```
