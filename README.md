# CDDX — Cross-Domain Distributed Exchange

**A federated database system enabling secure cross-cluster queries while maintaining strict data ownership boundaries.**

---

## 🎯 The Problem

Organizations with distributed databases face a fundamental challenge: how do you query data across independent systems without violating data sovereignty?

**Traditional solutions fail because they either:**
- Replicate data everywhere (violates ownership, increases breach surface)
- Require tight coupling between systems (brittle, hard to scale)
- Use broadcast queries (inefficient, O(n) complexity)
- Sacrifice performance for federation (unusable for operational queries)

**CDDX solves this with a lightweight pointer registry.**

---

## 💡 How It Works

CDDX uses a **Central Registry Server** that acts as a phonebook for your data:

1. **Entity Created** → Cluster registers ownership in central registry
2. **Entity Detected** → Other cluster queries registry: "Who owns this?"
3. **Pointer Returned** → Registry responds with owner's address
4. **Data Fetched** → Requesting cluster contacts owner directly
5. **No Replication** → Data never leaves the owning cluster permanently

**Key principle:** The registry knows *where* data lives, never *what* the data is.

---

## 🏗️ Architecture

### System Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Central Registry Server (CRS)** | Pointer lookup service | FastAPI (Python) |
| **etcd** | Durable pointer storage | Raft consensus |
| **Redis** | Hot lookup cache (sub-ms latency) | In-memory KV store |
| **Cluster Nodes** | Independent database owners | FastAPI + PostgreSQL |
| **Docker Compose** | Container orchestration | Docker |

### Data Flow

```
╔═══════════════╗         ╔═══════════════╗         ╔═══════════════╗
║   AEGIS       ║         ║     CRS       ║         ║   WINSTON     ║
║   Cluster     ║         ║  (Registry)   ║         ║   Cluster     ║
║               ║         ║               ║         ║               ║
║  PostgreSQL   ║         ║  etcd+Redis   ║         ║  PostgreSQL   ║
╚═══════════════╝         ╚═══════════════╝         ╚═══════════════╝
        │                         │                         │
        │                         │                         │
        │  1. Register Entity     │                         │
        ├────────────────────────>│                         │
        │                         │                         │
        │                         │  2. Detect Entity       │
        │                         │<────────────────────────┤
        │                         │                         │
        │                         │  3. Return: "Aegis      │
        │                         │     owns it at 8001"    │
        │                         ├────────────────────────>│
        │                         │                         │
        │  4. Fetch Data          │                         │
        │<────────────────────────────────────────────────────┤
        │                         │                         │
        │  5. Return Entity       │                         │
        ├────────────────────────────────────────────────────>│
        │                         │                         │
```

---

## 🚀 Key Features

✅ **Zero Data Replication** — Entities never leave their home cluster  
✅ **O(1) Lookup** — Registry lookup via cached pointers  
✅ **Strict Ownership** — Only owning cluster can modify data  
✅ **Auto-Registration** — Entities register on creation  
✅ **Cross-Cluster Queries** — Fetch foreign entities seamlessly  
✅ **Horizontal Scalability** — Add clusters without coordination  
✅ **Persistent Storage** — Docker volumes ensure data survival  

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **CRS Lookup (cached)** | < 1ms |
| **CRS Lookup (cold)** | < 50ms |
| **Cross-Cluster Query** | < 200ms |
| **Entity Registration** | < 100ms |
| **Cache Hit Rate** | > 85% (after warmup) |
| **Running Services** | 7 containers |

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** — Async Python web framework
- **PostgreSQL** — Relational database for entity storage
- **etcd** — Distributed KV store with Raft consensus
- **Redis** — In-memory cache for hot lookups

### Infrastructure
- **Docker & Docker Compose** — Containerization & orchestration
- **Uvicorn** — ASGI server for FastAPI apps

### Patterns & Principles
- RESTful API design with OpenAPI documentation
- Microservices architecture with service isolation
- Two-tier caching (Redis → etcd)
- Eventual consistency with strong ownership semantics

---

## 📐 API Overview

### Aegis/Winston (Cluster APIs)

