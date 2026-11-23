#!/usr/bin/env python3
"""
Dynamic Full Stack Developer Roadmap & Study Material Engine for Roshan Moger
Reads candidate profile directly and synthesizes a tailored, step-by-step
up-skilling roadmap with curated, high-quality study materials, documentation,
and production GitHub repos to transition from Associate to Senior / High-Scale Full Stack.
"""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Read Candidate Profile
def load_candidate_profile():
    return {
        "name": "Roshan Moger",
        "current_title": "Associate Software Engineer at ExcelSoft Technologies",
        "experience": "2+ Years (May 2024 - Present)",
        "target_level": "SDE 2 / Mid-Senior Full Stack Developer",
        "education": "B.E. in Electrical & Electronics Engineering (NIE Institute of Technology, Mysore)",
        "verified_strengths": [
            "React.js", "TypeScript", "JavaScript", "ASP.NET Core", "C#", "REST APIs",
            "Redux", "Tailwind CSS", "Redis Caching (Basics)", "WebSockets (Real-time telemetry)",
            "Docker (Basics)", "Kubernetes (Basics)", "AWS (EC2, S3, RDS, Lambda, CloudWatch)",
            "SQL (PostgreSQL, MySQL)", "MongoDB (Basics)", "Node.js / Express (Basics)"
        ],
        "key_projects": [
            "Saras Standard Platform & SVKM Platform (ExcelSoft)",
            "Real-Time Expense Tracker (MERN)",
            "Event Management System (React + WebSockets)"
        ]
    }

