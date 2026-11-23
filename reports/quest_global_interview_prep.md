# Quest Global Interview Preparation Pack

## Role: Fullstack Developer (.NET Core, React, AWS)

**Candidate:** Roshan Moger | 2+ Years Experience (Associate Software Engineer)  
**Location:** Bengaluru, Karnataka  
**Target Tech Stack:** React.js, TypeScript, ASP.NET Core, C#, AWS, Docker, Kubernetes, Redis, WebSockets

---

## 1. Interview Stage Breakdown

| Stage                                  | Focus Area                                     | Key Evaluation Criteria                                                                           |
| :------------------------------------- | :--------------------------------------------- | :------------------------------------------------------------------------------------------------ |
| **Round 1: Technical Screening**       | Experience Walkthrough & Fundamentals          | Clarity of communication, depth in React/.NET Core, current role contributions at ExcelSoft.      |
| **Round 2: Technical Deep Dive**       | C#/.NET Core + React.js + State Management     | Clean architecture, DI, async/await, EF Core, component lifecycle, hooks, Redux, JWT/RBAC.        |
| **Round 3: System Design & Cloud**     | Scalability, Caching, AWS & Docker             | Redis caching strategies, WebSockets real-time sync, microservices design, AWS EC2/S3/RDS/Lambda. |
| **Round 4: Engineering Manager Round** | Agile, Code Reviews, STAR Behavioral Scenarios | Production incident resolution, cross-functional collaboration, ownership, sprint velocity.       |

---

## 2. Tailored STAR Stories for Roshan Moger

### Story 1: High-Concurrency Redis Caching & Query Optimization

- **Situation:** On ExcelSoft's Saras Standard Platform, thousands of candidates take synchronized assessments simultaneously. High-frequency queries for test structures and question banks caused database contention and latency spikes.
- **Task:** Offload recurring read traffic from the primary SQL database and keep API response times under 150ms during peak windows.
- **Action:** Analyzed slow API endpoints using APM tools and implemented a distributed Redis caching layer in ASP.NET Core. Designed time-to-live (TTL) expiration strategies combined with proactive cache invalidation whenever administrators published test modifications.
- **Result:** Drastically lowered redundant database reads, stabilized API response times, and ensured 99.9% uptime during high-stakes exam launches.
- **Use when asked:** _"Tell me about a time you optimized backend performance,"_ or _"How do you design caching in distributed systems?"_

### Story 2: Real-Time Event Telemetry using WebSockets

- **Situation:** The proctoring system required immediate telemetry on student connectivity, tab switches, and live test status. Initial HTTP polling intervals consumed unnecessary server bandwidth and created noticeable alert delays.
- **Task:** Engineer a low-overhead, bi-directional communication channel between the React frontend and backend services.
- **Action:** Implemented a WebSocket connection manager with heartbeat ping/pong, exponential backoff reconnection, and custom React hooks (`useWebSocket`) to subscribe components directly to live event streams.
- **Result:** Reduced alert delivery latency to sub-second levels while eliminating thousands of redundant HTTP polling requests per minute per active test room.
- **Use when asked:** _"Describe a complex frontend feature you implemented,"_ or _"How do you handle real-time data streaming?"_

### Story 3: JWT Token Rotation and Role-Based Route Security (RBAC)

- **Situation:** The multi-tenant EdTech platform hosted distinct user tiers (Students, Evaluators, Proctors, Super Admins), requiring airtight authorization and seamless session renewal without intrusive logouts.
- **Task:** Build an end-to-end security pipeline bridging ASP.NET Core policy enforcement with React client-side route guards.
- **Action:** Configured ASP.NET Core middleware to issue short-lived JWT access tokens and secure HTTP-only refresh tokens. On the frontend, created Axios request/response interceptors to automatically catch 401 errors, invoke the refresh endpoint silently, and retry failed requests. Wrapped sensitive view hierarchies in Higher-Order Components (HOCs) checking user claims against defined permissions.
- **Result:** Secured all sensitive administrative APIs while delivering a frictionless user session experience across uninterrupted exam windows.
- **Use when asked:** _"How do you implement authentication and security across a full-stack application?"_