**POST /entities** — Create new entity  
**GET /entities** — List all owned entities  
**GET /entities/{id}** — Fetch specific entity  
**PUT /entities/{id}** — Update entity  
**DELETE /entities/{id}** — Delete entity  
**GET /detect/{id}** — Detect and fetch cross-cluster entity  

### CRS (Registry API)

**POST /register** — Register entity pointer  
**GET /lookup/{id}** — Lookup entity owner  

---

## 🧩 Use Cases

### Government & Law Enforcement
Multi-jurisdictional data sharing while respecting sovereignty. Example: City police detect suspect from neighboring county → automatic lookup → fetch warrant info → maintain audit trail.

### Healthcare Networks
Patient data sharing across facilities with HIPAA compliance. Home hospital owns record, visiting ER queries only necessary info.

### Financial Services
Cross-border fraud detection without centralizing sensitive data. Transaction risk scoring leverages account history across institutions.

### Supply Chain
Multi-party tracking with proprietary data protection. Downstream partners verify shipments without accessing supplier secrets.

---

## 🔒 Design Principles

**1. Data Sovereignty First**  
Only the owning cluster can write entity data. The registry is read-only for external clusters.

**2. No Replication**  
Cross-cluster queries fetch data on-demand. Requesting cluster never stores foreign entities permanently.

**3. Explicit Ownership**  
Every entity has exactly one owner. Ownership transfer requires formal protocol (future work).

**4. Fail-Safe**  
If registry is unavailable, cross-cluster queries block rather than risk data leakage.

**5. Horizontal Scalability**  
New clusters join by registering with CRS. No reconfiguration of existing clusters required.

---

## 🎓 What I Learned

Building CDDX taught me:

- **Distributed Systems Design** — CAP theorem tradeoffs, consistency models, consensus protocols
- **Microservices Architecture** — Service isolation, API contracts, inter-service communication
- **Database Engineering** — Schema design, query optimization, persistence strategies
- **Container Orchestration** — Docker networking, volume management, multi-service coordination
- **API Design** — RESTful principles, OpenAPI documentation, error handling
- **Caching Strategies** — Two-tier caching, cache invalidation, TTL management
- **System Tradeoffs** — Balancing latency vs consistency, complexity vs simplicity

---

## 🚧 Future Work

**Security Layer (Phase 5)**  
- SPIFFE/SPIRE for cryptographic cluster identity
- mTLS for inter-cluster communication
- Open Policy Agent for fine-grained access control

**Event Pipelines (Phase 6)**  
- Kafka integration for async coordination
- Sighting notifications across clusters
- Event replay and audit capabilities

**Production Hardening (Phase 7)**  
- Multi-region CRS with Raft replication
- Horizontal cluster scaling
- Disaster recovery automation
- Comprehensive observability (Prometheus, Grafana, Jaeger)

---

## 🏆 Why This Matters

**For Organizations:**  
Enables data sharing across boundaries without sacrificing sovereignty, compliance, or security.

**For Infrastructure:**  
Demonstrates practical application of distributed systems patterns in a real-world scenario.

**For Learning:**  
Comprehensive implementation of concepts typically only taught theoretically in CS courses.

---

## 🤝 Competitive Landscape

**vs. Presto/Trino:** CDDX is operational-first (real-time queries) vs analytics-focused  
**vs. Denodo/TIBCO:** Lightweight and ownership-aware vs expensive enterprise virtualization  
**vs. CockroachDB/YugabyteDB:** Federated independent DBs vs single distributed database  
**vs. Blockchain:** Practical query performance vs immutable audit trail  

**Unique Value:** Strict ownership semantics enforced at infrastructure layer, not just policy.

---

## 📧 About author

**Project by:** Ansh Deotale  
**LinkedIn:** https://www.linkedin.com/in/ansh-deotale/  
**GitHub:** https://github.com/AnshDeotale04

**Interested in distributed systems, database engineering, data handling and cloud infrastructure.**

---

## 📄 License

This documentation is provided for portfolio and educational purposes. The implementation is proprietary.

---

**⭐ If you find this architecture interesting, consider starring the repo!**
