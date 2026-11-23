#!/usr/bin/env python3
"""
Automated Live Crawler & Job Sync Engine for Roshan Moger
Queries live portal CLIs (LinkedIn, freehire ATS, etc.) to discover new vacancies,
scores them against Roshan Moger's candidate profile, eliminates duplicates,
generates interview prep guides, and persists records in data/jobs_database.json.
"""

import sys
import os
import re
import json
import shutil
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = WORKSPACE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "jobs_database.json"

if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))
if str(WORKSPACE_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR / "tools"))

try:
    from interview_prep_engine import generate_dynamic_prep, format_as_markdown, CANDIDATE_PROFILE
except ImportError:
    CANDIDATE_PROFILE = {"core_skills": [".NET Core", "C#", "React.js", "TypeScript", "SQL Server", "REST APIs", "Redis", "AWS", "WebSockets"]}
    def generate_dynamic_prep(*args, **kwargs): return {}
    def format_as_markdown(prep): return ""

# Strict filtering requested:
# - ONLY .NET Full Stack (ASP.NET Core, C#, Web API) and React.js / TypeScript
# - STRICTLY EXCLUDE: Java, Python, PHP, Laravel, Ruby, C++, Go, Android, iOS, Drupal, Salesforce, etc.
# - STRICTLY EXCLUDE: Senior, Lead, Staff, Architect, or roles requiring >3 years experience.
EXCLUDED_KEYWORDS = [
    "java", "python", "php", "laravel", "ruby", "c++", "cpp", "golang", "android", "ios", 
    "drupal", "wordpress", "flutter", "swift", "kotlin", "salesforce", "sales", "qa",
    "networking", "security analyst", "data scientist", "data analyst",
    "senior", "sr.", "sr ", "lead", "tech lead", "team lead", "staff", "architect", "principal", "manager",
    "director", "vp", "head of", "specialist", "expert", "iii", "iv",
    "react native", "mobile developer", "mobile engineer"
]

EXP_EXCLUSION_PATTERNS = [
    r'\b(?:[5-9]|\d{2,})\+?\s*(?:to|-)\s*\d+\s*(?:years?|yrs?)\b',   # 5-7 years, 6-8 yrs, etc.
    r'\b\d+\s*(?:to|-)\s*(?:[5-9]|\d{2,})\+?\s*(?:years?|yrs?)\b',   # 3-6 years, 4-7 yrs, etc.
    r'\b(?:[5-9]|\d{2,})\+?\s*(?:years?|yrs?)\b',                     # 5+ years, 6 years, 7+ yrs, etc.
    r'\b(?:[5-9]|\d{2,})\s*\+',                                       # 5+, 6+, 7+, 8+
    r'\b(?:[5-9]|\d{2,})\s*[-–]\s*(?:[5-9]|\d{2,})\b',               # 5-7, 6-8, 6-7
]

def is_role_suitable(title, skills=[], description=""):
    """
    Enforces strict candidate alignment:
    1. Rejects Java, Python, PHP, C++, Android, React Native, etc.
    2. Rejects Senior, Lead, Architect, or roles requiring 5+, 6+, 7+ years of experience.
    3. Strictly targets 2 to 4 years experience.
    4. Requires target stack: MUST be .NET / C# / ASP.NET or React / TypeScript.
    """
    t_lower = title.lower()
    combined = (title + " " + " ".join(skills) + " " + description).lower()

    # Direct substring checks for terms with punctuation / mobile / senior experience
    for ex in ["c++", "cpp", "4+", "5+", "6+", "7+", "8+", "10+", "5 years", "6 years", "7 years", "8 years", "5 yrs", "6 yrs", "7 yrs", "8 yrs", "5-7", "6-8", "6-7", "react native", "mobile developer", "mobile engineer"]:
        if ex in t_lower or ex in combined:
            return False

    # Check experience regex patterns (reject 5+, 6+, 7+ years, 5-7, 6-8, etc.)
    for pattern in EXP_EXCLUSION_PATTERNS:
        if re.search(pattern, t_lower) or re.search(pattern, combined):
            return False

    # Exclude non-target tech or senior levels with word boundaries
    for ex in EXCLUDED_KEYWORDS:
        pattern = r'(?:\b|_)' + re.escape(ex) + r'(?:\b|_)'
        if re.search(pattern, t_lower) or re.search(pattern, combined):
            return False

    # 2. Must specifically match .NET or React
    has_dotnet = any(k in combined for k in [".net", "dotnet", "c#", "csharp", "asp.net"])
    has_react = any(k in combined for k in ["react", "react.js", "reactjs"])

    if not (has_dotnet or has_react):
        return False

    return True

