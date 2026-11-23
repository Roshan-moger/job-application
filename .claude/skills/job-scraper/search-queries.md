# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

**Language scope:** write every query category in every language listed in your CLAUDE.md Languages table (typically 1-2, sometimes more). A posting requiring a language you have _not_ declared, as a job condition, is excluded before scoring; a posting requiring a _higher level_ than you declared in a language you _do_ work in is flagged for your own judgment, not excluded — see `04-job-evaluation.md`'s Language Gate, the single source of truth for this rule. Translate each category's keywords rather than machine-translating word-for-word (e.g. "Frontend Developer" -> "Desarrollador Frontend", not a literal word-for-word translation) if you work in more than one language.

## Search Sites

Primary:

- **linkedin.com/jobs** - LinkedIn tech job listings (covered by `linkedin-search` CLI)
- **freehire.me** - Tech roles aggregator covering ~50 ATS systems (covered by `freehire-search` CLI)
- **instahyre.com** / **naukri.com** / **wellfound.com** - Leading tech and startup job boards in India & Remote

Secondary:

- Direct Google searches with `site:` filters for high-growth tech companies and enterprise engineering teams.

## Query Categories

### Priority 1: Full Stack Web Development

Core career direction combining React/TypeScript with ASP.NET Core / C# / Node.js.

```
site:linkedin.com/jobs "Full Stack Developer" "React" "ASP.NET Core" Bangalore OR Remote
site:linkedin.com/jobs "Full Stack Engineer" "TypeScript" "C#" India
site:linkedin.com/jobs "Full Stack Developer" "React" "Node.js" Mysore OR Bangalore
site:instahyre.com "Full Stack Developer" "React" "ASP.NET"
site:wellfound.com "Full Stack Developer" "React" "TypeScript"
```

### Priority 2: Frontend Engineering (React / TypeScript)

Roles emphasizing high-performance, responsive UI and real-time state management.

```
site:linkedin.com/jobs "Frontend Developer" "React.js" "TypeScript" Bangalore OR Remote
site:linkedin.com/jobs "React Developer" "Redux" "Tailwind" India
site:instahyre.com "Frontend Engineer" "React" "TypeScript"
```

### Priority 3: Backend Engineering (ASP.NET Core / C# / Node.js)

Roles emphasizing API design, distributed architecture, caching (Redis), and real-time communication.

```
site:linkedin.com/jobs ".NET Developer" "ASP.NET Core" "C#" Bangalore OR Remote
site:linkedin.com/jobs "Backend Developer" "C#" "REST API" India
site:linkedin.com/jobs "Backend Engineer" "Node.js" "Redis" Remote
```

### Priority 4: Cloud & Web Software Engineering

Broader software engineering opportunities across modern cloud infrastructure.

```
site:linkedin.com/jobs "Software Engineer" "React" "AWS" India
site:linkedin.com/jobs "Software Development Engineer" "Full Stack" Bangalore
site:wellfound.com "Software Engineer" "Docker" "AWS" "React"
```

## Location Filter

When evaluating results, verify the job location meets Roshan's preferences:

- **Ideal:** Mysore, Bangalore (Bengaluru), or 100% Remote (India / International)
- **Acceptable (Hybrid / Relocation):** Hyderabad, Pune, Chennai, Delhi NCR (Gurgaon / Noida)
- **International:** Remote globally or relocation with sponsorship (Europe, UK, APAC, Middle East)

## Language Filter

Your working languages and levels are in CLAUDE.md's Languages table. When filtering scraped results, apply `04-job-evaluation.md`'s Language Gate: a posting requiring a language you haven't declared at all is excluded; a posting requiring a higher level than you declared in a language you do work in is not excluded, flag it clearly instead (see `job-scraper/SKILL.md`'s Step 3 "Quick Fit Assessment" for how the flag surfaces in `/scrape` output). Postings simply _written_ in a language you don't work in, that don't require it on the job, are fine.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:

- "/scrape [focus_area]" -> relevant category queries + custom focus-specific queries
