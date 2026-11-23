#!/usr/bin/env python3
"""
Dynamic Tailored Resume Generator for Roshan Moger
Synthesizes company and job requirements with Roshan's verified profile to produce
a role-tailored, ATS-optimized ModernCV Banking LaTeX resume and compiles it to PDF.
"""

import sys
import os
import re
import json
import subprocess
import shutil
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
CV_DIR = WORKSPACE_DIR / "cv"
CV_DIR.mkdir(exist_ok=True)
DATA_FILE = WORKSPACE_DIR / "data" / "jobs_database.json"

def clean_slug(text):
    return re.sub(r'[^a-zA-Z0-9]+', '_', text.lower()).strip('_')[:30]

def load_jobs():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

def save_jobs(jobs):
    DATA_FILE.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")

def find_job(query, jobs):
    q = query.lower().strip()
    # 1. Exact ID match
    for j in jobs:
        if j.get("id", "").lower() == q:
            return j
    # 2. Company exact/contains match
    for j in jobs:
        if q in j.get("company", "").lower():
            return j
    # 3. Title contains match
    for j in jobs:
        if q in j.get("title", "").lower():
            return j
    return None

def generate_tailored_tex(job):
    company = job.get("company", "Company")
    title = job.get("title", "Full Stack Developer")
    skills = job.get("skills", [])
    skills_text = " ".join(skills).lower() + " " + title.lower()

    is_dotnet_focus = any(k in skills_text for k in [".net", "dotnet", "c#", "asp.net"])
    is_frontend_focus = any(k in skills_text for k in ["frontend", "react", "next.js", "ui"]) and not is_dotnet_focus
    is_cloud_focus = any(k in skills_text for k in ["aws", "cloud", "docker", "kubernetes"])

    # 1. Tailored Profile Statement
    if is_dotnet_focus:
        profile_stmt = (
            f"Full Stack Developer with 2.5+ years of enterprise engineering experience specializing in "
            f"ASP.NET Core, C\\#, Web API, and React.js. Experienced in Model Context Protocol (MCP) and integrating LLMs "
            f"(Google Gemini via AWS Bedrock). Proven track record at ExcelSoft Technologies architecting high-throughput "
            f"RESTful services, integrating Redis caching layers, and deploying containerized microservices across AWS with Docker and Kubernetes. "
            f"Dedicated to writing clean, maintainable code adhering to SOLID principles and enterprise design patterns for {company}."
        )
    elif is_frontend_focus:
        profile_stmt = (
            f"Frontend & Full Stack Software Engineer with 2.5+ years of production experience crafting high-performance, "
            f"responsive web applications using React.js, TypeScript, Next.js, and Redux. Experienced at ExcelSoft "
            f"Technologies engineering modular UI component libraries, integrating AI chat assistants with Gemini via AWS Bedrock, "
            f"and Core Web Vitals optimization. Passionate about delivering seamless, user-centric experiences for {company}."
        )
    else:
        profile_stmt = (
            f"Full Stack Developer with 2.5+ years of hands-on experience developing end-to-end web applications "
            f"using React.js, TypeScript, ASP.NET Core, C\\#, and cloud microservices. Experienced in Model Context Protocol (MCP) "
            f"and integrating LLMs (Google Gemini via AWS Bedrock). Demonstrated success at ExcelSoft Technologies implementing "
            f"high-concurrency caching with Redis, JWT auth, and containerized AWS/Kubernetes deployments for {company}."
        )

    # 2. Tailored Core Competencies
    if is_dotnet_focus:
        comp_1 = "\\item \\textbf{Backend & Microservices}: ASP.NET Core, C\\#, Web API, Entity Framework Core, Dependency Injection, RESTful APIs, Node.js, Express.js."
        comp_2 = "\\item \\textbf{Frontend Development}: React.js, TypeScript, JavaScript, Redux, Tailwind CSS, HTML5, CSS3, Responsive UI."
        comp_3 = "\\item \\textbf{AI & LLM Integration}: Model Context Protocol (MCP), AWS Bedrock, Google Gemini."
        comp_4 = "\\item \\textbf{Cloud & DevOps}: AWS (EC2, IAM, S3, RDS, Lambda, CloudWatch), Docker, Kubernetes, CI/CD Pipelines, Git, GitHub Actions."
        comp_5 = "\\item \\textbf{Databases & Caching}: Redis Distributed Caching, PostgreSQL, Microsoft SQL Server, MongoDB."
    elif is_frontend_focus:
        comp_1 = "\\item \\textbf{Frontend Engineering}: React.js, TypeScript, JavaScript (ES6+), Next.js, Redux, Context API, Tailwind CSS, HTML5/CSS3."
        comp_2 = "\\item \\textbf{Backend & APIs}: ASP.NET Core, C\\#, Node.js, Express.js, RESTful APIs, WebSockets, JWT Authentication."
        comp_3 = "\\item \\textbf{AI & LLM Integration}: Model Context Protocol (MCP), AWS Bedrock, Google Gemini."
        comp_4 = "\\item \\textbf{Cloud & Tooling}: AWS (EC2, S3, CloudFront), Docker, Kubernetes, Git, Postman, VS Code."
        comp_5 = "\\item \\textbf{Architecture & Methodologies}: Component-Driven Development, Modular SPAs, Agile/Scrum, SOLID Principles, Peer Reviews."
    else:
        comp_1 = "\\item \\textbf{Frontend Engineering}: React.js, TypeScript, JavaScript, Redux, React Router, Tailwind CSS, Bootstrap, HTML5, CSS3."
        comp_2 = "\\item \\textbf{Backend & API Design}: ASP.NET Core, C\\#, Node.js, Express.js, REST APIs, WebSockets, JWT Authentication."
        comp_3 = "\\item \\textbf{AI & LLM Integration}: Model Context Protocol (MCP), AWS Bedrock, Google Gemini."
        comp_4 = "\\item \\textbf{Cloud & DevOps}: AWS (EC2, IAM, S3, RDS, Lambda, CloudWatch), Docker, Kubernetes, GitHub Actions, Git."
        comp_5 = "\\item \\textbf{Data & Caching}: Redis Distributed Caching, PostgreSQL, MongoDB, Microsoft SQL Server."

    tex_content = f"""\\documentclass[11pt,a4paper,sans]{{moderncv}}
\\moderncvstyle{{banking}}
\\moderncvcolor{{blue}}

\\renewcommand*{{\\namefont}}{{\\fontsize{{34}}{{36}}\\bfseries\\upshape}}
\\colorlet{{firstnamecolor}}{{color1}}
\\colorlet{{lastnamecolor}}{{color1}}
\\colorlet{{namecolor}}{{color1}}
\\renewcommand*{{\\sectionstyle}}[1]{{{{\\sectionfont\\color{{color1}}#1}}}}

\\usepackage[utf8]{{inputenc}}
\\AtEndPreamble{{\\hypersetup{{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=blue,
    pdftitle={{Roshan Moger - Tailored CV for {company}}},
    pdfpagemode=UseNone,
}}}}
\\usepackage[scale=0.80]{{geometry}}
\\usepackage{{import}}
\\usepackage{{needspace}}

% Personal data
\\name{{Roshan}}{{Moger}}
\\address{{Mysore, Karnataka, India}}{{}}{{}}
\\phone[mobile]{{+91-8970035508}}
\\email{{roshanmoger502@gmail.com}}
\\extrainfo{{\\href{{https://linkedin.com/in/roshan-moger}}{{LinkedIn}}, \\href{{https://github.com/Roshan-moger}}{{GitHub}}, \\href{{https://roshan-devhub.netlify.app}}{{roshan-devhub.netlify.app}}}}

\\begin{{document}}

\\makecvtitle

% ============================================================
%     PROFILE STATEMENT
% ============================================================

\\vspace{{6pt}}
\\small{{{profile_stmt}}}

% ============================================================
%     CORE COMPETENCIES
% ============================================================

\\section{{Technical Skills}}
\\vspace{{1pt}}
\\begin{{itemize}}
{comp_1}
{comp_2}
{comp_3}
{comp_4}
{comp_5}
\\end{{itemize}}

% ============================================================
%     PROFESSIONAL EXPERIENCE
% ============================================================

\\section{{Professional Experience}}
\\vspace{{3pt}}
\\begin{{itemize}}

% --- ExcelSoft Technologies ---
\\item \\textbf{{Associate Software Engineer}} \\hfill \\textbf{{May 2024 -- Present}} \\\\
\\textit{{ExcelSoft Technologies}} \\hfill \\textit{{Mysore, Karnataka, India}}
\\begin{{itemize}}
  \\item Developed end-to-end features across \\textbf{{React.js / TypeScript}} single-page applications and \\textbf{{ASP.NET Core / C\\#}} REST APIs for enterprise EdTech and compliance platforms.
  \\item Designed and built a \\textbf{{Model Context Protocol (MCP) server}} using \\textbf{{.NET}} to expose SaaS data/workflows to AI systems, and developed an in-product chatbot integrating \\textbf{{Google Gemini (via AWS Bedrock)}} alongside the company's private AI model.
  \\item Contributed to \\textbf{{Saras Standard Platform}}, \\textbf{{SVKM Platform}}, and \\textbf{{OwlBot}}, supporting assessment creation, scheduling, secure test delivery, reporting, and copyright-compliance reporting.
  \\item Implemented secure \\textbf{{JWT authentication}} with refresh tokens, session persistence, protected routes, and role-based access control (RBAC).
  \\item Built reusable React components, custom hooks, and higher-order components for common UI, authorization, and API-integration requirements.
  \\item Implemented a multi-tier \\textbf{{Redis caching layer}} to reduce unnecessary database queries in high-traffic assessment modules.
  \\item Deployed and managed containerized microservices using \\textbf{{Docker}}, \\textbf{{Kubernetes}}, and \\textbf{{AWS}} services (EC2, IAM, S3, RDS, Lambda, CloudWatch).
\\end{{itemize}}

\\end{{itemize}}

% ============================================================
%     KEY PROJECTS
% ============================================================

\\section{{Selected Projects}}
\\vspace{{3pt}}
\\begin{{itemize}}

\\item \\textbf{{Real-Time Expense Tracker Platform}} \\hfill \\textit{{React.js, TypeScript, Redux, Node.js, Express, MongoDB}}
\\begin{{itemize}}
  \\item Built a full-stack personal finance platform with \\textbf{{JWT authentication}}, dynamic categorization, and interactive data visualization charts.
  \\item Designed optimized query patterns for expense and user-data operations; containerized services using \\textbf{{Docker Compose}}.
\\end{{itemize}}

\\vspace{{2pt}}

\\item \\textbf{{Event Management System}} \\hfill \\textit{{React.js, TypeScript, WebSockets, REST APIs}}
\\begin{{itemize}}
  \\item Designed a multi-role web platform (Admin, Organizer, Customer) featuring event creation, ticket booking, and QR-based check-in over \\textbf{{WebSockets}}.
\\end{{itemize}}

\\end{{itemize}}

% ============================================================
%     EDUCATION
% ============================================================

\\section{{Education}}
\\vspace{{3pt}}
\\begin{{itemize}}

\\item \\textbf{{Bachelor of Engineering (B.E.) in Electrical \\& Electronics Engineering}} \\hfill \\textbf{{2019 -- 2023}} \\\\
\\textit{{NIE Institute of Technology, Mysore}} \\hfill \\textit{{GPA: 7.8 / 10.0}}
\\begin{{itemize}}
  \\item Core foundation in software engineering, data structures, and computer programming.
\\end{{itemize}}

\\end{{itemize}}

% ============================================================
%     CERTIFICATIONS
% ============================================================

\\section{{Certifications}}
\\vspace{{3pt}}
\\begin{{itemize}}

\\item \\textbf{{Java Full-Stack Development Certification}} \\hfill \\textbf{{Aug 2023 -- Apr 2024}} \\\\
\\textit{{Kodnest Technologies Pvt. Ltd.}} \\hfill \\textit{{Bengaluru, Karnataka, India}}
\\begin{{itemize}}
  \\item Comprehensive training in full-stack application development, database design, and RESTful service engineering.
\\end{{itemize}}

\\end{{itemize}}

\\end{{document}}
"""
    return tex_content

