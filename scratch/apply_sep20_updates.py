import re
import json
import datetime
from pathlib import Path
import ast

dashboard_path = Path("tools/generate_1to3yr_dashboard.py")
content = dashboard_path.read_text(encoding="utf-8")

today = datetime.date(2026, 9, 20)

def fix_surrogates(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("utf-16", "surrogatepass").decode("utf-16")
    except Exception:
        return s

def parse_job_date(date_str):
    return datetime.datetime.strptime(date_str, "%b %d, %Y").date()

new_sep19_jobs = [
    {
        "id": "ibm-cloud-fullstack-linkedin",
        "title": "Application Developer - Azure Cloud FullStack (.NET Core & ReactJS)",
        "company": "IBM",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 19, 2026",
        "days_ago": 1,
        "exp": "1-3 Years (Full Stack)",
        "score": "96% Match",
        "base_score": 96,
        "skills": [".NET Core", "C#", "React.js", "TypeScript", "Azure", "Microservices", "REST APIs", "Redis", "Docker"],
        "url": "https://in.linkedin.com/jobs/view/application-developer-azure-cloud-fullstack-at-ibm-4457231072",
        "note": "🔥 1d ago! IBM Consulting modern cloud-native role: microservices using .NET Core, SPAs in ReactJS, Azure Cloud, and Redis caching."
    },
    {
        "id": "omnissa-csharp-dotnet-linkedin",
        "title": "Software Engineer - C#.NET & Distributed Systems",
        "company": "Omnissa",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India (Hybrid)",
        "date": "Sep 19, 2026",
        "days_ago": 1,
        "exp": "1-3 Years (Software Engineer)",
        "score": "95% Match",
        "base_score": 95,
        "skills": ["C#", ".NET Core", "ASP.NET", "PostgreSQL", "SQL", "Redis", "Distributed Systems", "REST APIs"],
        "url": "https://in.linkedin.com/jobs/view/software-engineer-senior-se-staff-engineer-c%23-net-at-omnissa-4414762028",
        "note": "🔥 1d ago! Core UEM platform engineering: C#, .NET Core, event-driven distributed systems, Redis, and SQL/PostgreSQL."
    },
    {
        "id": "scoutit-sep19-linkedin",
        "title": "React Developer (Associate)",
        "company": "Scoutit",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 19, 2026",
        "days_ago": 1,
        "exp": "1-3 Years (Associate)",
        "score": "94% Match",
        "base_score": 94,
        "skills": ["React.js", "Redux", "JavaScript", "RESTful APIs", "JWT", "Webpack", "Tailwind CSS"],
        "url": "https://in.linkedin.com/jobs/view/react-developer-at-scoutit-4468089223",
        "note": "🔥 1d ago! Associate front-end developer for modular React component libraries, Redux workflows, and REST API integration."
    },
    {
        "id": "osfin-ai-frontend-linkedin",
        "title": "Frontend Engineer - React.js & FinOps Intelligence",
        "company": "Osfin.ai",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru East, Karnataka, India",
        "date": "Sep 19, 2026",
        "days_ago": 1,
        "exp": "1-3 Years",
        "score": "93% Match",
        "base_score": 93,
        "skills": ["React.js", "TypeScript", "Redux", "REST APIs", "Web Performance", "Tailwind CSS"],
        "url": "https://www.linkedin.com/jobs/view/4468040638",
        "note": "🔥 1d ago! FinTech transaction intelligence SaaS platform: performant React UI architecture and client state management."
    }
]

start_idx = content.find("jobs_data = [")
end_marker = "\n]\n\n# Pre-generate prep guides for all roles"
end_idx = content.find(end_marker)

jobs_code = content[start_idx + len("jobs_data = "):end_idx + 2]
raw_jobs = ast.literal_eval(jobs_code)

seen_ids = set()
cleaned_existing = []
for j in raw_jobs:
    if j["id"] in seen_ids:
        continue
    seen_ids.add(j["id"])
    cleaned_existing.append(j)

updated_jobs = []
sep19_inserted = False

for j in cleaned_existing:
    for k, v in j.items():
        if isinstance(v, str):
            j[k] = fix_surrogates(v)
        elif isinstance(v, list):
            j[k] = [fix_surrogates(x) if isinstance(x, str) else x for x in v]

    dt = parse_job_date(j["date"])
    days_ago = (today - dt).days
    j["days_ago"] = max(0, days_ago)

    # Clean note if older than 3 days
    if j["days_ago"] >= 4:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|1d ago!|2d ago!|3d ago!)\s*", "", j["note"])
    elif j["days_ago"] == 2:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|1d ago!|3d ago!)\s*", "🔥 2d ago! ", j["note"])
    elif j["days_ago"] == 3:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|1d ago!|2d ago!)\s*", "🔥 3d ago! ", j["note"])

    # Insert Sep 19 jobs before ge-vernova-linkedin
    if j["id"] == "ge-vernova-linkedin" and not sep19_inserted:
        for new_j in new_sep19_jobs:
            if new_j["id"] not in seen_ids:
                updated_jobs.append(new_j)
                seen_ids.add(new_j["id"])
        sep19_inserted = True

    updated_jobs.append(j)

