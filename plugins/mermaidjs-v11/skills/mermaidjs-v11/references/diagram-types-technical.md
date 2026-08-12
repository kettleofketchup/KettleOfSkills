# Mermaid.js Diagram Types: Technical

Syntax reference for git, timeline, network, mindmap, and requirement diagrams.

## Technical Diagrams

### Git Graph
Branching strategies, workflows.

**Syntax:**
```
gitGraph
  commit
  branch develop
  checkout develop
  commit
  checkout main
  merge develop
```

### Timeline
Chronological events, milestones.

**Syntax:**
```
timeline
  2024 : Event A : Event B
  2025 : Event C
```

### Packet Diagram
Network protocols, structures.

**Syntax:**
```
packet-beta
  0-15: "Header"
  16-31: "Data"
```

### ZenUML Sequence
Alternative sequence syntax.

**Syntax:**
```
zenuml
  A.method() {
    B.process()
    return result
  }
```

### Mindmap
Brainstorming, hierarchies.

**Syntax:**
```
mindmap
  root((Central Idea))
    Branch 1
      Sub 1
      Sub 2
    Branch 2
```

### Requirement Diagram
SysML requirements, traceability.

**Syntax:**
```
requirementDiagram
  requirement req1 {
    id: R1
    text: User shall login
    risk: Medium
  }
```

## Quick Reference

| Type | Best For | Complexity |
|------|----------|------------|
| Architecture | Cloud/infra systems | High |
| C4 | Context/container views | Medium |
| Git Graph | Branch strategy docs | Low |
| Mindmap | Brainstorming sessions | Low |
| Pie/XY/Radar | Data visualization | Low |
| Timeline | Event/milestone docs | Low |
| Kanban | Task board workflows | Medium |
| Packet | Network protocol docs | Medium |
