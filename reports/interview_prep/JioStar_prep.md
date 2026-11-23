# 🎯 Dynamic Interview Preparation Guide: JioStar
### Role: Software Development Engineer II - Web
**Candidate:** Roshan Moger (2+ Years Experience)
**Target Location:** Bengaluru, Karnataka | **Required Level:** 2-4 Years (SDE 2 / Web)
**Industry Domain:** Devtools Realtime
**Domain Focus:** Bi-directional WebSockets, connection heartbeat & auto-reconnect, message delivery guarantees, horizontal socket scaling with Redis pub/sub.

---

## 📊 1. Resume Alignment & Skill Match Analysis
### ✅ Direct Matches from Your Resume:
- **React.js**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.
- **TypeScript**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.
- **WebSockets**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.
- **Tailwind CSS**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.

### 🔍 Gaps & Areas to Brush Up Based on Your Resume:
- **Next.js**:
  - *Your Resume Bridge:* You have deep React.js, TypeScript, and Redux experience.
  - *What to Review Before Interview:* Review Next.js 14/15 App Router: Server Components vs Client Components (`'use client'`), Incremental Static Regeneration (ISR), and route handlers.
- **Jest**:
  - *Your Resume Bridge:* You write unit and integration tests across React components and backend API endpoints.
  - *What to Review Before Interview:* Review React Testing Library query priority (`getByRole`), mocking API requests (MSW), and E2E test assertions with Playwright/Cypress.
- **Playwright**:
  - *Your Resume Bridge:* You write unit and integration tests across React components and backend API endpoints.
  - *What to Review Before Interview:* Review React Testing Library query priority (`getByRole`), mocking API requests (MSW), and E2E test assertions with Playwright/Cypress.

---

## 🚀 2. Tailored STAR Stories (Ready to Speak)
### Redis Distributed Caching to Eliminate Latency (JioStar Application)
- **Situation:** On ExcelSoft's assessment platforms, peak traffic caused heavy database read contention. For a high-throughput environment like JioStar, database bottlenecks degrade user experience.
- **Task:** Cut database round-trips by >60% and ensure sub-150ms API responses under concurrent user load.
- **Action:** Designed a Redis distributed caching layer in ASP.NET Core with TTL policies and reactive cache invalidation. Engineered cache-aside patterns with fallback to relational queries.
- **Result:** Reduced direct database hits significantly and maintained 99.9% uptime during peak concurrent activity.
> 💡 **Winning Pitch Line:** 'At ExcelSoft, I engineered Redis caching to handle massive concurrent traffic spikes, which directly translates to JioStar's requirement for scalable, low-latency services.'

### Sub-Second Live Data Streaming with WebSockets (JioStar Focus)
- **Situation:** Online platforms require real-time updates without the network overhead and delay of recurring HTTP polling.
- **Task:** Build a responsive bi-directional event stream between React frontends and backend services.
- **Action:** Implemented WebSocket connection managers with exponential backoff auto-reconnect, custom React hooks (`useWebSocket`), and heartbeat ping/pong monitoring.
- **Result:** Achieved sub-second alert broadcasts while eliminating thousands of redundant polling requests.
> 💡 **Winning Pitch Line:** 'My experience building real-time WebSocket pipelines allows me to implement instant, reliable user interactions for JioStar's digital products.'

### JWT Token Rotation & Route-Level RBAC (JioStar Standard)
- **Situation:** Multi-role enterprise platforms require strict authorization boundaries without degrading user session fluidity.
- **Task:** Develop an end-to-end security pipeline bridging ASP.NET Core / Node.js with React route protection.
- **Action:** Configured short-lived JWT access tokens with secure HTTP-only refresh tokens, Axios interceptors for silent refresh on 401s, and React Higher-Order Components checking role claims.
- **Result:** Prevented unauthorized data access while ensuring zero unexpected session expirations for active users.
> 💡 **Winning Pitch Line:** 'I design secure, enterprise-grade authentication and RBAC systems that protect sensitive data while maintaining smooth user sessions at JioStar.'

---

## 💻 3. High-Probability Technical Questions & Answers
### Q1: How do you horizontally scale WebSocket connections across multiple backend servers?
**Model Answer (2+ Years Perspective):**
> Use a distributed Pub/Sub message broker like Redis or RabbitMQ. When client A connects to Server 1 and client B connects to Server 2, Server 1 publishes messages to a Redis channel, and Server 2 receives and broadcasts them to client B. Sticky sessions or socket clustering via AWS ALB ensure stable socket routing.

### Q2: How do you handle dropped connections and message ordering on the client?
**Model Answer (2+ Years Perspective):**
> Implement exponential backoff reconnection in a custom React hook. Assign monotonically increasing sequence IDs to messages. When reconnected, the client transmits the last received message ID so the server can replay missed events from an ephemeral cache (Redis stream).

### Q3: How do you prevent memory leaks when managing WebSockets in React components?
**Model Answer (2+ Years Perspective):**
> Always clean up listeners and close connections in the `useEffect` cleanup return function: `return () => { socket.close(); socket.removeEventListener(...); };`. Avoid capturing stale state closures by using `useRef` or updater functions inside state setters.

---

## 🏗️ 4. System Design & Architectural Challenge
**Challenge:** Design a Resilient Real-Time Event & Notification Streaming Platform.
- **How to structure your solution:**
  1. Clarify functional and non-functional requirements (throughput, availability, latency).
  2. Outline API endpoints and data contracts (REST/WebSockets).
  3. Design storage tier: Primary SQL/NoSQL DB + Redis caching layer for hot reads.
  4. Address failure modes: Retries with exponential backoff, circuit breakers, and rate limiting.

---

## 🙋 5. Reverse Interview Questions (Ask the Interviewer)
- *"What does the engineering architecture look like at JioStar for this team, and how are frontend and backend responsibilities coordinated?"*
- *"How does JioStar approach testing and continuous deployment (CI/CD) for production releases?"*
- *"What is the biggest technical challenge or scaling goal this team is looking to solve over the next 6 months?"*
- *"What does career growth and mentorship look like for an engineer with 2+ years of experience coming into JioStar?"*