# If not inserted, put at top of LinkedIn section
for new_j in new_sep19_jobs:
    if new_j["id"] not in [x["id"] for x in updated_jobs]:
        updated_jobs.insert(0, new_j)

print(f"Total jobs count for Sep 20: {len(updated_jobs)}")

# Format as Python code
def format_job(j):
    lines = ["    {"]
    lines.append(f'        "id": {json.dumps(j["id"], ensure_ascii=False)},')
    lines.append(f'        "title": {json.dumps(j["title"], ensure_ascii=False)},')
    lines.append(f'        "company": {json.dumps(j["company"], ensure_ascii=False)},')
    lines.append(f'        "portal": {json.dumps(j["portal"], ensure_ascii=False)},')
    lines.append(f'        "portal_badge": {json.dumps(j["portal_badge"], ensure_ascii=False)},')
    lines.append(f'        "portal_color": {json.dumps(j["portal_color"], ensure_ascii=False)},')
    lines.append(f'        "location": {json.dumps(j["location"], ensure_ascii=False)},')
    lines.append(f'        "date": {json.dumps(j["date"], ensure_ascii=False)},')
    lines.append(f'        "days_ago": {j["days_ago"]},')
    lines.append(f'        "exp": {json.dumps(j["exp"], ensure_ascii=False)},')
    lines.append(f'        "score": {json.dumps(j["score"], ensure_ascii=False)},')
    lines.append(f'        "base_score": {j["base_score"]},')
    lines.append(f'        "skills": {json.dumps(j["skills"], ensure_ascii=False)},')
    lines.append(f'        "url": {json.dumps(j["url"], ensure_ascii=False)},')
    lines.append(f'        "note": {json.dumps(j["note"], ensure_ascii=False)}')
    if "cv_link" in j:
        lines[-1] += ","
        lines.append(f'        "cv_link": {json.dumps(j["cv_link"], ensure_ascii=False)}')
    lines.append("    }")
    return "\n".join(lines)

formatted_sections = []
formatted_sections.append("jobs_data = [")

portal_headers = {
    "google-fresh": "    # --- DIRECT COMPANY CAREER PORTALS ---",
    "accenture-naukri": "    # --- NAUKRI.COM (India's #1 Tech Job Board - Max 3 Days) ---",
    "siemens-indeed": "    # --- INDEED INDIA (Max 3 Days Filtered) ---",
    "zepto-instahyre": "    # --- INSTAHYRE (Curated High-Growth Tech Hiring) ---",
    "oracle-fresh": "    # --- WELLFOUND / ANGELIST (High-Growth Startups & Scaleups) ---",
    "ge-vernova-workday": "    # --- FREEHIRE.ME & GLOBAL ATS PLATFORMS (Fresh 3-Day & Enterprise) ---",
    "ibm-cloud-fullstack-linkedin": "    # --- LINKEDIN VERIFIED POSTINGS (Sep 19-20, 2026 Live Updates) ---"
}

for idx, j in enumerate(updated_jobs):
    if j["id"] in portal_headers:
        if idx > 0:
            formatted_sections.append("")
        formatted_sections.append(portal_headers[j["id"]])
    job_str = format_job(j)
    if idx < len(updated_jobs) - 1:
        job_str += ","
    formatted_sections.append(job_str)

formatted_sections.append("]")
new_jobs_code = "\n".join(formatted_sections)

new_content = content[:start_idx] + new_jobs_code + content[end_idx + 2:]
dashboard_path.write_text(new_content, encoding="utf-8")
print("Successfully wrote updated jobs_data for Sep 20, 2026!")

