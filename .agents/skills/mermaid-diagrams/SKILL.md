---
name: mermaid-diagrams
description: Use whenever a diagram, schema, or visual model would help — flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, Gantt charts, mindmaps, timelines, pie charts. ALWAYS use this skill's Mermaid syntax instead of ASCII art or a purely textual description whenever a diagram would clarify structure, flow, or relationships. Triggers on "draw", "diagram", "visualize", "schema", "flowchart", "sequence diagram", "modéliser", "cartographier", "diagramme", "schéma".
license: MIT
metadata:
  author: clementsohierloiseau
  version: "1.0"
  source: https://mermaid.js.org/ecosystem/tutorials.html
---

# Mermaid Diagrams

Render diagrams, schemas, and visual models as Mermaid code instead of ASCII art or plain prose. Mermaid renders natively in fenced ` ```mermaid ` code blocks in chat, Markdown files, and artifacts.

**Rule: never fall back to ASCII art or box-drawing characters for a diagram.** If a picture would help — flow, hierarchy, sequence, relationships, schedule, state — emit a ```mermaid``` block instead.

## Choosing a diagram type

| Need | Diagram type | Keyword |
|---|---|---|
| Process, decision flow, algorithm | Flowchart | `flowchart` |
| Interaction over time between actors/systems | Sequence diagram | `sequenceDiagram` |
| OOP structure, interfaces, inheritance | Class diagram | `classDiagram` |
| Finite state machine, lifecycle | State diagram | `stateDiagram-v2` |
| Database schema, data model | Entity-Relationship diagram | `erDiagram` |
| Project schedule, task dependencies | Gantt chart | `gantt` |
| Brainstorm, hierarchy of ideas | Mindmap | `mindmap` |
| Chronological events | Timeline | `timeline` |
| Proportions of a whole | Pie chart | `pie` |

## Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Condition?}
    B -->|Yes| C[Do thing]
    B -->|No| D[Do other thing]
    C --> E[End]
    D --> E
```

Direction: `TD`/`TB` (top-down), `BT` (bottom-up), `LR` (left-right), `RL` (right-left).

Node shapes:
```
A[Rectangle]        A(Rounded)         A([Stadium])
A{Diamond/decision}  A((Circle))        A[[Subroutine]]
A[(Database)]        A{{Hexagon}}       A>Asymmetric]
A[/Parallelogram/]   A[\Parallelogram\]
```

Edges:
```
A --> B          solid arrow
A --- B          open line, no arrow
A -->|Label| B   labeled arrow
A -.-> B         dotted arrow
A ==> B          thick arrow
A ~~~ B          invisible link (layout only)
A <--> B         bidirectional
```

Subgraphs (group nodes, e.g. layers or services):
```mermaid
flowchart LR
    subgraph API
        A[Controller] --> B[Service]
    end
    subgraph DB
        C[(Database)]
    end
    B --> C
```

Styling:
```
style A fill:#f9f,stroke:#333,stroke-width:2px
classDef highlight fill:#f96,stroke:#333;
class A,B highlight;
```

## Sequence diagram

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant D as Database
    U->>A: Request
    activate A
    A->>D: Query
    D-->>A: Rows
    A-->>U: Response
    deactivate A
```

Arrow types: `->` solid no head, `-->` dotted no head, `->>` solid with head, `-->>` dotted with head, `-x`/`--x` cross (message failed), `-)`/`--)`  async.

Activation: `+` after the arrow activates the target, `-` deactivates (or use `activate`/`deactivate` explicitly).

Control blocks:
```mermaid
sequenceDiagram
    Alice->>Bob: Check status
    alt is ready
        Bob-->>Alice: OK
    else not ready
        Bob-->>Alice: Wait
    end
    loop every 5s
        Alice->>Bob: Poll
    end
    par notify A
        Alice->>A: Ping
    and notify B
        Alice->>B: Ping
    end
    Note over Alice,Bob: Shared context