def compile_pdf(tex_path):
    cmd = ["lualatex", "-interaction=nonstopmode", tex_path.name]
    try:
        print(f"Compiling LaTeX to PDF: {tex_path.name}...")
        res = subprocess.run(cmd, cwd=str(CV_DIR), capture_output=True, text=True, timeout=60)
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_path.exists():
            print(f"✅ Successfully compiled: {pdf_path.name} ({pdf_path.stat().st_size} bytes)")
            return pdf_path
        else:
            print(f"Compilation warning: PDF not produced. Log tail:\n{res.stdout[-300:]}", file=sys.stderr)
    except Exception as e:
        print(f"Error compiling LaTeX: {e}", file=sys.stderr)
    return None

def tailor_for_company(query):
    jobs = load_jobs()
    job = find_job(query, jobs)
    if not job:
        print(f"❌ Job matching '{query}' not found in database. Using query directly as company name.")
        job = {
            "id": f"custom-{clean_slug(query)}",
            "company": query,
            "title": "Full Stack Developer",
            "skills": [".NET Core", "C#", "React.js", "TypeScript", "SQL Server", "REST APIs", "AWS"],
            "portal": "Direct"
        }

    company_slug = clean_slug(job["company"])
    role_slug = clean_slug(job["title"])
    tex_filename = f"main_{company_slug}_{role_slug}.tex"
    tex_path = CV_DIR / tex_filename

    tex_code = generate_tailored_tex(job)
    tex_path.write_text(tex_code, encoding="utf-8")
    print(f"📄 Generated tailored TeX source: {tex_path}")

    pdf_path = compile_pdf(tex_path)
    if pdf_path and pdf_path.exists():
        relative_link = f"/cv/{pdf_path.name}"
        job["cv_link"] = relative_link
        # Update in database if exists
        updated = False
        for i, existing in enumerate(jobs):
            if existing.get("id") == job.get("id"):
                jobs[i]["cv_link"] = relative_link
                updated = True
                break
        if not updated:
            jobs.append(job)
        save_jobs(jobs)

        # Trigger dashboard generator to update HTML
        gen_script = WORKSPACE_DIR / "tools" / "generate_1to3yr_dashboard.py"
        subprocess.run([sys.executable, str(gen_script)], cwd=str(WORKSPACE_DIR), capture_output=True)
        print(f"🎉 Tailored CV ready and linked on dashboard: {relative_link}")
        return str(pdf_path)
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/tailor_resume.py <company_name_or_job_id>")
        sys.exit(1)
    target = sys.argv[1]
    tailor_for_company(target)
