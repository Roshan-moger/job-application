import re
import json
import datetime
from pathlib import Path
import ast

dashboard_path = Path("tools/generate_1to3yr_dashboard.py")
content = dashboard_path.read_text(encoding="utf-8")

today = datetime.date(2026, 9, 21)

def fix_surrogates(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("utf-16", "surrogatepass").decode("utf-16")
    except Exception:
        return s

def parse_job_date(date_str):
    return datetime.datetime.strptime(date_str, "%b %d, %Y").date()

new_sep21_jobs = [
    {
        "id": "tcs-react-dotnet-linkedin",
        "title": ".Net Full Stack Developer with React.js (Associate)",
        "company": "Tata Consultancy Services",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru South, Karnataka, India",
        "date": "Sep 21, 2026",
        "days_ago": 0,
        "exp": "1-3 Years (Associate)",
        "score": "97% Match ★ TOP FIT",
        "base_score": 97,
        "skills": [".NET Core", "C#", "React.js", "Web API", "Entity Framework", "SQL Server", "Docker", "Kubernetes", "Cloud"],
        "url": "https://in.linkedin.com/jobs/view/net-fsd-with-react-js-at-tata-consultancy-services-4468712549",
        "note": "🔥 Posted Today! 97% Match! Associate full-stack vacancy: .NET Core, C#, React.js, Web API, MSSQL, EF, Docker & Kubernetes in Bengaluru."
    },
    {
        "id": "headout-web-engineer-linkedin",
        "title": "Web Software Engineer (Frontend / Full Stack)",
        "company": "Headout",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 21, 2026",
        "days_ago": 0,
        "exp": "1+ Years (Associate)",
        "score": "96% Match",
        "base_score": 96,
        "skills": ["React.js", "TypeScript", "JavaScript", "HTML/CSS", "Git", "REST APIs", "Web Performance"],
        "url": "https://in.linkedin.com/jobs/view/web-software-engineer-at-headout-4467603900",
        "note": "🔥 Posted Today! High-growth consumer travel platform: build end-to-end features with React, TypeScript, and high-performance web systems."
    },
    {
        "id": "tcs-react-linkedin",
        "title": "Reactjs Developer",
        "company": "Tata Consultancy Services",
        "portal": "LinkedIn",
        "portal_badge": "🔷 LinkedIn",
        "portal_color": "#0ea5e9",
        "location": "Bengaluru, Karnataka, India",
        "date": "Sep 20, 2026",
        "days_ago": 1,
        "exp": "1-3 Years",
        "score": "95% Match",
        "base_score": 95,
        "skills": ["React.js", "TypeScript", "JavaScript", "Redux", "REST APIs", "Git"],
        "url": "https://in.linkedin.com/jobs/view/reactjs-developer-at-tata-consultancy-services-4469812646",
        "note": "🔥 1d ago! Modern enterprise UI engineering: React.js components, Redux state management, and RESTful service integration."
    }
]

new_ats_sep21_jobs = [
    {
        "id": "mufg-dotnet-ats",
        "title": ".NET Developer (1-3 Years Experience)",
        "company": "MUFG Pension & Market Services",
        "portal": "freehire.me",
        "portal_badge": "🌐 freehire ATS",
        "portal_color": "#06b6d4",
        "location": "Bengaluru / India",
        "date": "Sep 21, 2026",
        "days_ago": 0,
        "exp": "1-3 Years",
        "score": "97% Match ★ TOP FIT",
        "base_score": 97,
        "skills": [".NET Core", "C#", "ASP.NET MVC", "SQL Server", "RESTful APIs", "SOLID", "Azure", "Git", "Angular/React"],
        "url": "https://hcmn.fa.ap1.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/16021?utm_source=freehire.me",
        "note": "🔥 Posted Today! Top tier global financial institution explicitly requiring 1-3 years C#, .NET, ASP.NET MVC, SQL Server & REST APIs."
    },
    {
        "id": "jobgether-dotnet-ats",
        "title": ".Net Software Developer (18-22 LPA)",
        "company": "Jobgether",
        "portal": "freehire.me",
        "portal_badge": "🌐 freehire ATS",
        "portal_color": "#06b6d4",
        "location": "Remote India / Bengaluru",
        "date": "Sep 21, 2026",
        "days_ago": 0,
        "exp": "2-4 Years (18-22 LPA)",
        "score": "96% Match",
        "base_score": 96,
        "skills": ["C#", ".NET Core", "ASP.NET Core", "RESTful APIs", "SQL Server", "React", "Angular", "System Design"],
        "url": "https://jobs.lever.co/jobgether/ece0922a-9ee2-4609-a3bb-8b0914bf7475?utm_source=freehire.me",
        "note": "🔥 Posted Today! Fully remote product engineering opportunity: scalable .NET Core backend, REST APIs, SQL Server, and React."
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
ats_inserted = False
linkedin_inserted = False

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
    elif j["days_ago"] == 1:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|2d ago!|3d ago!)\s*", "🔥 1d ago! ", j["note"])
    elif j["days_ago"] == 2:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|1d ago!|3d ago!)\s*", "🔥 2d ago! ", j["note"])
    elif j["days_ago"] == 3:
        j["note"] = re.sub(r"^🔥\s*(Posted Today!|1d ago!|2d ago!)\s*", "🔥 3d ago! ", j["note"])

    # Insert ATS jobs before ge-vernova-workday
    if j["id"] == "ge-vernova-workday" and not ats_inserted:
        for new_j in new_ats_sep21_jobs:
            if new_j["id"] not in seen_ids:
                updated_jobs.append(new_j)
                seen_ids.add(new_j["id"])
        ats_inserted = True

    # Insert LinkedIn jobs before ibm-cloud-fullstack-linkedin
    if j["id"] == "ibm-cloud-fullstack-linkedin" and not linkedin_inserted:
        for new_j in new_sep21_jobs:
            if new_j["id"] not in seen_ids:
                updated_jobs.append(new_j)
                seen_ids.add(new_j["id"])
        linkedin_inserted = True

    updated_jobs.append(j)

# Fallback: make sure all new jobs are included
for new_j in new_ats_sep21_jobs + new_sep21_jobs:
    if new_j["id"] not in [x["id"] for x in updated_jobs]:
        updated_jobs.insert(0, new_j)

print(f"Total jobs count for Sep 21: {len(updated_jobs)}")

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
    "mufg-dotnet-ats": "    # --- FREEHIRE.ME & GLOBAL ATS PLATFORMS (Fresh 3-Day & Enterprise) ---",
    "tcs-react-dotnet-linkedin": "    # --- LINKEDIN VERIFIED POSTINGS (Sep 21, 2026 Live Updates) ---"
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
print("Successfully wrote updated jobs_data for Sep 21, 2026!")