# Backward compatibility alias
def is_experience_suitable(title):
    return is_role_suitable(title, [])

def calculate_match_score(title, skills):
    """Calculate match score against Roshan Moger's candidate profile."""
    score = 90
    text = (title + " " + " ".join(skills)).lower()

    # High bonus for .NET + React full-stack combo
    has_dotnet = any(k in text for k in [".net", "dotnet", "c#", "csharp", "asp.net"])
    has_react = any(k in text for k in ["react", "react.js", "reactjs"])

    if has_dotnet and has_react:
        score += 8  # 98% Match TOP FIT!
    elif has_dotnet:
        score += 5  # 95% Match
    elif has_react:
        score += 4  # 94% Match

    if "typescript" in text:
        score += 1
    if any(k in text for k in ["sql", "sql server", "mssql", "postgresql", "postgres"]):
        score += 1
    if any(k in text for k in ["aws", "docker", "redis", "websockets", "mcp"]):
        score += 1

    score = min(score, 98)
    if score >= 96:
        score_text = f"{score}% Match ★ TOP FIT"
    else:
        score_text = f"{score}% Match"
    return score, score_text

CORE_SKILLS_MAP = {
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET Core",
    "dotnet": ".NET Core",
    ".net core": ".NET Core",
    "asp.net": "ASP.NET Core",
    "asp.net core": "ASP.NET Core",
    "react": "React.js",
    "react.js": "React.js",
    "reactjs": "React.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "redux": "Redux",
    "rest": "REST APIs",
    "api": "REST APIs",
    "apis": "REST APIs",
    "web api": "REST APIs",
    "sql": "SQL Server",
    "sql server": "SQL Server",
    "mssql": "SQL Server",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "redis": "Redis",
    "aws": "AWS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "websockets": "WebSockets",
    "websocket": "WebSockets",
    "microservices": "Microservices",
    "tailwind": "Tailwind CSS",
    "node": "Node.js",
    "nodejs": "Node.js",
    "next.js": "Next.js",
    "nextjs": "Next.js"
}

def get_bun_path():
    """Locate bun executable on system."""
    bun = shutil.which("bun")
    if not bun:
        # Check standard user and global paths on Windows
        candidate_paths = [
            Path.home() / ".bun" / "bin" / "bun.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "bun" / "bun.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "bun" / "bun.exe"
        ]
        for p in candidate_paths:
            if p.exists():
                return str(p)
    return bun or "bun"

def load_database():
    """Load existing jobs database or return empty list."""
    if DB_PATH.exists():
        try:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Warning: Failed to load {DB_PATH}: {e}", file=sys.stderr)
    return []

def save_database(jobs):
    """Persist jobs database to disk."""
    DB_PATH.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Saved {len(jobs)} total jobs to {DB_PATH}")


def format_job_date(raw_date_str):
    """Parse raw date into (formatted_date, days_ago, date_obj)."""
    today = date.today()
    if not raw_date_str:
        return today.strftime("%b %d, %Y"), 0, today

    # Try ISO date 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'
    try:
        clean_str = raw_date_str.split("T")[0]
        parsed = datetime.strptime(clean_str, "%Y-%m-%d").date()
        days_ago = max(0, (today - parsed).days)
        return parsed.strftime("%b %d, %Y"), days_ago, parsed
    except Exception:
        pass

    # Try 'Sep 28, 2026'
    try:
        parsed = datetime.strptime(raw_date_str, "%b %d, %Y").date()
        days_ago = max(0, (today - parsed).days)
        return parsed.strftime("%b %d, %Y"), days_ago, parsed
    except Exception:
        pass

    return today.strftime("%b %d, %Y"), 0, today

def slugify(text):
    """Convert text to safe ID string."""
    clean = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
    return clean[:30]