# Roadmap & Study Materials Database Calibrated for Roshan's 2+ Yrs Profile
ROADMAP_PHASES = [
    {
        "phase_num": 1,
        "title": "Advanced Frontend & Full-Stack React Architecture",
        "subtitle": "Next.js App Router, React Server Components (RSC), & Web Performance",
        "est_hours": "16-20 Hours",
        "candidate_baseline": "Strong foundation in React.js, TypeScript, custom hooks, Redux, and Tailwind CSS from ExcelSoft production work.",
        "skip_advice": "Skip basic React fundamentals (JSX, props, simple useState/useEffect, basic routing). You already use them daily in production.",
        "must_learn": [
            "Next.js 14/15 App Router: Server Components vs Client Components ('use client'), Server Actions, and Streaming with Suspense.",
            "Rendering Strategies: SSR (Server-Side Rendering), SSG (Static Site Generation), and ISR (Incremental Static Regeneration).",
            "Core Web Vitals & Optimization: Largest Contentful Paint (LCP), Interaction to Next Paint (INP), Cumulative Layout Shift (CLS), and bundle splitting (`React.lazy`, `@bundle-analyzer`).",
            "Modern Lightweight State: Zustand and TanStack Query (React Query) for server-state caching vs Redux for complex UI state."
        ],
        "study_materials": [
            {
                "name": "Official Next.js App Router Documentation & Tutorial",
                "type": "Official Docs",
                "url": "https://nextjs.org/docs/app",
                "desc": "The authoritative source. Follow the 'Building Your Application' section focusing on Routing, Data Fetching, and Server Actions."
            },
            {
                "name": "React 19 & Server Components Deep Dive (Jack Herrington)",
                "type": "Video Course",
                "url": "https://www.youtube.com/@jherr",
                "desc": "Best practical explanations on RSC mental models, client/server boundaries, and modern state architectures."
            },
            {
                "name": "TanStack Query (React Query) Official Guides",
                "type": "Official Docs",
                "url": "https://tanstack.com/query/latest/docs/framework/react/overview",
                "desc": "Standard industry library for server state, background refetching, mutation lifecycle, and optimistic updates."
            },
            {
                "name": "web.dev Core Web Vitals Optimization Guide (Google Chrome Team)",
                "type": "Technical Guide",
                "url": "https://web.dev/explore/fast",
                "desc": "Concrete techniques to optimize LCP, INP, and CLS for consumer-facing web applications."
            }
        ],
        "interview_talking_point": "In interviews, explain how you evaluate Client vs Server Components to minimize JavaScript ship size, and how you use TanStack Query/SWR for cache invalidation without state bloat."
    },
    {
        "phase_num": 2,
        "title": "Enterprise Backend, Clean Architecture & Microservices",
        "subtitle": "ASP.NET Core Clean Architecture, CQRS, MediatR, & Event-Driven Patterns",
        "est_hours": "18-22 Hours",
        "candidate_baseline": "Solid experience building ASP.NET Core REST APIs, JWT authentication, and dependency injection at ExcelSoft.",
        "skip_advice": "Skip basic C# syntax and generic Web API controller scaffolding. Focus on architectural decoupling and high-scale patterns.",
        "must_learn": [
            "Clean Architecture (Onion Architecture): Separation into Domain, Application, Infrastructure, and Presentation layers.",
            "CQRS Pattern & MediatR: Separating Command mutations from Query reads for clean scaling and testability.",
            "Asynchronous Event Streaming & Message Brokers: Asynchronous inter-service decoupling using RabbitMQ or Apache Kafka vs REST.",
            "Resilience Patterns: Circuit Breakers, Retries with Exponential Backoff, and Rate Limiting using Polly in .NET.",
            "Node.js Backend Deep Dive: Node.js Event Loop phases (timers, I/O polling, microtasks), worker threads, and cluster module."
        ],
        "study_materials": [
            {
                "name": "Jason Taylor's Clean Architecture Solution Template (.NET)",
                "type": "GitHub Repository",
                "url": "https://github.com/jasontaylordev/CleanArchitecture",
                "desc": "The gold-standard GitHub repository demonstrating Clean Architecture, CQRS, MediatR, and EF Core in ASP.NET Core."
            },
            {
                "name": "CodeOpinion (Derek Comartin) - Software Architecture & CQRS",
                "type": "Video Channel",
                "url": "https://www.youtube.com/@CodeOpinion",
                "desc": "Outstanding visual explanations on Clean Architecture, CQRS, Event-Driven Architecture, and Microservices trade-offs."
            },
            {
                "name": "Microsoft e-ShopOnContainers / .NET Microservices Architecture e-Book",
                "type": "Architecture Guide",
                "url": "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/",
                "desc": "Comprehensive free guide on designing microservices, domain events, API Gateways, and containerized deployment."
            },
            {
                "name": "Node.js Best Practices Repository (Goldberg Yoni)",
                "type": "GitHub Repository",
                "url": "https://github.com/goldbergyoni/nodebestpractices",
                "desc": "The #1 Node.js repository covering architecture, error handling, security, and event-loop optimization."
            }
        ],
        "interview_talking_point": "Articulate how Clean Architecture prevents database bleeding into domain logic, and how CQRS simplifies complex business rules while allowing independent optimization of read vs write paths."
    },
    {
        "phase_num": 3,
        "title": "High-Scale Databases, Distributed Caching & Concurrency",
        "subtitle": "SQL Query Optimization, Redis Advanced Patterns, & Concurrency Control",
        "est_hours": "14-18 Hours",
        "candidate_baseline": "Hands-on Redis caching for assessment queries and relational schema modeling at ExcelSoft.",
        "skip_advice": "Skip basic CRUD SQL queries (simple joins, inserts). Focus on indexing internals, query plans, and concurrency.",
        "must_learn": [
            "Relational Indexing & Query Execution Plans: Clustered vs Non-Clustered indexes, B-Trees, composite index column order, and analyzing `EXPLAIN ANALYZE`.",
            "Database Concurrency & ACID: Isolation levels (Read Committed, Repeatable Read, Serializable), dirty reads, phantom reads, and Optimistic Concurrency Control via row versioning (`[Timestamp]`).",
            "Redis Production Patterns: Cache-Aside, Write-Through, Cache Stampede prevention (Probabilistic Early Expiration), and Distributed Locking with Redlock.",
            "MongoDB Aggregation Framework: `$match`, `$group`, `$lookup` pipelines and compound index modeling for NoSQL applications."
        ],
        "study_materials": [
            {
                "name": "Use The Index, Luke! - SQL Indexing & Performance",
                "type": "Book / Guide",
                "url": "https://use-the-index-luke.com/",
                "desc": "The ultimate database performance guide explaining how B-Trees, indexes, and SQL optimizers actually work under the hood."
            },
            {
                "name": "Redis University - RU102JS & Advanced Caching Patterns",
                "type": "Interactive Course",
                "url": "https://university.redis.com/",
                "desc": "Free interactive official courses covering Redis data structures, distributed locking, TTL strategies, and Pub/Sub."
            },
            {
                "name": "Hussein Nasser - Database Engineering Mastery",
                "type": "Video Channel",
                "url": "https://www.youtube.com/@hnasr",
                "desc": "World-class deep dives into database connections, ACID isolation levels, WAL (Write-Ahead Logging), and database indexing."
            },
            {
                "name": "MongoDB University - Aggregation Framework Deep Dive",
                "type": "Official Course",
                "url": "https://learn.mongodb.com/",
                "desc": "Free hands-on lab on pipeline stages, indexing strategies, and document data modeling."
            }
        ],
        "interview_talking_point": "Share your ExcelSoft story where Redis caching offloaded read traffic by >60%, and explain how you handle cache stampedes and optimistic concurrency in multi-user environments."
    },
    {
        "phase_num": 4,
        "title": "Cloud Infrastructure, DevOps & Production Resilience",
        "subtitle": "AWS Cloud-Native Services, Docker Multi-Stage Builds, & CI/CD",
        "est_hours": "12-16 Hours",
        "candidate_baseline": "Familiarity deploying containerized services on Docker, Kubernetes, and AWS (EC2, S3, RDS, Lambda, CloudWatch).",
        "skip_advice": "Skip basic Docker commands (`docker run`, `docker build`). Focus on container optimization, secure networking, and deployment pipelines.",
        "must_learn": [
            "Docker Optimization: Multi-stage Dockerfiles, minimal base images (Alpine/Distroless), non-root users, and layer caching.",
            "AWS Architecture: VPC design (public vs private subnets), IAM least-privilege policies, Application Load Balancers (ALB), S3 pre-signed URLs, and RDS Multi-AZ failover.",
            "Continuous Integration / Deployment: GitHub Actions workflows with linting, unit testing, Docker image pushing to AWS ECR, and automated zero-downtime rolling deployments.",
            "Observability & Production Monitoring: Structured JSON logging (Serilog), distributed tracing with OpenTelemetry, and configuring CloudWatch alarms."
        ],
        "study_materials": [
            {
                "name": "AWS Skill Builder & Cloud Practitioner / Solutions Architect Guide",
                "type": "Official Training",
                "url": "https://explore.skillbuilder.aws/",
                "desc": "Official free learning paths covering AWS core networking, compute, storage, and security."
            },
            {
                "name": "TechWorld with Nana - Docker & Kubernetes Real-World Masterclass",
                "type": "Video Course",
                "url": "https://www.youtube.com/@TechWorldwithNana",
                "desc": "Practical, clear architectural explanations of Kubernetes manifests, pods, services, ingress, and deployments."
            },
            {
                "name": "GitHub Actions Official Documentation & Workflow Templates",
                "type": "Official Docs",
                "url": "https://docs.github.com/en/actions",
                "desc": "Step-by-step guides for automating build, test, Docker container publish, and cloud deployment pipelines."
            },
            {
                "name": "The Twelve-Factor App Methodology",
                "type": "Architecture Guide",
                "url": "https://12factor.net/",
                "desc": "The fundamental principles for building modern, scalable, cloud-native Software-as-a-Service applications."
            }
        ],
        "interview_talking_point": "Demonstrate your understanding of security by explaining why backend databases and APIs sit in private subnets, accessed only via ALBs with SSL termination and IAM roles rather than hardcoded credentials."
    },
    {
        "phase_num": 5,
        "title": "Full Stack System Design (LLD & HLD)",
        "subtitle": "Object-Oriented Design, SOLID, Design Patterns & High-Concurrency System Design",
        "est_hours": "16-20 Hours",
        "candidate_baseline": "Solid architectural intuition from building real-time proctoring and multi-role event management systems.",
        "skip_advice": "Skip theoretical textbook definitions without code. Focus on interview-style whiteboard design and trade-offs.",
        "must_learn": [
            "Low-Level Design (LLD): Applying SOLID principles, Factory, Strategy, Observer, Repository, and Unit of Work patterns in real C#/TypeScript applications.",
            "High-Level Design (HLD): Designing scalable distributed systems for SDE interviews (e.g. Real-Time Chat System, Flash-Sale E-Commerce, Live Location Tracker, Idempotent Payment Service).",
            "Scalability Fundamentals: Horizontal vs Vertical scaling, Load Balancers, Consistent Hashing, Database Sharding, Read Replicas, and CAP Theorem.",
            "API Schema Design: Designing RESTful resources with proper HTTP status codes, pagination (cursor-based vs offset), and WebSockets message schemas."
        ],
        "study_materials": [
            {
                "name": "System Design Primer by Donne Martin",
                "type": "GitHub Repository",
                "url": "https://github.com/donnemartin/system-design-primer",
                "desc": "The #1 System Design resource on the internet (270k+ stars). Complete guide with diagrams, sample interview questions, and trade-off analysis."
            },
            {
                "name": "Refactoring.Guru - Design Patterns & SOLID",
                "type": "Interactive Guide",
                "url": "https://refactoring.guru/design-patterns",
                "desc": "The clearest visual guide to design patterns with real code examples in C#, TypeScript, and Java."
            },
            {
                "name": "NeetCode - System Design for Beginners & SDEs",
                "type": "Video Channel",
                "url": "https://www.youtube.com/@NeetCode",
                "desc": "High-yield, intuitive walkthroughs of common system design interview problems (Rate Limiter, Chat App, URL Shortener)."
            },
            {
                "name": "ByteByteGo (Alex Xu) System Design Newsletter & Blog",
                "type": "Technical Blog",
                "url": "https://bytebytego.com/",
                "desc": "Clear visual architectural breakdowns of modern distributed systems (Netflix, Uber, Stripe, WhatsApp)."
            }
        ],
        "interview_talking_point": "In system design rounds, lead with requirement clarification (functional vs non-functional), establish throughput and storage estimates, draft the high-level API & architecture, and proactively address bottlenecks (caching, database scaling, fault tolerance)."
    }
]

