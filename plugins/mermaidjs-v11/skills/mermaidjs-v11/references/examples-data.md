# Mermaid.js Examples: Database & OOP Diagrams

Database schemas, class diagrams, and REST API endpoint documentation.

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

## API Endpoint Map

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