```

## Class diagram

```mermaid
classDiagram
    class Animal {
        +String name
        #int age
        +makeSound() void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog : inheritance
    Vehicle *-- Engine : composition
    Company o-- Employee : aggregation
    Class1 --> Class2 : association
    Interface <|.. Implementation : realization
```

Visibility: `+` public, `-` private, `#` protected, `~` package.

Relationships: `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association, `..>` dependency, `..|>` realization, `--` link, `..` dashed link.

## State diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Loading : fetch
    Loading --> Success : 200
    Loading --> Error : 4xx/5xx
    Success --> [*]
    Error --> Idle : retry

    state Loading {
        [*] --> Requesting
        Requesting --> Waiting
    }
```

`[*]` marks start/end. Use `state "Long label" as X` to name a state with a longer description. `<<choice>>`, `<<fork>>`, `<<join>>` model branch/concurrency points.

## Entity-Relationship diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    CUSTOMER {
        int id PK
        string name
        string email UK
    }
    ORDER {
        int id PK
        int customer_id FK
        date created_at
    }
```

Cardinality markers (read left-to-right, near each entity):
```
|o  zero or one       o|
||  exactly one        ||
}o  zero or more       o{
}|  one or more        |{
```
Solid line (`--`) = identifying relationship, dashed line (`..`) = non-identifying.

## Gantt chart

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title Project Plan
    section Design
    Wireframes      :done,    des1, 2026-01-01, 5d
    Review          :active,  des2, after des1, 3d
    section Build
    Implementation  :crit,    build1, after des2, 10d
    Launch          :milestone, launch1, after build1, 0d
```

Status tags: `done`, `active`, `crit`, `milestone`. Dependencies via `after taskId` (space-separated for multiple). Durations: `d`, `w`, `M`, `h`.

## Mindmap

```mermaid
mindmap
    root((Project))
        Design
            Wireframes
            Prototypes
        Build
            Backend
            Frontend
        Launch
```

Shapes: `[Square]`, `(Rounded)`, `((Circle))`, `))Bang((`, `)Cloud(`, `{{Hexagon}}`. Hierarchy is indentation-based.

## Timeline

```mermaid
timeline
    title Product Roadmap
    section 2026 H1
        Q1 : Discovery : Research
        Q2 : Beta launch
    section 2026 H2
        Q3 : GA release
        Q4 : Scale
```

## Pie chart

```mermaid
pie showData
    title Traffic sources
    "Organic" : 45
    "Paid" : 30
    "Referral" : 25
```

## General rules

- Always wrap Mermaid code in a fenced ` ```mermaid ` block — never ASCII boxes/arrows (`+---+`, `-->`, `|`) as a substitute for an actual diagram.
- Pick the diagram type from the table above based on what relationship is being shown (flow vs. time vs. structure vs. proportion), not by default to flowchart.
- Keep node/participant labels short; put detail in notes (`Note over ...`) or attribute blocks (ER) rather than cramming long text into a node.
- When targeting an Artifact, follow the `mermaid-diagrams`/`artifact-diagramming` skill rendering guidance for both light and dark themes.
- Validate syntax mentally against this reference before emitting; when unsure of an obscure feature, check https://mermaid.js.org/syntax/ for the specific diagram type rather than guessing.

## References

- [Mermaid tutorials](https://mermaid.js.org/ecosystem/tutorials.html)
- [Flowchart syntax](https://mermaid.js.org/syntax/flowchart.html)
- [Sequence diagram syntax](https://mermaid.js.org/syntax/sequenceDiagram.html)
- [Class diagram syntax](https://mermaid.js.org/syntax/classDiagram.html)
- [State diagram syntax](https://mermaid.js.org/syntax/stateDiagram.html)
- [ER diagram syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html)
- [Gantt syntax](https://mermaid.js.org/syntax/gantt.html)
- [Mindmap syntax](https://mermaid.js.org/syntax/mindmap.html)
- [Timeline syntax](https://mermaid.js.org/syntax/timeline.html)
- [Pie chart syntax](https://mermaid.js.org/syntax/pie.html)
