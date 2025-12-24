# PKMS System Diagram (Mermaid)

## Table of Contents

- [PKMS System Diagram (Mermaid)](#pkms-system-diagram-mermaid)
  - [Table of Contents](#table-of-contents)
  - [Overview Diagram](#overview-diagram)
  - [Diagram](#diagram)
  - [How to Read This Diagram](#how-to-read-this-diagram)
    - [Vertical Flow = Lifecycle](#vertical-flow--lifecycle)
    - [Horizontal Separation = Responsibility](#horizontal-separation--responsibility)
  - [Key Design Insights Captured](#key-design-insights-captured)
    - [1. Filesystem as a Hard Boundary](#1-filesystem-as-a-hard-boundary)
    - [2. IndexedDocument Boundary](#2-indexeddocument-boundary)
    - [3. Knowledge Linking Is Orthogonal](#3-knowledge-linking-is-orthogonal)
    - [4. Addressing ≠ Retrieval](#4-addressing--retrieval)

## Overview Diagram

```mermaid
flowchart LR
    subgraph External
        ER[External Resource]
    end

    subgraph PKMS
        F[Fetcher]
        ORS[Owned Resource Storage]
        G[Globber]
        I[Indexer]
        U[Upserter]
        DB[(Index DB)]
        S[Search]
        V[Viewer]
        L[Linking]
    end

    ER -->|Acquire| F
    F -->|Store| ORS
    ORS -->|Discover| G
    G --> I
    I -->|IndexedDocument| U
    U --> DB

    DB --> S
    DB --> L
    ORS --> V
```

## Diagram

> This diagram illustrates the **conceptual system architecture** of PKMS, focusing on responsibilities and boundaries rather than implementation details.

```mermaid
flowchart TB
    %% =========================
    %% External World
    %% =========================
    External["External Systems<br/>(Web, APIs, Chat Apps, Feeds)"]
    User[User / Automation]

    %% =========================
    %% Acquisition
    %% =========================
    subgraph Acquisition["1. Resource Acquisition"]
        Fetcher[Fetcher]
        Scheduler[Scheduler / Policy]
    end

    %% =========================
    %% Owned Storage
    %% =========================
    FS[(Local Filesystem<br/>Owned Resource Storage)]

    %% =========================
    %% Ingestion Pipeline
    %% =========================
    subgraph Ingestion["2. Resource Ingestion"]
        Globber[Globber]
        Indexer[Indexer]
        Upserter[Upserter]
    end

    %% =========================
    %% Indexed Storage
    %% =========================
    DB[(Indexed Storage<br/>SQLite)]

    %% =========================
    %% Retrieval
    %% =========================
    subgraph Retrieval["3. Resource Retrieval"]
        Searcher[Searcher]
        QueryAPI[Query API]
    end

    %% =========================
    %% Knowledge Layer
    %% =========================
    subgraph Knowledge["4. Knowledge Linking"]
        Graph[Relations / Graph]
    end

    %% =========================
    %% Addressing & Presentation
    %% =========================
    subgraph Addressing["5. Addressing/Presentation"]
        URIResolver[PKMS URI Resolver]
        Handler[URI / URL Handler]
        Viewer[Viewer / External App]
    end

    %% =========================
    %% Flows
    %% =========================
    External --> Fetcher
    User --> Fetcher
    Scheduler --> Fetcher

    Fetcher --> FS

    FS --> Globber
    Globber --> Indexer
    Indexer --> Upserter
    Upserter --> DB

    DB --> Searcher
    Searcher --> QueryAPI
    QueryAPI --> User

    DB --> Graph
    Graph --> QueryAPI

    User --> URIResolver
    URIResolver --> Handler
    Handler --> Viewer
    Handler --> FS
    Handler --> DB
```


## How to Read This Diagram

### Vertical Flow = Lifecycle

- Top → Bottom represents the **resource lifecycle**
- Acquisition happens before Ingestion
- Ingestion produces Indexed Storage
- Retrieval and Linking are read-only consumers

### Horizontal Separation = Responsibility

Each subgraph is a **conceptual capability boundary**, not a module boundary.

## Key Design Insights Captured

### 1\. Filesystem as a Hard Boundary

- Acquisition writes to FS
- Ingestion reads from FS
- No hidden backchannels

### 2\. IndexedDocument Boundary

- Everything between Indexer → Upserter → DB operates on structured contracts
- No direct FS access after ingestion

### 3\. Knowledge Linking Is Orthogonal

- Graph does not depend on file layout
- Relations survive file moves / renames

### 4\. Addressing ≠ Retrieval

- URI resolution may touch FS or DB
- Search never opens files
- Viewers never index content
