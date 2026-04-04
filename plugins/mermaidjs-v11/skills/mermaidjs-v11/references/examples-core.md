# Mermaid.js Examples: Core Diagrams

Real-world patterns for common documentation scenarios.

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

**REST API Endpoints:**
```mermaid
flowchart LR
  API[API]
  Users[/users]
  Posts[/posts]
  Comments[/comments]

  API --> Users
  API --> Posts
  API --> Comments

  Users --> U1[GET /users]
  Users --> U2[POST /users]
  Users --> U3[GET /users/:id]
  Users --> U4[PUT /users/:id]
  Users --> U5[DELETE /users/:id]
```

## Database Design

**E-Commerce Schema:**
```mermaid
erDiagram
  CUSTOMER ||--o{ ORDER : places
  CUSTOMER {
    int id PK
    string email
    string name
  }
  ORDER ||--|{ LINE_ITEM : contains
  ORDER {
    int id PK
    int customer_id FK
    date created_at
    string status
  }
  PRODUCT ||--o{ LINE_ITEM : includes
  PRODUCT {
    int id PK
    string name
    decimal price
    int inventory
  }
  LINE_ITEM {
    int order_id FK
    int product_id FK
    int quantity
    decimal unit_price
  }
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

## Object-Oriented Design

**Payment System Classes:**
```mermaid
classDiagram
  class PaymentProcessor {
    <<interface>>
    +processPayment(amount)
    +refund(transactionId)
  }

  class StripeProcessor {
    -apiKey: string
    +processPayment(amount)
    +refund(transactionId)
  }

  class PayPalProcessor {
    -clientId: string
    -secret: string
    +processPayment(amount)
    +refund(transactionId)
  }

  class PaymentService {
    -processor: PaymentProcessor
    +charge(customer, amount)
    +issueRefund(orderId)
  }

  PaymentProcessor <|.. StripeProcessor
  PaymentProcessor <|.. PayPalProcessor
  PaymentService --> PaymentProcessor
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
