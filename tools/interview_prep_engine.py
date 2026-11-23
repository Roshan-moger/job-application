#!/usr/bin/env python3
"""
Dynamic Interview Preparation Engine for Roshan Moger
Synthesizes company & role requirements with Roshan's actual resume to generate
hyper-tailored, actionable interview preparation guides.
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Canonical Candidate Profile (Grounded in Roshan Moger's verified experience)
CANDIDATE_PROFILE = {
    "name": "Roshan Moger",
    "title": "Full Stack Developer (Associate Software Engineer)",
    "experience_years": "2.5+ Years",
    "current_role": "Associate Software Engineer at ExcelSoft Technologies (May 2024 - Present)",
    "certification": "Java Full-Stack Development Certification from Kodnest Technologies (Aug 2023 - Apr 2024)",
    "education": "B.E. in Electrical & Electronics Engineering, NIE Institute of Technology, Mysore (GPA 7.8/10, 2019-2023)",
    "contact": {
        "phone": "+91-8970035508",
        "email": "roshanmoger502@gmail.com",
        "linkedin": "https://linkedin.com/in/roshan-moger",
        "github": "https://github.com/Roshan-moger",
        "portfolio": "https://roshan-devhub.netlify.app"
    },
    "core_skills": [
        "React.js", "TypeScript", "JavaScript", "ASP.NET Core", "C#", "REST APIs",
        "Redux", "Tailwind CSS", "Redis Caching", "WebSockets", "Docker", "Kubernetes",
        "AWS (EC2, S3, RDS, Lambda, CloudWatch)", "SQL (MySQL, PostgreSQL)", "MongoDB",
        "Node.js", "Express.js", "Model Context Protocol (MCP)", "AWS Bedrock", "Google Gemini", "Git"
    ],
    "key_projects": [
        {
            "name": "Saras Standard Platform, SVKM Platform & OwlBot (ExcelSoft)",
            "tech": "React.js, TypeScript, ASP.NET Core, C#, Redis, WebSockets, AWS, MCP, AWS Bedrock, Google Gemini",
            "impact": "Enterprise EdTech & compliance platforms. Built modular React SPAs, high-throughput .NET Core APIs, Redis caching layer to offload heavy DB reads during assessment spikes, WebSockets for live proctoring telemetry, and an MCP server with Gemini chatbot integration via AWS Bedrock."
        },
        {
            "name": "Real-Time Expense Tracker",
            "tech": "React.js, TypeScript, Redux, Node.js, Express.js, MongoDB",
            "impact": "Full-stack personal finance tracker with JWT auth, refresh token rotation, route guards, and optimized query patterns."
        },
        {
            "name": "Event Management System",
            "tech": "React.js, TypeScript, WebSockets",
            "impact": "Multi-role platform (Admin, Organizer, Customer) with ticket booking, QR-based check-in, and instant live event streaming via WebSockets."
        }
    ]
}

# Domain Intelligence Database
DOMAIN_INTEL = {
    "fintech": {
        "keywords": ["navi", "bank", "pay", "finance", "fintech", "wealth", "lending", "credit", "insurance", "alegeus", "osfin", "osfin.ai", "mufg"],
        "priorities": "Data integrity, idempotent API transactions, zero-loss state management, high security, PCI-DSS/RBI compliance, audit trails.",
        "common_questions": [
            ("How do you ensure idempotency in payment and financial transaction APIs?",
             "In ASP.NET Core / Node.js, each mutation request carries a unique client-generated Idempotency-Key header. The server verifies this key in Redis/DB with an atomic check-and-set. If the key exists and is processed, it returns the cached response without re-executing business logic; if processing, it rejects duplicates with 409 Conflict."),
            ("How do you handle sensitive financial data in frontend state and client storage?",
             "Never store sensitive financial data (PAN, CVV, raw tokens) in localStorage or sessionStorage (vulnerable to XSS). Keep tokens in HTTP-only Secure SameSite cookies. Mask card/account details in Redux state, and clear transient transactional state from memory upon navigation or component unmount."),
            ("How do you design database transactions to prevent double-spending or race conditions?",
             "Use ACID database transactions with appropriate isolation levels (Repeatable Read or Serializable). In EF Core / SQL, implement optimistic concurrency control using row versioning tokens (`[Timestamp]`), or use pessimistic locking (`SELECT FOR UPDATE`) for high-contention balance updates.")
        ],
        "system_design": "Design a High-Throughput Real-Time Transaction & Balance Notification Service.",
        "gaps_to_brush_up": [
            "ACID transaction isolation levels & distributed locking (Redis Redlock).",
            "Idempotent API design using unique idempotency keys.",
            "Handling micro-frontend communication without data leaks."
        ]
    },
    "healthtech": {
        "keywords": ["truemeds", "pharma", "health", "care", "medical", "clinic", "doctor", "huntingcube", "leucine"],
        "priorities": "Patient data confidentiality (HIPAA/DISHA compliance), fast e-commerce catalog search, prescription upload pipelines, resilient cart & checkout state.",
        "common_questions": [
            ("How do you ensure user privacy and security when handling prescription uploads?",
             "Prescription files should be uploaded directly from the client to AWS S3 using pre-signed URLs with strict Content-Type and size validation. Never expose public S3 buckets. Enforce server-side AES-256 encryption (SSE-S3 or AWS KMS) and authorize access via signed time-limited tokens."),
            ("How do you optimize product search and medicine substitution filtering in React?",
             "Implement debouncing (300-400ms) on search inputs using custom hooks (`useDebounce`). Cache frequent search results locally or in Redis, and virtualize large inventory lists with `react-window` to maintain 60 FPS scrolling."),
            ("How do you ensure cart state persistence across device restarts?",
             "Use a hybrid state strategy: local optimistic UI state via Redux Persist, synchronized asynchronously with backend Redis/database carts. On auth state change, merge anonymous guest cart items into the authenticated user account without duplicate items.")
        ],
        "system_design": "Design a Scalable Medicine Search & Real-Time Prescription Verification Flow.",
        "gaps_to_brush_up": [
            "File upload security with AWS S3 pre-signed URLs.",
            "Debounced search & client-side virtualization for large catalogs.",
            "Handling multi-step checkout state with robust validation."
        ]
    },
    "ecommerce": {
        "keywords": ["giva", "fossil", "cart", "shop", "commerce", "retail", "store", "headout"],
        "priorities": "High-traffic flash sales, SEO & Core Web Vitals, inventory locking, checkout funnel conversion, CDN caching.",
        "common_questions": [
            ("How do you handle inventory reservation during high-concurrency flash sales?",
             "Use Redis atomic operations (`DECR` or Lua scripts) to reserve stock in memory before persisting orders to the relational database. If stock hits zero, reject immediately without hammering the database. Implement a TTL on reservations (e.g. 10 minutes) so abandoned carts release stock automatically via Redis keyspace notifications."),
            ("How do you optimize Core Web Vitals (LCP, CLS, FID/INP) in an e-commerce SPA?",
             "Minimize Largest Contentful Paint (LCP) by preloading hero banners and using modern formats (WebP/AVIF) from AWS CloudFront CDN. Eliminate Cumulative Layout Shift (CLS) by specifying explicit aspect ratio dimensions on images. Optimize INP by code-splitting heavy bundles with `React.lazy()` and moving non-critical analytics scripts off the main thread."),
            ("How do you manage complex multi-filter navigation (price, category, rating) without lag?",
             "Keep filter state in URL search parameters (`useSearchParams`) to enable bookmarking and back-button navigation. Memoize derived product arrays with `useMemo`, and debounce filter sliders to avoid excessive re-render cycles.")
        ],
        "system_design": "Design a Flash-Sale Order Processing Engine with High Concurrency.",
        "gaps_to_brush_up": [
            "Core Web Vitals optimization techniques.",
            "Redis Lua scripts for atomic stock decrement.",
            "URL-based state synchronization for product catalogs."
        ]
    },
    "devtools_realtime": {
        "keywords": ["discorder", "tools", "realtime", "socket", "stream", "chat", "bot"],
        "priorities": "Bi-directional WebSockets, connection heartbeat & auto-reconnect, message delivery guarantees, horizontal socket scaling with Redis pub/sub.",
        "common_questions": [
            ("How do you horizontally scale WebSocket connections across multiple backend servers?",
             "Use a distributed Pub/Sub message broker like Redis or RabbitMQ. When client A connects to Server 1 and client B connects to Server 2, Server 1 publishes messages to a Redis channel, and Server 2 receives and broadcasts them to client B. Sticky sessions or socket clustering via AWS ALB ensure stable socket routing."),
            ("How do you handle dropped connections and message ordering on the client?",
             "Implement exponential backoff reconnection in a custom React hook. Assign monotonically increasing sequence IDs to messages. When reconnected, the client transmits the last received message ID so the server can replay missed events from an ephemeral cache (Redis stream)."),
            ("How do you prevent memory leaks when managing WebSockets in React components?",
             "Always clean up listeners and close connections in the `useEffect` cleanup return function: `return () => { socket.close(); socket.removeEventListener(...); };`. Avoid capturing stale state closures by using `useRef` or updater functions inside state setters.")
        ],
        "system_design": "Design a Resilient Real-Time Event & Notification Streaming Platform.",
        "gaps_to_brush_up": [
            "Socket connection pooling and heartbeat ping/pong lifecycle.",
            "Redis Pub/Sub adapter for WebSocket clustering.",
            "Handling out-of-order packet delivery in SPAs."
        ]
    },
    "enterprise_consulting": {
        "keywords": ["quest", "pwc", "infosys", "merck", "acceleration", "consulting", "enterprise", "akzo", "akzonobel", "itc", "sonata", "kimoha", "thomson", "eurofins", "incresco", "gevernova", "vernova", "ge vernova", "yash", "synechron", "cognizant", "ibm", "omnissa", "tcs", "tata", "jobgether"],
        "priorities": "Clean Architecture, SOLID principles, testability, enterprise security (OAuth2/OIDC), microservices patterns, Docker/K8s governance.",
        "common_questions": [
            ("Explain Clean Architecture / Onion Architecture in ASP.NET Core.",
             "Clean Architecture organizes code into concentric layers where dependencies only point inward: Domain (Entities, Value Objects) at the center -> Application (Use Cases, DTOs, CQRS handlers) -> Infrastructure (EF Core, AWS, Redis, External APIs) -> Presentation (Controllers, Minimal APIs). The Domain and Application layers never depend on external databases or UI frameworks."),
            ("What is the difference between CQRS and traditional CRUD?",
             "CQRS (Command Query Responsibility Segregation) separates write operations (Commands that change state) from read operations (Queries that return data). This allows independent scaling, optimized read models (e.g. read-only DTO projections bypassing heavy entity tracking), and streamlined caching without complicated ORM overhead."),
            ("How do you design a zero-downtime deployment strategy on AWS?",
             "Implement Blue-Green or Rolling Updates via Kubernetes / AWS ECS. Health check endpoints (`/health/live` and `/health/ready`) ensure new container pods are verified before AWS Application Load Balancer routes live user traffic to them. Database schema migrations are backward-compatible using expand-and-contract patterns.")
        ],
        "system_design": "Design a Multi-Tenant Scalable Enterprise Management System.",
        "gaps_to_brush_up": [
            "CQRS pattern and MediatR in ASP.NET Core.",
            "Enterprise OAuth2 / OpenID Connect authorization flows.",
            "Zero-downtime database migrations (Expand-and-Contract)."
        ]
    },
    "streaming_media": {
        "keywords": ["jiostar", "jio", "viacom", "hotstar", "streaming", "video", "media", "ott", "telemetry"],
        "priorities": "Adaptive bitrate streaming (HLS/MPEG-DASH), Core Web Vitals, video player telemetry (QoS/QoE), sub-second WebSockets, Shaka Player/Video.js, cross-device web platforms.",
        "common_questions": [
            ("How do you optimize Core Web Vitals and startup latency for heavy media streaming web apps?",
             "Preconnect to media CDNs, load player SDKs dynamically, defer non-critical analytics until player state reaches 'playing', and use Service Workers to cache manifest chunks and static UI assets. Ensure initial bundle is minimal by lazy-loading player controls and modal overlays."),
            ("How do you design a real-time playback telemetry pipeline without hurting UI rendering?",
             "Collect metrics (buffer health, bitrate switches, dropped frames, startup time) via HTML5 video events into a lightweight memory buffer. Flush events in micro-batches using `navigator.sendBeacon` or a dedicated WebSocket channel on a Web Worker thread to keep the React UI main thread at 60 FPS."),
            ("How do you handle live proctoring or live multi-stream synchronization in React?",
             "Use WebRTC / WebSocket channels for low-latency video feed signalling, maintain audio-video synchronization using presentation timestamps (PTS), and gracefully degrade quality on network drops using adaptive bitrate triggers.")
        ],
        "system_design": "Design a Scalable Video Playback & Real-Time Telemetry Tracking Pipeline.",
        "gaps_to_brush_up": [
            "HLS/DASH streaming protocols & video player lifecycle (Shaka Player / HLS.js).",
            "Core Web Vitals tuning (LCP, INP, CLS) in media-heavy SPAs.",
            "Web Worker data serialization for background telemetry processing."
        ]
    },
    "devsecops_saas": {
        "keywords": ["autorabit", "salesforce", "devsecops", "devops", "pipeline", "release", "ci-cd"],
        "priorities": "Multi-tenant isolation, background job queues, GraphQL/REST API design, worker claiming & concurrency, Docker/Kubernetes container orchestration.",
        "common_questions": [
            ("How do you design a resilient background task and queue processing system?",
             "Use a Redis-backed queue (such as BullMQ) or RabbitMQ with worker claiming, heartbeat checks, idempotency keys, and dead-letter queues (DLQ). Workers lock tasks atomically, process them with timeout limits, and release locks on completion to prevent duplicate execution upon worker crash."),
            ("How do you prevent the N+1 problem in GraphQL APIs?",
             "Use DataLoader batching and caching patterns. DataLoader coalesces individual item fetch requests made across a single execution tick into a single bulk query (e.g. `WHERE id IN (...)`), returning resolved promises mapped by entity ID."),
            ("How do you enforce multi-tenant data security in full-stack applications?",
             "Incorporate tenant ID claims directly inside JWT tokens. In ASP.NET Core / Node.js, apply global query filters (EF Core query filters or Prisma middleware) that automatically append `tenant_id = @currentTenant` to every query, preventing cross-tenant leakage.")
        ],
        "system_design": "Design a Scalable Multi-Tenant Job Runner & CI/CD Pipeline Dashboard.",
        "gaps_to_brush_up": [
            "Distributed job queues (BullMQ / RabbitMQ) with worker concurrency.",
            "GraphQL schema design, DataLoader batching, and query complexity limits.",
            "Multi-tenant isolation strategies (database per tenant vs shared schema with tenant ID)."
        ]
    },
    "freight_logistics": {
        "keywords": ["freightos", "freight", "logistics", "cargo", "supply", "shipping", "booking"],
        "priorities": "High-volume booking engines, complex multi-currency calculation, real-time tracking dashboards, AWS CloudFront & S3 caching, automated test coverage (Jest/Cypress).",
        "common_questions": [
            ("How do you architect complex booking workflows with multi-step forms in React?",
             "Use a centralized state machine or Redux with persistent draft storage. Break the wizard into lazy-loaded modular steps with schema validation (Zod) per step. Ensure URL sync allows resuming at any step with restored form data."),
            ("How do you ensure end-to-end reliability for critical payment and cargo booking flows?",
             "Write unit tests with Jest for pure business logic and Redux reducers, integration tests with React Testing Library for user interactions, and end-to-end Cypress smoke tests for complete checkout/booking flows in CI/CD before release."),
            ("How do you leverage AWS S3 and CloudFront for global asset delivery?",
             "Host static SPA assets in S3 with strict private access (Origin Access Control - OAC) behind CloudFront CDN. Configure gzip/Brotli compression, cache headers (`Cache-Control: max-age=31536000, immutable` for hashed bundles, `no-cache` for `index.html`), and edge lambdas for custom routing.")
        ],
        "system_design": "Design a Real-Time Global Freight Rate Quoting & Booking Engine.",
        "gaps_to_brush_up": [
            "End-to-End testing architecture with Cypress & Jest.",
            "AWS CloudFront OAC & S3 pre-signed upload security.",
            "Idempotent payment webhook processing."
        ]
    },
    "consumer_tech": {
        "keywords": ["swiggy", "zepto", "cred", "razorpay", "groww", "blinkit", "accenture", "dell", "lti", "wipro", "capgemini", "scoutit", "mathco", "talentgigs", "innovkaro"],
        "priorities": "High-concurrency web apps, responsive rendering, state persistence, API performance, resilient checkout/onboarding.",
        "common_questions": [
            ("How do you architect large-scale React applications to maintain high responsiveness?",
             "By modularizing features into independent domain packages, implementing route-based code-splitting with React.lazy, colocating state, utilizing custom hooks for data fetching with caching, and avoiding costly deep component re-renders with React.memo and useCallback."),
            ("How do you handle real-time order tracking or live notifications in web apps?",
             "Use a WebSocket connection or Server-Sent Events (SSE) backed by a Redis pub/sub channel. In React, manage this via a centralized custom hook (useWebSocket) that dispatches updates to Redux, handles auto-reconnection with exponential backoff, and cleans up socket subscriptions on unmount."),
            ("How do you ensure enterprise REST APIs are secure and scalable in production?",
             "Implement rate limiting (e.g. token bucket in Redis), enforce JWT authentication with short TTLs and secure HTTP-only refresh tokens, configure CORS strictly, validate all request DTOs, and utilize API gateways for centralized authentication, SSL termination, and caching.")
        ],
        "system_design": "Design a High-Throughput Real-Time Consumer Web Platform with Live Telemetry.",
        "gaps_to_brush_up": [
            "Micro-frontends and code-splitting architecture.",
            "Client-side caching strategies (SWR / React Query).",
            "Server-Sent Events (SSE) vs WebSockets trade-offs."
        ]
    }
}

def detect_domain(company_name, role_title, skills):
    text = f"{company_name} {role_title} {' '.join(skills)}".lower()
    for domain, data in DOMAIN_INTEL.items():
        for kw in data["keywords"]:
            if kw in text:
                return domain, data
    # Default to modern web / enterprise
    return "enterprise_consulting", DOMAIN_INTEL["enterprise_consulting"]

def analyze_resume_alignment(job_skills):
    job_skills_lower = [s.lower().strip() for s in job_skills]
    roshan_skills_lower = [s.lower() for s in CANDIDATE_PROFILE["core_skills"]]

    direct_matches = []
    gaps_or_extensions = []

    for s in job_skills:
        s_low = s.lower().strip()
        matched = False
        for r in CANDIDATE_PROFILE["core_skills"]:
            if s_low in r.lower() or r.lower() in s_low:
                direct_matches.append(r)
                matched = True
                break
        if not matched:
            gaps_or_extensions.append(s)

    # De-duplicate
    direct_matches = list(dict.fromkeys(direct_matches))
    gaps_or_extensions = list(dict.fromkeys(gaps_or_extensions))

    return direct_matches, gaps_or_extensions

def generate_dynamic_prep(company, role, skills, location="Bengaluru, Karnataka", experience_req="1-3 Years", job_url=""):
    domain_key, domain_data = detect_domain(company, role, skills)
    direct_matches, gaps = analyze_resume_alignment(skills)

    # Tailor STAR Stories to this specific company
    tailored_stars = [
        {
            "theme": "Backend Scaling & Caching",
            "title": f"Redis Distributed Caching to Eliminate Latency ({company} Application)",
            "situation": f"On ExcelSoft's assessment platforms, peak traffic caused heavy database read contention. For a high-throughput environment like {company}, database bottlenecks degrade user experience.",
            "task": "Cut database round-trips by >60% and ensure sub-150ms API responses under concurrent user load.",
            "action": "Designed a Redis distributed caching layer in ASP.NET Core with TTL policies and reactive cache invalidation. Engineered cache-aside patterns with fallback to relational queries.",
            "result": "Reduced direct database hits significantly and maintained 99.9% uptime during peak concurrent activity.",
            "pitch_line": f"'At ExcelSoft, I engineered Redis caching to handle massive concurrent traffic spikes, which directly translates to {company}'s requirement for scalable, low-latency services.'"
        },
        {
            "theme": "Real-Time Systems & Event Streaming",
            "title": f"Sub-Second Live Data Streaming with WebSockets ({company} Focus)",
            "situation": f"Online platforms require real-time updates without the network overhead and delay of recurring HTTP polling.",
            "task": "Build a responsive bi-directional event stream between React frontends and backend services.",
            "action": "Implemented WebSocket connection managers with exponential backoff auto-reconnect, custom React hooks (`useWebSocket`), and heartbeat ping/pong monitoring.",
            "result": "Achieved sub-second alert broadcasts while eliminating thousands of redundant polling requests.",
            "pitch_line": f"'My experience building real-time WebSocket pipelines allows me to implement instant, reliable user interactions for {company}'s digital products.'"
        },
        {
            "theme": "Security, Auth & Enterprise Architecture",
            "title": f"JWT Token Rotation & Route-Level RBAC ({company} Standard)",
            "situation": f"Multi-role enterprise platforms require strict authorization boundaries without degrading user session fluidity.",
            "task": "Develop an end-to-end security pipeline bridging ASP.NET Core / Node.js with React route protection.",
            "action": "Configured short-lived JWT access tokens with secure HTTP-only refresh tokens, Axios interceptors for silent refresh on 401s, and React Higher-Order Components checking role claims.",
            "result": "Prevented unauthorized data access while ensuring zero unexpected session expirations for active users.",
            "pitch_line": f"'I design secure, enterprise-grade authentication and RBAC systems that protect sensitive data while maintaining smooth user sessions at {company}.'"
        },
        {
            "theme": "AI Integration & Model Context Protocol (MCP)",
            "title": f"MCP Server in .NET & Gemini LLM Chatbot ({company} Application)",
            "situation": f"Enterprise platforms need to bridge internal SaaS workflows and proprietary data with Generative AI systems without compromising security boundaries.",
            "task": "Expose SaaS platform data and workflows to AI agents and build an in-product conversational assistant using Google Gemini via AWS Bedrock.",
            "action": "Designed and implemented an MCP server using .NET to standardize SaaS capabilities into agentic tools. Integrated Google Gemini (via AWS Bedrock) alongside internal AI models with strict prompt guardrails and streaming telemetry.",
            "result": "Enabled conversational querying across assessment and compliance modules, dramatically streamlining reporting workflows.",
            "pitch_line": f"'At ExcelSoft, I engineered an MCP server in .NET and integrated Google Gemini via AWS Bedrock, bringing cutting-edge agentic AI into production for {company}.'"
        }
    ]

    # Specific actionable gaps to prepare based on Roshan's resume
    resume_gap_advice = []
    for g in gaps:
        g_low = g.lower()
        if "next" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "You have deep React.js, TypeScript, and Redux experience.",
                "what_to_prepare": "Review Next.js 14/15 App Router: Server Components vs Client Components (`'use client'`), Incremental Static Regeneration (ISR), and route handlers."
            })
        elif "node" in g_low or "express" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "You built the Real-Time Expense Tracker with Node.js/Express and have extensive ASP.NET Core API experience.",
                "what_to_prepare": "Brush up on Node.js event loop phases, Express middleware chaining, and async error-handling wrappers."
            })
        elif "mongo" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "You used MongoDB in your MERN Expense Tracker alongside SQL at ExcelSoft.",
                "what_to_prepare": "Review MongoDB aggregation pipelines (`$match`, `$group`, `$lookup`), compound index creation, and schema design vs SQL normalization."
            })
        elif "aws" in g_low or "cloud" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "You deployed Dockerized microservices across AWS EC2, S3, RDS, Lambda, and CloudWatch.",
                "what_to_prepare": "Be ready to explain how you configure IAM least-privilege roles, S3 pre-signed URLs, and CloudWatch alert thresholds."
            })
        elif "graphql" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "You have extensive experience designing and consuming RESTful and WebSocket APIs.",
                "what_to_prepare": "Review GraphQL schema definition (SDL), query resolvers, mutations, DataLoader batching to prevent N+1 queries, and Apollo/TanStack Client integration."
            })
        elif "jest" in g_low or "testing" in g_low or "test" in g_low or "cypress" in g_low or "playwright" in g_low or "nunit" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "You write unit and integration tests across React components and backend API endpoints.",
                "what_to_prepare": "Review React Testing Library query priority (`getByRole`), mocking API requests (MSW), and E2E test assertions with Playwright/Cypress."
            })
        elif "python" in g_low:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": "Your strong backend foundations in C# and TypeScript allow quick transition across typed languages.",
                "what_to_prepare": "Review FastAPI / Flask routing, Pydantic type validation, async/await event loops, and relational DB integration."
            })
        else:
            resume_gap_advice.append({
                "skill": g,
                "resume_bridge": f"Your strong full-stack foundations in React and C#/.NET Core allow fast ramp-up.",
                "what_to_prepare": f"Review standard industry best practices and core API/architectural patterns for {g}."
            })

    # High-signal reverse interview questions for Roshan to ask
    reverse_questions = [
        f"What does the engineering architecture look like at {company} for this team, and how are frontend and backend responsibilities coordinated?",
        f"How does {company} approach testing and continuous deployment (CI/CD) for production releases?",
        f"What is the biggest technical challenge or scaling goal this team is looking to solve over the next 6 months?",
        f"What does career growth and mentorship look like for an engineer with 2+ years of experience coming into {company}?"
    ]

    return {
        "company": company,
        "role": role,
        "location": location,
        "experience_req": experience_req,
        "domain": domain_key.replace("_", " ").title(),
        "domain_priorities": domain_data["priorities"],
        "job_url": job_url,
        "direct_matches": direct_matches,
        "skills_to_review": gaps,
        "resume_gap_advice": resume_gap_advice,
        "tailored_stars": tailored_stars,
        "technical_qa": domain_data["common_questions"],
        "system_design_scenario": domain_data["system_design"],
        "reverse_questions": reverse_questions,
        "candidate": CANDIDATE_PROFILE
    }

def format_as_markdown(prep_data):
    md = []
    md.append(f"# 🎯 Dynamic Interview Preparation Guide: {prep_data['company']}")
    md.append(f"### Role: {prep_data['role']}")
    md.append(f"**Candidate:** {prep_data['candidate']['name']} ({prep_data['candidate']['experience_years']} Experience)")
    md.append(f"**Target Location:** {prep_data['location']} | **Required Level:** {prep_data['experience_req']}")
    md.append(f"**Industry Domain:** {prep_data['domain']}")
    md.append(f"**Domain Focus:** {prep_data['domain_priorities']}\n")
    md.append("---\n")

    md.append("## 📊 1. Resume Alignment & Skill Match Analysis")
    md.append("### ✅ Direct Matches from Your Resume:")
    for s in prep_data["direct_matches"]:
        md.append(f"- **{s}**: Production-proven from your work at ExcelSoft Technologies and full-stack projects.")
    
    if prep_data["resume_gap_advice"]:
        md.append("\n### 🔍 Gaps & Areas to Brush Up Based on Your Resume:")
        for g in prep_data["resume_gap_advice"]:
            md.append(f"- **{g['skill']}**:")
            md.append(f"  - *Your Resume Bridge:* {g['resume_bridge']}")
            md.append(f"  - *What to Review Before Interview:* {g['what_to_prepare']}")
    md.append("\n---\n")

    md.append("## 🚀 2. Tailored STAR Stories (Ready to Speak)")
    for s in prep_data["tailored_stars"]:
        md.append(f"### {s['title']}")
        md.append(f"- **Situation:** {s['situation']}")
        md.append(f"- **Task:** {s['task']}")
        md.append(f"- **Action:** {s['action']}")
        md.append(f"- **Result:** {s['result']}")
        md.append(f"> 💡 **Winning Pitch Line:** {s['pitch_line']}\n")
    md.append("---\n")

    md.append("## 💻 3. High-Probability Technical Questions & Answers")
    for idx, (q, a) in enumerate(prep_data["technical_qa"], 1):
        md.append(f"### Q{idx}: {q}")
        md.append(f"**Model Answer (2+ Years Perspective):**\n> {a}\n")
    md.append("---\n")

    md.append("## 🏗️ 4. System Design & Architectural Challenge")
    md.append(f"**Challenge:** {prep_data['system_design_scenario']}")
    md.append("- **How to structure your solution:**")
    md.append("  1. Clarify functional and non-functional requirements (throughput, availability, latency).")
    md.append("  2. Outline API endpoints and data contracts (REST/WebSockets).")
    md.append("  3. Design storage tier: Primary SQL/NoSQL DB + Redis caching layer for hot reads.")
    md.append("  4. Address failure modes: Retries with exponential backoff, circuit breakers, and rate limiting.")
    md.append("\n---\n")

    md.append("## 🙋 5. Reverse Interview Questions (Ask the Interviewer)")
    for q in prep_data["reverse_questions"]:
        md.append(f"- *\"{q}\"*")

    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Generate dynamic interview prep guide for any company based on Roshan's resume")
    parser.add_argument("--company", required=True, help="Company name (e.g. Truemeds, Navi, PwC)")
    parser.add_argument("--role", required=True, help="Role title (e.g. React Developer, SDE 1)")
    parser.add_argument("--skills", nargs="*", default=["React", "TypeScript", "Node.js", "REST"], help="Skills list")
    parser.add_argument("--location", default="Bengaluru, Karnataka", help="Job location")
    parser.add_argument("--output", help="Output path for markdown report")

    args = parser.parse_args()
    prep = generate_dynamic_prep(args.company, args.role, args.skills, args.location)
    md_content = format_as_markdown(prep)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_content, encoding="utf-8")
        print(f"✅ Generated interview prep guide at: {out_path}")
    else:
        print(md_content)

if __name__ == "__main__":
    main()