### Story 4: Containerized Microservices on AWS Infrastructure

- **Situation:** Discrepancies between local development setups, staging environments, and production AWS infrastructure occasionally introduced deployment defects.
- **Task:** Standardize service deployment artifacts and configure cloud-native infrastructure.
- **Action:** Multi-stage Dockerized the React single-page apps (served via Nginx) and ASP.NET Core API services. Configured Kubernetes deployment manifests and provisioned AWS services including EC2 instances, RDS managed databases, S3 object storage for assets, and CloudWatch alerts for centralized logging.
- **Result:** Achieved 100% environment parity, simplified zero-downtime rolling updates, and reduced deployment cycle times.
- **Use when asked:** _"Tell me about your experience with Docker, Kubernetes, and AWS."_

---

## 3. High-Probability Technical Questions & Model Answers

### Q1: "How does Dependency Injection work in ASP.NET Core, and what is the difference between Transient, Scoped, and Singleton?"

**Model Answer:**

> "ASP.NET Core has built-in Inversion of Control (IoC). In `Program.cs`, we register services with the `IServiceCollection`:
>
> - **Transient (`AddTransient`):** A new instance is created every time it is requested. Ideal for lightweight, stateless utilities.
> - **Scoped (`AddScoped`):** A single instance is created per client request (HTTP context). This is standard for DbContext and repository layers so all services in that HTTP request share the same transaction context.
> - **Singleton (`AddSingleton`):** Created once on initial request or application start and shared across the entire application lifecycle. Used for in-memory caches, configuration wrappers, or thread-safe logging services.
>   It's critical never to inject a Scoped service into a Singleton, as that can lead to captive dependencies and memory leaks."

### Q2: "How do you optimize rendering performance in React.js when state changes frequently?"

**Model Answer:**

> "In React, unnecessary re-renders are usually mitigated through architectural and API practices:
>
> 1. **State Colocation:** Keep state as close as possible to the leaf components that actually need it, preventing upper tree re-renders.
> 2. **Memoization:** Wrap expensive child components in `React.memo`, and memoize complex calculations with `useMemo` and callbacks passed to children with `useCallback`.
> 3. **Proper Key Usage:** Never use array indices as keys when list items can reorder, insert, or delete.
> 4. **Windowing / Virtualization:** For large data tables (like candidate lists), use libraries like `react-window` to render only elements currently inside the viewport."

### Q3: "What is your approach to handling database transactions and concurrency in EF Core / SQL Server?"

**Model Answer:**

> "In EF Core, `DbContext.SaveChanges()` executes within a transaction by default. For multi-step business flows spanning multiple repositories, I wrap the operations in an explicit `BeginTransactionAsync()`. To handle concurrent updates (such as two admins editing the same exam schedule simultaneously), I use **optimistic concurrency control** via row versioning (`[Timestamp]` byte array column). If EF Core detects a concurrency conflict, it throws a `DbUpdateConcurrencyException`, allowing our API to catch it and notify the client to refresh and resolve the conflict cleanly."

### Q4: "How do you secure API secrets and configuration across environments in AWS?"

**Model Answer:**

> "I never store sensitive secrets or connection strings in Git repositories or Docker images. In development, I use `appsettings.Development.json` or .NET User Secrets. In AWS production environments, I use **AWS Systems Manager Parameter Store** or **AWS Secrets Manager**, retrieving connection strings and API keys at runtime via IAM role-based authentication without hardcoded credentials. Non-sensitive environment variables are injected through Kubernetes ConfigMaps."

---

## 4. Reverse Interview Questions (Questions Roshan Can Ask Quest Global)

1. _"What does the microservices topology look like at Quest Global for this project, and are you using event-driven architectures (like Kafka or AWS SQS) between .NET services?"_
2. _"How does the engineering team balance building new business features versus addressing technical debt and upgrading framework versions?"_
3. _"What does the CI/CD pipeline and release cadence look like for full-stack deployments on your AWS infrastructure?"_
4. _"What opportunities are there within the engineering team for mentorship and taking ownership of end-to-end architecture decisions?"_