def generate_roadmap_markdown():
    profile = load_candidate_profile()
    md = []
    md.append(f"# 🗺️ Tailored Full Stack Developer Upskilling Roadmap")
    md.append(f"### Candidate: {profile['name']} | {profile['current_title']}")
    md.append(f"**Target Goal:** Accelerate to {profile['target_level']} at Top Product & Tier-1 Tech Companies")
    md.append(f"**Current Baseline:** 2+ Years Enterprise Production Experience (React.js, TypeScript, ASP.NET Core, C#, Redis, WebSockets, AWS)")
    md.append(f"**Total Estimated Learning Time:** ~75-90 Hours across 5 Structured Milestones\n")
    md.append("---\n")

    md.append("## 📍 Your Starting Baseline (What You Already Have Proven on Resume)")
    md.append("You enter this roadmap with strong enterprise software experience. You do **NOT** need to start from scratch:")
    for s in profile["verified_strengths"]:
        md.append(f"- **{s}**: Proven in production modules (Saras Platform, SVKM, OwlBot) or full-stack projects.")
    md.append("\n---\n")

    md.append("## 🎯 Step-by-Step 5-Phase Master Roadmap\n")

    for phase in ROADMAP_PHASES:
        md.append(f"### Phase {phase['phase_num']}: {phase['title']}")
        md.append(f"*{phase['subtitle']}* | **Estimated Time:** {phase['est_hours']}\n")
        md.append(f"**Your Baseline:** {phase['candidate_baseline']}")
        md.append(f"💡 **What to Skip:** {phase['skip_advice']}\n")
        
        md.append("#### 🔑 What You Must Learn:")
        for item in phase["must_learn"]:
            md.append(f"- {item}")
        md.append("")

        md.append("#### 📚 Curated Free Study Materials & Documentation:")
        for res in phase["study_materials"]:
            md.append(f"- **[{res['name']}]({res['url']})** `[{res['type']}]`")
            md.append(f"  *{res['desc']}*")
        md.append("")

        md.append(f"> 🏆 **Interview Talking Point:** {phase['interview_talking_point']}\n")
        md.append("---\n")

    md.append("## 📅 Suggested 8-Week Execution Schedule")
    md.append("| Week | Focus Phase | Core Topics to Master | Key Deliverable / Capstone |")
    md.append("| :--- | :--- | :--- | :--- |")
    md.append("| **Week 1-2** | Phase 1: Frontend Mastery | Next.js App Router, RSC, Core Web Vitals | Build a Next.js 14 SSR portal with TanStack Query caching |")
    md.append("| **Week 3-4** | Phase 2: Enterprise Backend | Clean Architecture, CQRS, MediatR, Node.js | Refactor an API using Jason Taylor's Clean Architecture template |")
    md.append("| **Week 5** | Phase 3: Databases & Caching | SQL Indexing plans, Redis Cache-Aside, Redlock | Benchmark SQL query execution plan before vs after composite indexing |")
    md.append("| **Week 6** | Phase 4: Cloud & DevOps | AWS VPC/IAM, Multi-stage Docker, GitHub CI/CD | Write a GitHub Actions pipeline building & deploying a container to AWS |")
    md.append("| **Week 7-8** | Phase 5: System Design | LLD Patterns & HLD Distributed Architecture | Whiteboard & practice design for Flash-Sale / Real-Time Chat System |")

    return "\n".join(md)

def main():
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / "FULLSTACK_ROADMAP.md"
    content = generate_roadmap_markdown()
    out_file.write_text(content, encoding="utf-8")
    print(f"✅ Generated personalized Full Stack Roadmap at: {out_file}")

if __name__ == "__main__":
    main()