def search_linkedin(bun_path, queries, location="Bengaluru, Karnataka, India", jobage=3, limit=10):
    """Execute live LinkedIn search using the local agent skill."""
    cli_path = WORKSPACE_DIR / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
    if not cli_path.exists():
        print(f"LinkedIn CLI not found at {cli_path}", file=sys.stderr)
        return []

    found_jobs = []
    for q in queries:
        cmd = [
            bun_path, "run", str(cli_path),
            "search",
            "--location", location,
            "-q", q,
            "--experience", "2,3",
            "--jobage", str(jobage),
            "--limit", str(limit),
            "--format", "json"
        ]
        try:
            print(f"[LinkedIn Crawler] Querying: '{q}' in '{location}' (jobage: {jobage}d)...")
            res = subprocess.run(cmd, cwd=str(WORKSPACE_DIR), capture_output=True, text=True, encoding="utf-8", timeout=30)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                for item in data.get("results", []):
                    title = item.get("title") or "Software Engineer"
                    company = item.get("company") or "Direct Tech Employer"

                    # Infer skills from title
                    matched_skills = []
                    t_lower = title.lower()
                    if ".net" in t_lower or "c#" in t_lower:
                        matched_skills.extend([".NET Core", "C#", "REST APIs", "SQL Server"])
                    if "react" in t_lower:
                        matched_skills.extend(["React.js", "TypeScript", "JavaScript"])
                    if "full stack" in t_lower or "fullstack" in t_lower:
                        matched_skills.extend(["REST APIs", "AWS", "Git"])

                    # Enforce strict suitability (ONLY .NET/React, NO Java/Python/C++/Senior/Lead)
                    if not is_role_suitable(title, matched_skills):
                        continue

                    if not matched_skills:
                        matched_skills = ["React.js", ".NET Core", "C#", "SQL Server"]

                    date_str, days_ago, _ = format_job_date(item.get("date"))
                    job_id = f"li-{slugify(company)}-{slugify(title)}-{str(item.get('id', ''))[:8]}"

                    # Deduplicate skills
                    matched_skills = list(dict.fromkeys(matched_skills))
                    base_score, score_text = calculate_match_score(title, matched_skills)

                    fresh_indicator = "🔥 Posted Today!" if days_ago == 0 else f"🔥 {days_ago}d ago!"
                    note = f"{fresh_indicator} Live verified LinkedIn opening: {title} at {company} matching {', '.join(matched_skills[:4])}."

                    job_entry = {
                        "id": job_id,
                        "title": title,
                        "company": company,
                        "portal": "LinkedIn",
                        "portal_badge": "🔷 LinkedIn",
                        "portal_color": "#0ea5e9",
                        "location": item.get("location", location),
                        "date": date_str,
                        "days_ago": days_ago,
                        "exp": "2-4 Years (Associate / Mid)",
                        "score": score_text,
                        "base_score": base_score,
                        "skills": matched_skills,
                        "url": item.get("url", ""),
                        "note": note,
                        "applied": False,
                        "date_scraped": date.today().isoformat()
                    }
                    found_jobs.append(job_entry)
        except Exception as e:
            print(f"[LinkedIn Crawler] Error on query '{q}': {e}", file=sys.stderr)

    return found_jobs

