import re
import json
import datetime
from pathlib import Path

dashboard_path = Path("tools/generate_1to3yr_dashboard.py")
content = dashboard_path.read_text(encoding="utf-8")

today = datetime.date(2026, 9, 18)

def fix_surrogates(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("utf-16", "surrogatepass").decode("utf-16")
    except Exception:
        return s

def parse_job_date(date_str):
    # e.g. "Sep 08, 2026" or "Aug 20, 2026"
    return datetime.datetime.strptime(date_str, "%b %d, %Y").date()

new_linkedin_jobs = [
    {
        "id": "ge-vernova-linkedin",
        "title": "Software Engineer (C# .NET & ReactJS)",
        "company": "GE Vernova",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 18, 2026",
        "days_ago": 0,
        "exp": "2-5 Years (Full Stack)",
        "score": "98% Match ★ TOP FIT",
        "base_score": 98,
        "skills": ["C#", ".NET Core", "ASP.NET Core", "React.js", "TypeScript", "AWS", "Docker", "SQL Server", "PostgreSQL", "REST APIs", "Microservices", "SOLID"],
        "url": "https://www.linkedin.com/jobs/view/4469146208",
        "note": "🔥 Posted Today! 98% Match! 1:1 stack match for ASP.NET Core, C#, ReactJS, TypeScript, AWS, Docker, Microservices, and SQL/Postgres in Bengaluru."
    },
    {
        "id": "yash-tech-linkedin",
        "title": "Software Engineer - (C#/.NET & React)",
        "company": "YASH Technologies",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 18, 2026",
        "days_ago": 0,
        "exp": "2-5 Years (Full Stack)",
        "score": "96% Match",
        "base_score": 96,
        "skills": ["C#", ".NET Core", "React.js", "RESTful APIs", "Microservices", "SQL", "Git", "OOP"],
        "url": "https://in.linkedin.com/jobs/view/software-engineer-c%23-net-react-job-at-yash-technologies-4467846891",
        "note": "🔥 Posted Today! Full Stack Developer C#/.NET Core and React for enterprise web apps, microservices & REST APIs in Bengaluru."
    },
    {
        "id": "scoutit-sep18-linkedin",
        "title": "React Developer",
        "company": "Scoutit",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 18, 2026",
        "days_ago": 0,
        "exp": "1-3 Years (Associate)",
        "score": "94% Match",
        "base_score": 94,
        "skills": ["React.js", "TypeScript", "Redux", "JavaScript", "REST APIs", "Tailwind CSS"],
        "url": "https://in.linkedin.com/jobs/view/4467840641",
        "note": "🔥 Posted Today! Front-end React developer role for modular component libraries, Redux state, and API integration."
    },
    {
        "id": "eurofins-sep18-linkedin",
        "title": "Software Engineer (.NET Core & React/Angular)",
        "company": "Eurofins",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 18, 2026",
        "days_ago": 0,
        "exp": "2+ Years (Software Engineer)",
        "score": "95% Match",
        "base_score": 95,
        "skills": ["C#", ".NET Core", "ASP.NET Core", "WebAPI", "TypeScript", "SQL Server", "REST APIs", "Docker"],
        "url": "https://in.linkedin.com/jobs/view/4468890940",
        "note": "🔥 Posted Today! Software Engineer (.NET Core 6/8, WebAPI, React/Angular, SQL Server) with 2+ years experience in Bengaluru."
    },
    {
        "id": "synechron-sep17-linkedin",
        "title": ".NET Fullstack Developer (React/Angular)",
        "company": "Synechron",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru East, Karnataka, India",
        "date": "Sep 17, 2026",
        "days_ago": 1,
        "exp": "2-4 Years",
        "score": "95% Match",
        "base_score": 95,
        "skills": ["C#", "ASP.NET Core", "React.js", "TypeScript", "SQL Server", "REST APIs", "Entity Framework", "Git"],
        "url": "https://in.linkedin.com/jobs/view/4467579856",
        "note": "🔥 1d ago! .NET Fullstack Developer for ASP.NET Core, C#, React/Angular, REST APIs, and SQL Server in Bengaluru East."
    }
]

new_ats_jobs = [
    {
        "id": "ge-vernova-workday",
        "title": "Software Engineer (Full Stack .NET & React)",
        "company": "GE Vernova",
        "portal": "freehire.me",
        "portal_badge": "🌐 freehire ATS",
        "portal_color": "#06b6d4",
        "location": "Bengaluru, Karnataka",
        "date": "Sep 16, 2026",
        "days_ago": 2,
        "exp": "2-5 Years",
        "score": "97% Match",
        "base_score": 97,
        "skills": ["C#", ".NET Core", "React.js", "REST APIs", "SQL", "Docker", "Kubernetes", "PostgreSQL"],
        "url": "https://gevernova.wd5.myworkdayjobs.com/Only_Confidential_Executive_Recruiting/job/Bengaluru/Software-Engineer_R5052563-1?utm_source=freehire.me",
        "note": "🔥 2d ago! Direct GE Vernova Workday ATS opening for Full Stack .NET (C#) & React in Bengaluru."
    },
    {
        "id": "cognizant-taleo",
        "title": "Dotnet Full Stack Developer (.NET Core & React/Angular)",
        "company": "Cognizant",
        "portal": "freehire.me",
        "portal_badge": "🌐 freehire ATS",
        "portal_color": "#06b6d4",
        "location": "Bengaluru, Karnataka (Hybrid)",
        "date": "Sep 16, 2026",
        "days_ago": 2,
        "exp": "2-4 Years",
        "score": "94% Match",
        "base_score": 94,
        "skills": [".NET Core", "C#", "Entity Framework", "React.js", "TypeScript", "Azure", "SQL Server", "REST APIs"],
        "url": "https://cognizant.taleo.net/careersection/naukri/jobdetail.ftl?job=00070011022&lang=en&utm_source=freehire.me",
        "note": "🔥 2d ago! Direct Taleo opening: C#, .NET Core, EF, React/Angular, Azure cloud services & SQL Server."
    }
]

import ast

start_idx = content.find("jobs_data = [")
end_marker = "\n]\n\n# Pre-generate prep guides for all roles"
end_idx = content.find(end_marker)

jobs_code = content[start_idx + len("jobs_data = "):end_idx + 2]
raw_jobs = ast.literal_eval(jobs_code)

# Filter out duplicates if new jobs were already added
seen_ids = set()
cleaned_existing = []
for j in raw_jobs:
    if j["id"] in seen_ids:
        continue
    seen_ids.add(j["id"])
    cleaned_existing.append(j)

updated_jobs = []
ats_inserted = False
linkedin_inserted = False

for j in cleaned_existing:
    # Fix any surrogates in existing fields
    for k, v in j.items():
        if isinstance(v, str):
            j[k] = fix_surrogates(v)
        elif isinstance(v, list):
            j[k] = [fix_surrogates(x) if isinstance(x, str) else x for x in v]

    # Recalculate days_ago based on date
    dt = parse_job_date(j["date"])
    days_ago = (today - dt).days
    j["days_ago"] = max(0, days_ago)

    # Clean note if it had old "🔥 Posted Today!" or "🔥 1d ago!" etc.
    if j["days_ago"] >= 4:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|1d ago!|2d ago!|3d ago!)\s*", "", j["note"])

    # Insert ATS jobs before akzonobel-freehire
    if j["id"] == "akzonobel-freehire" and not ats_inserted:
        for new_j in new_ats_jobs:
            if new_j["id"] not in seen_ids:
                updated_jobs.append(new_j)
                seen_ids.add(new_j["id"])
        ats_inserted = True

    # Insert LinkedIn jobs before alegeus-linkedin
    if j["id"] == "alegeus-linkedin" and not linkedin_inserted:
        for new_j in new_linkedin_jobs:
            if new_j["id"] not in seen_ids:
                updated_jobs.append(new_j)
                seen_ids.add(new_j["id"])
        linkedin_inserted = True

    updated_jobs.append(j)

# If not inserted yet (e.g. if akzonobel-freehire was already preceded), make sure all new jobs are present
for new_j in new_ats_jobs + new_linkedin_jobs:
    if new_j["id"] not in [x["id"] for x in updated_jobs]:
        updated_jobs.insert(0, new_j)

print(f"Total jobs count: {len(updated_jobs)}")

# Format as clean Python code using ensure_ascii=False
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
    "ge-vernova-linkedin": "    # --- LINKEDIN VERIFIED POSTINGS (Sep 18, 2026 Live Updates) ---"
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
print("Successfully wrote updated jobs_data to tools/generate_1to3yr_dashboard.py!")

