# Mermaid.js Diagram Types: Planning & Architecture

Syntax reference for planning, architecture, and data visualization diagrams.

## Planning Diagrams

### User Journey
Experience flows, satisfaction tracking.

**Syntax:**
```
journey
  title User Journey
  section Shopping
    Browse: 5: Customer
    Add to cart: 3: Customer, System
```

**Scores:** 1-5 satisfaction levels

### Kanban
Task boards, workflow stages.

**Syntax:**
```
kanban
  Todo[Task Board]
    task1[Implement API]
    @{ assigned: "Dev1", priority: "High" }
  InProgress[In Progress]
    task2[Fix bug]
```

### Quadrant Chart
Prioritization, trend analysis.

**Syntax:**
```
quadrantChart
  x-axis Low --> High
  y-axis Low --> High
  Item A: [0.3, 0.6]
```

## Architecture Diagrams

### C4 Diagram
System architecture, components.

**Syntax:**
```
C4Context
  Person(user, "User")
  System(app, "Application")
  Rel(user, app, "Uses")
```

### Architecture Diagram
Cloud infrastructure, services.

**Syntax:**
```
architecture-beta
  service api(server)[API]
  service db(database)[Database]
  api:R --> L:db
```

**Icons:** cloud, database, disk, internet, server, or iconify.design icons

### Block Diagram
Module dependencies, networks.

**Syntax:**
```
block-beta
  columns 3
  a["Block A"] b["Block B"]
  a --> b
```

**Shapes:** rounded, stadium, cylinder, diamond, trapezoid, hexagon

## Data Visualization

### Pie Chart
Proportions, distributions.

**Syntax:**
```
pie showData
  "Category A" : 45.5
  "Category B" : 30.0
```

### XY Chart
Trends, comparisons.

**Syntax:**
```
xychart-beta
  x-axis [jan, feb, mar]
  y-axis "Sales" 0 --> 100
  line [30, 45, 60]
  bar [25, 40, 55]
```

### Sankey
Flow visualization, resource allocation.

**Syntax:**
```
sankey-beta
  Source,Target,Value
  A,B,10
  B,C,5
```

### Radar Chart
Multi-dimensional comparison.

**Syntax:**
```
radar-beta
  axis Skill1, Skill2, Skill3
  curve Team1{3,4,5}
  curve Team2{4,3,4}
```

### Treemap
Hierarchical proportions.

**Syntax:**
```
treemap-beta
  "Root"
    "Category A"
      "Item 1": 100
      "Item 2": 200
```