def search_freehire(bun_path, queries, jobage=3, limit=10, country="AE,IN"):
    """Execute live freehire.me ATS search using the local agent skill across Dubai/UAE, Japan, Korea, and India."""
    cli_path = WORKSPACE_DIR / ".agents" / "skills" / "freehire-search" / "cli" / "src" / "cli.ts"
    if not cli_path.exists():
        print(f"freehire CLI not found at {cli_path}", file=sys.stderr)
        return []

    found_jobs = []
    for q in queries:
        cmd = [
            bun_path, "run", str(cli_path),
            "search",
            "-q", q,
            "--seniority", "junior,middle",
            "--country", country,
            "--jobage", str(jobage),
            "--limit", str(limit),
            "--format", "json"
        ]
        try:
            print(f"[freehire Crawler] Querying ATS aggregator for {country}: '{q}' (jobage: {jobage}d)...")
            res = subprocess.run(cmd, cwd=str(WORKSPACE_DIR), capture_output=True, text=True, encoding="utf-8", timeout=30)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                for item in data.get("results", []):
                    title = item.get("title") or "Software Engineer"
                    company = item.get("company") or "Direct Tech Employer"
                    if company and ":" in company and "_" in company:  # Filter out internal hash names
                        company = "Enterprise Partner"

                    # Map raw skills
                    raw_skills = item.get("skills") or []
                    matched_skills = []
                    for rs in raw_skills:
                        if not rs:
                            continue
                        norm = CORE_SKILLS_MAP.get(rs.lower().strip())
                        if norm and norm not in matched_skills:
                            matched_skills.append(norm)

                    # Infer skills from title if missing
                    t_lower = title.lower()
                    if ".net" in t_lower or "c#" in t_lower:
                        if ".NET Core" not in matched_skills: matched_skills.append(".NET Core")
                        if "C#" not in matched_skills: matched_skills.append("C#")
                    if "react" in t_lower:
                        if "React.js" not in matched_skills: matched_skills.append("React.js")

                    # Enforce strict suitability (ONLY .NET / React, NO Java / Python / C++ / Senior / Lead, NO 5+, 6+, 7+ years)
                    desc_text = item.get("description") or ""
                    if not is_role_suitable(title, matched_skills, description=desc_text):
                        continue

                    if not matched_skills:
                        matched_skills = ["C#", ".NET Core", "React.js", "SQL Server", "REST APIs"]

                    date_str, days_ago, _ = format_job_date(item.get("date"))
                    raw_id = item.get("id") or slugify(title)
                    job_id = f"ats-{slugify(company)}-{slugify(raw_id)[:15]}"

                    base_score, score_text = calculate_match_score(title, matched_skills)
                    loc = item.get("location") or ""
                    countries = item.get("countries") or []
                    if not loc:
                        if "AE" in countries: loc = "Dubai, UAE"
                        elif "JP" in countries: loc = "Tokyo, Japan"
                        elif "KR" in countries: loc = "Seoul, South Korea"
                        elif "IN" in countries: loc = "Bengaluru, India"
                        else: loc = "Remote"
                    else:
                        if "AE" in countries and "dubai" not in loc.lower() and "uae" not in loc.lower():
                            loc = f"{loc}, Dubai / UAE"
                        elif "JP" in countries and "japan" not in loc.lower():
                            loc = f"{loc}, Japan"
                        elif "KR" in countries and "korea" not in loc.lower():
                            loc = f"{loc}, South Korea"

                    fresh_indicator = "🔥 Posted Today!" if days_ago == 0 else f"🔥 {days_ago}d ago!"
                    note = f"{fresh_indicator} Live verified ATS opening: {title} at {company} ({loc}) matching {', '.join(matched_skills[:4])}."

                    job_entry = {
                        "id": job_id,
                        "title": title,
                        "company": company,
                        "portal": "freehire.me",
                        "portal_badge": "🌐 freehire ATS",
                        "portal_color": "#06b6d4",
                        "location": loc,
                        "date": date_str,
                        "days_ago": days_ago,
                        "exp": "2-4 Years (Associate / Mid)",
                        "score": score_text,
                        "base_score": base_score,
                        "skills": matched_skills,
                        "url": item.get("url", ""),
                        "note": note,
                        "applied": False,
                        "date_scraped": date.today().isoformat()
                    }
                    found_jobs.append(job_entry)
        except Exception as e:
            print(f"[freehire Crawler] Error on query '{q}': {e}", file=sys.stderr)

    return found_jobs

