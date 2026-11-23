# 🎯 Dynamic Interview Preparation Guide: TechTorch
### Role: Salesforce Developer
**Candidate:** Roshan Moger (2.5+ Years Experience)
**Target Location:** India | **Required Level:** 1-3 Years (Associate)
**Industry Domain:** Devsecops Saas
**Domain Focus:** Multi-tenant isolation, background job queues, GraphQL/REST API design, worker claiming & concurrency, Docker/Kubernetes container orchestration.

---

## 📊 1. Resume Alignment & Skill Match Analysis
### ✅ Direct Matches from Your Resume:
- **REST APIs**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.

---

## 🚀 2. Tailored STAR Stories (Ready to Speak)
### Redis Distributed Caching to Eliminate Latency (TechTorch Application)
- **Situation:** On ExcelSoft's assessment platforms, peak traffic caused heavy database read contention. For a high-throughput environment like TechTorch, database bottlenecks degrade user experience.
- **Task:** Cut database round-trips by >60% and ensure sub-150ms API responses under concurrent user load.
- **Action:** Designed a Redis distributed caching layer in ASP.NET Core with TTL policies and reactive cache invalidation. Engineered cache-aside patterns with fallback to relational queries.
- **Result:** Reduced direct database hits significantly and maintained 99.9% uptime during peak concurrent activity.
> 💡 **Winning Pitch Line:** 'At ExcelSoft, I engineered Redis caching to handle massive concurrent traffic spikes, which directly translates to TechTorch's requirement for scalable, low-latency services.'

### Sub-Second Live Data Streaming with WebSockets (TechTorch Focus)
- **Situation:** Online platforms require real-time updates without the network overhead and delay of recurring HTTP polling.
- **Task:** Build a responsive bi-directional event stream between React frontends and backend services.
- **Action:** Implemented WebSocket connection managers with exponential backoff auto-reconnect, custom React hooks (`useWebSocket`), and heartbeat ping/pong monitoring.
- **Result:** Achieved sub-second alert broadcasts while eliminating thousands of redundant polling requests.
> 💡 **Winning Pitch Line:** 'My experience building real-time WebSocket pipelines allows me to implement instant, reliable user interactions for TechTorch's digital products.'

### JWT Token Rotation & Route-Level RBAC (TechTorch Standard)
- **Situation:** Multi-role enterprise platforms require strict authorization boundaries without degrading user session fluidity.
- **Task:** Develop an end-to-end security pipeline bridging ASP.NET Core / Node.js with React route protection.
- **Action:** Configured short-lived JWT access tokens with secure HTTP-only refresh tokens, Axios interceptors for silent refresh on 401s, and React Higher-Order Components checking role claims.
- **Result:** Prevented unauthorized data access while ensuring zero unexpected session expirations for active users.
> 💡 **Winning Pitch Line:** 'I design secure, enterprise-grade authentication and RBAC systems that protect sensitive data while maintaining smooth user sessions at TechTorch.'

### MCP Server in .NET & Gemini LLM Chatbot (TechTorch Application)
- **Situation:** Enterprise platforms need to bridge internal SaaS workflows and proprietary data with Generative AI systems without compromising security boundaries.
- **Task:** Expose SaaS platform data and workflows to AI agents and build an in-product conversational assistant using Google Gemini via AWS Bedrock.
- **Action:** Designed and implemented an MCP server using .NET to standardize SaaS capabilities into agentic tools. Integrated Google Gemini (via AWS Bedrock) alongside internal AI models with strict prompt guardrails and streaming telemetry.
- **Result:** Enabled conversational querying across assessment and compliance modules, dramatically streamlining reporting workflows.
> 💡 **Winning Pitch Line:** 'At ExcelSoft, I engineered an MCP server in .NET and integrated Google Gemini via AWS Bedrock, bringing cutting-edge agentic AI into production for TechTorch.'

---

## 💻 3. High-Probability Technical Questions & Answers
### Q1: How do you design a resilient background task and queue processing system?
**Model Answer (2+ Years Perspective):**
> Use a Redis-backed queue (such as BullMQ) or RabbitMQ with worker claiming, heartbeat checks, idempotency keys, and dead-letter queues (DLQ). Workers lock tasks atomically, process them with timeout limits, and release locks on completion to prevent duplicate execution upon worker crash.

### Q2: How do you prevent the N+1 problem in GraphQL APIs?
**Model Answer (2+ Years Perspective):**
> Use DataLoader batching and caching patterns. DataLoader coalesces individual item fetch requests made across a single execution tick into a single bulk query (e.g. `WHERE id IN (...)`), returning resolved promises mapped by entity ID.

### Q3: How do you enforce multi-tenant data security in full-stack applications?
**Model Answer (2+ Years Perspective):**
> Incorporate tenant ID claims directly inside JWT tokens. In ASP.NET Core / Node.js, apply global query filters (EF Core query filters or Prisma middleware) that automatically append `tenant_id = @currentTenant` to every query, preventing cross-tenant leakage.

---

## 🏗️ 4. System Design & Architectural Challenge
**Challenge:** Design a Scalable Multi-Tenant Job Runner & CI/CD Pipeline Dashboard.
- **How to structure your solution:**
  1. Clarify functional and non-functional requirements (throughput, availability, latency).
  2. Outline API endpoints and data contracts (REST/WebSockets).
  3. Design storage tier: Primary SQL/NoSQL DB + Redis caching layer for hot reads.
  4. Address failure modes: Retries with exponential backoff, circuit breakers, and rate limiting.

---

## 🙋 5. Reverse Interview Questions (Ask the Interviewer)
- *"What does the engineering architecture look like at TechTorch for this team, and how are frontend and backend responsibilities coordinated?"*
- *"How does TechTorch approach testing and continuous deployment (CI/CD) for production releases?"*
- *"What is the biggest technical challenge or scaling goal this team is looking to solve over the next 6 months?"*
- *"What does career growth and mentorship look like for an engineer with 2+ years of experience coming into TechTorch?"*