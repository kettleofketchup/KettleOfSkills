# Mermaid.js Diagram Types: Core

Syntax reference for the most commonly used diagram types.

## Flowchart
Process flows, decision trees, workflows.

**Syntax:**
```
flowchart {direction}
  {nodeId}[{label}] {arrow} {nodeId}[{label}]
```

**Directions:** TB/TD (top-bottom), BT, LR (left-right), RL
**Shapes:** `()` round, `[]` rect, `{}` diamond, `{{}}` hexagon, `(())` circle
**Arrows:** `-->` solid, `-.->` dotted, `==>` thick
**Subgraphs:** Group related nodes

## Sequence Diagram
Actor interactions, API flows, message sequences.

**Syntax:**
```
sequenceDiagram
  participant A as Actor
  A->>B: Message
  activate B
  B-->>A: Response
  deactivate B
```

**Arrows:** `->` solid, `->>` arrow, `-->` dotted, `-x` cross, `-)` async
**Features:** Loops, alternatives, parallel, optional, critical regions

## Class Diagram
OOP structures, inheritance, relationships.

**Syntax:**
```
classDiagram
  class Animal {
    +String name
    -int age
    +void eat()
  }
  Animal <|-- Dog : inherits
```

**Visibility:** `+` public, `-` private, `#` protected, `~` package
**Relationships:** `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association

## State Diagram
State machines, transitions, workflows.

**Syntax:**
```
stateDiagram-v2
  [*] --> State1
  State1 --> State2 : transition
  State2 --> [*]
```

**Features:** Composite states, choice points, forks/joins, concurrency

## ER Diagram
Database relationships, schemas.

**Syntax:**
```
erDiagram
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
```

**Cardinality:** `||` one, `|o` zero-one, `}|` one-many, `}o` zero-many

## Gantt Chart
Project timelines, schedules.

**Syntax:**
```
gantt
  title Project
  dateFormat YYYY-MM-DD
  section Phase1
    Task1 :done, 2024-01-01, 5d
    Task2 :active, after Task1, 3d
```

**Status:** `done`, `active`, `crit`, `milestone`

## Quick Reference

| Type | Best For | Complexity |
|------|----------|------------|
| Flowchart | Processes | Low |
| Sequence | Interactions | Medium |
| Class | OOP | High |
| State | Behaviors | Medium |
| ER | Databases | Low |
| Gantt | Timelines | Medium |