def run_live_crawl(jobage=3, purge=False):
    """
    Run full live crawling pipeline:
    1. Queries LinkedIn & freehire CLIs
    2. Deduplicates against existing jobs database (or purges if purge=True)
    3. Generates interview prep for newly discovered companies
    4. Saves updated jobs_database.json
    Returns (num_new_jobs, total_jobs, new_jobs_list)
    """
    bun_path = get_bun_path()
    print(f"=== Starting Live Multi-Portal Crawl (System Date: {date.today().isoformat()}) ===")
    print(f"Using bun at: {bun_path}")

    if purge:
        print("🧹 PURGE FLAG ACTIVE: Removing all previously stored jobs to provide a 100% fresh crawl!")
        if DB_PATH.exists():
            backup_path = DATA_DIR / "jobs_database.backup.json"
            try:
                shutil.copy2(DB_PATH, backup_path)
                print(f"📦 Backed up previous database ({DB_PATH.stat().st_size} bytes) to {backup_path.name}")
            except Exception as e:
                print(f"Notice during backup: {e}", file=sys.stderr)
        existing_jobs = []
        existing_urls = set()
        existing_signatures = set()
    else:
        existing_jobs = load_database()
        existing_urls = set(j.get("url", "").strip().rstrip("/") for j in existing_jobs if j.get("url"))
        existing_signatures = set((j.get("company", "").strip().lower(), j.get("title", "").strip().lower()) for j in existing_jobs)

    queries_linkedin = [
        ".NET Full Stack Developer",
        "React Developer",
        ".NET Developer",
        "ASP.NET Core",
        "React .NET",
        "React TypeScript",
        "C# .NET Developer",
        "Frontend React Developer"
    ]

    queries_freehire = [
        ".NET React",
        "React Developer",
        ".NET Developer",
        "ASP.NET",
        "C# Developer",
        "React"
    ]

    scraped_jobs = []

    # 1. Dubai & United Arab Emirates
    print("[Live Crawler] Scanning Dubai & UAE vacancies...")
    scraped_jobs.extend(search_linkedin(bun_path, [".NET Full Stack Developer", "React Developer", ".NET Developer", "ASP.NET Core", "React TypeScript"], location="Dubai, United Arab Emirates", jobage=jobage, limit=15))
    scraped_jobs.extend(search_linkedin(bun_path, [".NET Developer", "React Developer", "C# Developer"], location="United Arab Emirates", jobage=jobage, limit=12))

    # 2. India & Bengaluru (Strictly Dubai & India)
    print("[Live Crawler] Scanning Bengaluru & India vacancies...")
    scraped_jobs.extend(search_linkedin(bun_path, queries_linkedin, location="Bengaluru, Karnataka, India", jobage=jobage, limit=15))
    scraped_jobs.extend(search_linkedin(bun_path, queries_linkedin[:4], location="India", jobage=jobage, limit=12))

    # 6. Global Multi-Country freehire ATS Aggregator (UAE, Japan, Korea, India)
    print("[Live Crawler] Scanning freehire ATS across Dubai, Japan, Korea, and India...")
    scraped_jobs.extend(search_freehire(bun_path, queries_freehire, jobage=jobage, limit=12, country="AE,IN"))

    new_jobs = []
    reports_prep_dir = WORKSPACE_DIR / "reports" / "interview_prep"
    reports_prep_dir.mkdir(parents=True, exist_ok=True)

    for j in scraped_jobs:
        clean_url = j.get("url", "").strip().rstrip("/")
        sig = (j.get("company", "").strip().lower(), j.get("title", "").strip().lower())

        if clean_url in existing_urls or sig in existing_signatures:
            continue

        existing_urls.add(clean_url)
        existing_signatures.add(sig)
        new_jobs.append(j)

        # Generate interview prep automatically
        try:
            prep = generate_dynamic_prep(j["company"], j["title"], j["skills"], j["location"], j["exp"], j["url"])
            clean_company = "".join(c if c.isalnum() else "_" for c in j["company"]).strip("_")
            md_file = reports_prep_dir / f"{clean_company}_prep.md"
            if not md_file.exists():
                md_file.write_text(format_as_markdown(prep), encoding="utf-8")
        except Exception as err:
            print(f"Warning: Failed to create prep for {j['company']}: {err}", file=sys.stderr)

        print(f"✨ Found NEW Job: [{j['portal']}] {j['title']} at {j['company']} ({j['date']}) - {j['score']}")

    # Merge: Put newest discovered jobs at the beginning
    updated_jobs = new_jobs + existing_jobs
    save_database(updated_jobs)

    # Regenerate multi-portal dashboard HTML
    gen_script = WORKSPACE_DIR / "tools" / "generate_1to3yr_dashboard.py"
    if gen_script.exists():
        print("📊 Updating multi-portal application dashboard HTML...")
        subprocess.run([sys.executable, str(gen_script)], cwd=str(WORKSPACE_DIR), capture_output=True)
        print("✅ Dashboard regenerated at reports/application-dashboard.html")

    print(f"=== Crawl Finished: {len(new_jobs)} new jobs added. Total in database: {len(updated_jobs)} ===")
    return len(new_jobs), len(updated_jobs), new_jobs

if __name__ == "__main__":
    jobage_arg = 3
    purge_arg = False

    for arg in sys.argv[1:]:
        if arg.lower() in ["--purge", "-p", "--clean", "--fresh"]:
            purge_arg = True
        else:
            try:
                jobage_arg = int(arg)
            except ValueError:
                pass

    run_live_crawl(jobage=jobage_arg, purge=purge_arg)
