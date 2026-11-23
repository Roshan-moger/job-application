# 🎯 Dynamic Interview Preparation Guide: Freightos
### Role: React Developer
**Candidate:** Roshan Moger (2+ Years Experience)
**Target Location:** Chennai / Hybrid (Bengaluru Remote) | **Required Level:** 1-3 Years
**Industry Domain:** Freight Logistics
**Domain Focus:** High-volume booking engines, complex multi-currency calculation, real-time tracking dashboards, AWS CloudFront & S3 caching, automated test coverage (Jest/Cypress).

---

## 📊 1. Resume Alignment & Skill Match Analysis
### ✅ Direct Matches from Your Resume:
- **React.js**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.
- **Redux**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.
- **AWS (EC2, S3, RDS, Lambda, CloudWatch)**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.
- **REST APIs**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.

### 🔍 Gaps & Areas to Brush Up Based on Your Resume:
- **Jest**:
  - *Your Resume Bridge:* You write unit and integration tests across React components and backend API endpoints.
  - *What to Review Before Interview:* Review React Testing Library query priority (`getByRole`), mocking API requests (MSW), and E2E test assertions with Playwright/Cypress.
- **Cypress**:
  - *Your Resume Bridge:* You write unit and integration tests across React components and backend API endpoints.
  - *What to Review Before Interview:* Review React Testing Library query priority (`getByRole`), mocking API requests (MSW), and E2E test assertions with Playwright/Cypress.
- **CI/CD**:
  - *Your Resume Bridge:* Your strong full-stack foundations in React and C#/.NET Core allow fast ramp-up.
  - *What to Review Before Interview:* Review standard industry best practices and core API/architectural patterns for CI/CD.

---

## 🚀 2. Tailored STAR Stories (Ready to Speak)
### Redis Distributed Caching to Eliminate Latency (Freightos Application)
- **Situation:** On ExcelSoft's assessment platforms, peak traffic caused heavy database read contention. For a high-throughput environment like Freightos, database bottlenecks degrade user experience.
- **Task:** Cut database round-trips by >60% and ensure sub-150ms API responses under concurrent user load.
- **Action:** Designed a Redis distributed caching layer in ASP.NET Core with TTL policies and reactive cache invalidation. Engineered cache-aside patterns with fallback to relational queries.
- **Result:** Reduced direct database hits significantly and maintained 99.9% uptime during peak concurrent activity.
> 💡 **Winning Pitch Line:** 'At ExcelSoft, I engineered Redis caching to handle massive concurrent traffic spikes, which directly translates to Freightos's requirement for scalable, low-latency services.'

### Sub-Second Live Data Streaming with WebSockets (Freightos Focus)
- **Situation:** Online platforms require real-time updates without the network overhead and delay of recurring HTTP polling.
- **Task:** Build a responsive bi-directional event stream between React frontends and backend services.
- **Action:** Implemented WebSocket connection managers with exponential backoff auto-reconnect, custom React hooks (`useWebSocket`), and heartbeat ping/pong monitoring.
- **Result:** Achieved sub-second alert broadcasts while eliminating thousands of redundant polling requests.
> 💡 **Winning Pitch Line:** 'My experience building real-time WebSocket pipelines allows me to implement instant, reliable user interactions for Freightos's digital products.'

### JWT Token Rotation & Route-Level RBAC (Freightos Standard)
- **Situation:** Multi-role enterprise platforms require strict authorization boundaries without degrading user session fluidity.
- **Task:** Develop an end-to-end security pipeline bridging ASP.NET Core / Node.js with React route protection.
- **Action:** Configured short-lived JWT access tokens with secure HTTP-only refresh tokens, Axios interceptors for silent refresh on 401s, and React Higher-Order Components checking role claims.
- **Result:** Prevented unauthorized data access while ensuring zero unexpected session expirations for active users.
> 💡 **Winning Pitch Line:** 'I design secure, enterprise-grade authentication and RBAC systems that protect sensitive data while maintaining smooth user sessions at Freightos.'

---

## 💻 3. High-Probability Technical Questions & Answers
### Q1: How do you architect complex booking workflows with multi-step forms in React?
**Model Answer (2+ Years Perspective):**
> Use a centralized state machine or Redux with persistent draft storage. Break the wizard into lazy-loaded modular steps with schema validation (Zod) per step. Ensure URL sync allows resuming at any step with restored form data.

### Q2: How do you ensure end-to-end reliability for critical payment and cargo booking flows?
**Model Answer (2+ Years Perspective):**
> Write unit tests with Jest for pure business logic and Redux reducers, integration tests with React Testing Library for user interactions, and end-to-end Cypress smoke tests for complete checkout/booking flows in CI/CD before release.

### Q3: How do you leverage AWS S3 and CloudFront for global asset delivery?
**Model Answer (2+ Years Perspective):**
> Host static SPA assets in S3 with strict private access (Origin Access Control - OAC) behind CloudFront CDN. Configure gzip/Brotli compression, cache headers (`Cache-Control: max-age=31536000, immutable` for hashed bundles, `no-cache` for `index.html`), and edge lambdas for custom routing.

---

## 🏗️ 4. System Design & Architectural Challenge
**Challenge:** Design a Real-Time Global Freight Rate Quoting & Booking Engine.
- **How to structure your solution:**
  1. Clarify functional and non-functional requirements (throughput, availability, latency).
  2. Outline API endpoints and data contracts (REST/WebSockets).
  3. Design storage tier: Primary SQL/NoSQL DB + Redis caching layer for hot reads.
  4. Address failure modes: Retries with exponential backoff, circuit breakers, and rate limiting.

---

## 🙋 5. Reverse Interview Questions (Ask the Interviewer)
- *"What does the engineering architecture look like at Freightos for this team, and how are frontend and backend responsibilities coordinated?"*
- *"How does Freightos approach testing and continuous deployment (CI/CD) for production releases?"*
- *"What is the biggest technical challenge or scaling goal this team is looking to solve over the next 6 months?"*
- *"What does career growth and mentorship look like for an engineer with 2+ years of experience coming into Freightos?"*