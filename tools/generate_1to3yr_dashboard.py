#!/usr/bin/env python3
"""
Multi-Portal Dashboard & Dynamic Interview Preparation Generator for Roshan Moger
Searches across all major job portals: Naukri.com, Indeed India, Instahyre, Wellfound (AngelList),
Direct Company Career Sites, freehire.me (ATS), and LinkedIn.
Includes Live Resume Match Recalculation Engine, Interactive Skill Toggles,
Dynamic Interview Preparation Modal for all companies, and Any-Company Generator.
"""

import sys
import json
import datetime
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

tools_dir = Path(__file__).resolve().parent
workspace_dir = tools_dir.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from interview_prep_engine import generate_dynamic_prep, format_as_markdown, CANDIDATE_PROFILE, DOMAIN_INTEL
from roadmap_engine import ROADMAP_PHASES, generate_roadmap_markdown

# --- DYNAMIC DATABASE LOADER & REAL-TIME RECALCULATION ENGINE ---
db_path = workspace_dir / "data" / "jobs_database.json"
if db_path.exists():
    try:
        jobs_data = json.loads(db_path.read_text(encoding="utf-8"))
    except Exception as err:
        print(f"Error loading jobs database: {err}", file=sys.stderr)
        jobs_data = []
else:
    jobs_data = []

today = datetime.date.today()

def parse_job_date(raw_date_str):
    """Dynamically parse date and compute days_ago relative to today."""
    if not raw_date_str:
        return today, 0, today.strftime("%b %d, %Y")
    try:
        clean = raw_date_str.split("T")[0]
        parsed = datetime.datetime.strptime(clean, "%Y-%m-%d").date()
        days_ago = max(0, (today - parsed).days)
        return parsed, days_ago, parsed.strftime("%b %d, %Y")
    except Exception:
        pass
    try:
        parsed = datetime.datetime.strptime(raw_date_str, "%b %d, %Y").date()
        days_ago = max(0, (today - parsed).days)
        return parsed, days_ago, parsed.strftime("%b %d, %Y")
    except Exception:
        pass
    return today, 0, today.strftime("%b %d, %Y")

# Recalculate dynamic days_ago and formatted date for every vacancy
for j in jobs_data:
    p_date, days_ago, formatted_date = parse_job_date(j.get("date"))
    j["days_ago"] = days_ago
    j["date"] = formatted_date

# Sort jobs: Newest postings first (0 days ago, 1d ago, etc.), then highest match score
jobs_data.sort(key=lambda j: (j.get("days_ago", 99), -j.get("base_score", 0)))

# Pre-generate prep guides for all roles
prep_database = {}
reports_dir = workspace_dir / "reports" / "interview_prep"
reports_dir.mkdir(parents=True, exist_ok=True)

for j in jobs_data:
    prep = generate_dynamic_prep(j["company"], j["title"], j["skills"], j["location"], j["exp"], j["url"])
    prep_database[j["id"]] = prep
    clean_company = "".join(c if c.isalnum() else "_" for c in j["company"]).strip("_")
    md_file = reports_dir / f"{clean_company}_prep.md"
    if not md_file.exists():
        md_file.write_text(format_as_markdown(prep), encoding="utf-8")

# Build Job Cards HTML
jobs_html = ""
for idx, j in enumerate(jobs_data):
    days_ago = j.get("days_ago", 99)
    if days_ago == 0:
        freshness_badge = f'<span class="badge-fresh-pill today">🔥 Posted Today ({today.strftime("%b %d")})</span>'
    elif days_ago == 1:
        freshness_badge = f'<span class="badge-fresh-pill">🔥 1d ago ({(today - datetime.timedelta(days=1)).strftime("%b %d")})</span>'
    elif days_ago == 2:
        freshness_badge = f'<span class="badge-fresh-pill">🔥 2d ago ({(today - datetime.timedelta(days=2)).strftime("%b %d")})</span>'
    elif days_ago == 3:
        freshness_badge = f'<span class="badge-fresh-pill">🔥 3d ago ({(today - datetime.timedelta(days=3)).strftime("%b %d")})</span>'
    else:
        freshness_badge = f'<span class="badge-older-pill">📅 {j["date"]}</span>'

    # Compute Country / Location Badge and Category (Dubai & India ONLY)
    loc_str = (j.get("location") or "").lower()
    if any(k in loc_str for k in ["dubai", "uae", "emirates", "abu dhabi", "sharjah"]):
        loc_category = "dubai"
        loc_badge = '<span class="loc-pill loc-uae">🇦🇪 Dubai, UAE</span>'
    else:
        loc_category = "india"
        loc_badge = '<span class="loc-pill loc-in">🇮🇳 India</span>'

    pills = "".join(f'<span class="pill" onclick="filterBySkill(\'{s}\')" title="Click to filter by {s}">{s}</span>' for s in j["skills"])
    custom_buttons = ""
    if "cv_link" in j and j["cv_link"]:
        custom_buttons += f'''
          <a href="{j['cv_link']}" target="_blank" class="btn btn-cv">📄 View Tailored CV (PDF) ↗</a>
        '''
    else:
        custom_buttons += f'''
          <button id="btn-tailor-{j['id']}" onclick="generateTailoredResumeOnSpot('{j['id']}', this)" class="btn btn-tailor">✨ Tailor Resume (On-Spot)</button>
        '''
    custom_buttons += f'''
      <button onclick="openPrepModal('{j['id']}')" class="btn btn-prep">🎯 Prepare Interview</button>
      <a href="{j['url']}" target="_blank" class="btn btn-link" style="border-left: 2px solid {j['portal_color']};">🚀 View & Apply ({j['portal']}) ↗</a>
      <button id="btn-apply-{j['id']}" onclick="toggleApplyJob('{j['id']}')" class="btn btn-apply-track">✅ Mark as Applied</button>
      <button onclick="deleteJobRole('{j['id']}', event)" class="btn btn-delete" title="Delete this role">🗑️ Delete</button>
    '''

    border_style = 'style="border: 2px solid #10b981; background: #132238;"' if 'cv_link' in j else ''
    tag_style = 'style="background: rgba(16, 185, 129, 0.3); color: #34d399; font-weight: 700;"' if 'cv_link' in j else ''

    jobs_html += f"""
    <div class="job-item" {border_style} data-id="{j['id']}" data-portal="{j['portal']}" data-location-cat="{loc_category}" data-base="{j['base_score']}" data-days="{days_ago}" data-exp="{j['exp']}">
      <div class="job-top">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
            <span class="portal-badge" style="background: {j['portal_color']}22; color: {j['portal_color']}; border-color: {j['portal_color']}55;">
              {j['portal_badge']}
            </span>
            {loc_badge}
            {freshness_badge}
            <span style="font-size: 13px; color: #a78bfa; font-weight: 600;">{j["exp"]}</span>
          </div>
          <div class="role-title">{j["title"]}</div>
          <div class="company-name">{j["company"]} &bull; <span style="color:#94a3b8; font-weight: normal;">{j["location"]}</span></div>
        </div>
        <div class="match-tag" {tag_style} id="tag-{j['id']}">{j["score"]}</div>
      </div>
      <div class="job-meta-row">
        <span>📅 Posted: <strong>{j["date"]}</strong></span>
        <span>🌐 Portal: <strong>{j['portal']}</strong></span>
        <span>📍 <strong>{j['location']}</strong></span>
      </div>
      <div class="pill-group" id="pills-{j['id']}">{pills}</div>
      <div class="job-note-bar">
        <span class="note-icon">💡</span>
        <span class="note-text">{j["note"]}</span>
      </div>
      <div class="job-button-bar">
        {custom_buttons}
      </div>
    </div>
    """

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Job Search - All-Portals Vacancy & Dynamic Interview Suite</title>
  <!-- PDF.js client-side resume PDF parser -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
  <script>
    if (window.pdfjsLib) {{
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    }}
  </script>
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f2937;
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --accent: #2563eb;
      --accent-light: #3b82f6;
      --success: #10b981;
      --warning: #f59e0b;
      --purple: #8b5cf6;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      padding: 24px;
      line-height: 1.5;
    }}
    .container {{ max-width: 1360px; margin: 0 auto; }}
    
    header {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }}
    .header-top {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
    h1 {{ font-size: 28px; font-weight: 800; letter-spacing: -0.5px; color: #fff; }}
    .subtitle {{ font-size: 15px; color: #94a3b8; margin-top: 6px; }}
    
    .status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
    }}
    .pulse {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    .meta-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 13px;
      color: #cbd5e1;
    }}
    .meta-tag {{
      background: rgba(255, 255, 255, 0.05);
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .meta-tag a {{ color: #38bdf8; text-decoration: none; }}
    .meta-tag a:hover {{ text-decoration: underline; }}

    /* Cross-Portal Launcher Bar */
    .portal-launcher-bar {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .launcher-title {{
      font-size: 13px;
      font-weight: 700;
      color: #cbd5e1;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .launcher-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .launcher-link {{
      text-decoration: none;
      font-size: 12.5px;
      font-weight: 600;
      padding: 7px 14px;
      border-radius: 8px;
      border: 1px solid #334155;
      background: #1e293b;
      color: #e2e8f0;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}
    .launcher-link:hover {{
      transform: translateY(-2px);
      filter: brightness(1.2);
    }}

    /* Recalculator Banner Card */
    .recalc-card {{
      background: linear-gradient(135deg, #131d35 0%, #0f172a 100%);
      border: 2px solid #3b82f6;
      border-radius: 14px;
      padding: 20px 24px;
      margin-bottom: 24px;
      box-shadow: 0 10px 30px -5px rgba(59, 130, 246, 0.2);
    }}
    .recalc-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .recalc-title {{
      font-size: 17px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn-refresh {{
      background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
      color: #fff;
      padding: 10px 22px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid #60a5fa;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
      transition: all 0.2s ease;
    }}
    .btn-refresh:hover {{
      filter: brightness(1.2);
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(37, 99, 235, 0.6);
    }}
    .refresh-icon {{
      display: inline-block;
      transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .spinning {{
      transform: rotate(360deg);
    }}

    .btn-upload-resume {{
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #fff;
      padding: 10px 18px;
      border-radius: 10px;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid #34d399;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
      transition: all 0.2s ease;
      white-space: nowrap;
    }}
    .btn-upload-resume:hover {{
      filter: brightness(1.2);
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(16, 185, 129, 0.5);
    }}
    .upload-dropzone {{
      border: 2px dashed #3b82f6;
      border-radius: 12px;
      padding: 28px 20px;
      text-align: center;
      background: rgba(59, 130, 246, 0.06);
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .upload-dropzone:hover, .upload-dropzone.dragover {{
      background: rgba(59, 130, 246, 0.16);
      border-color: #60a5fa;
      transform: scale(1.01);
    }}
    .active-resume-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .active-resume-badge.default {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .active-resume-badge.custom {{
      background: rgba(59, 130, 246, 0.2);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.4);
    }}
    .btn-add-job {{
      background: rgba(139, 92, 246, 0.15);
      border: 1px solid #8b5cf6;
      color: #c4b5fd;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
      white-space: nowrap;
    }}
    .btn-add-job:hover {{
      background: #8b5cf6;
      color: #fff;
      transform: translateY(-1px);
    }}

    .skill-toggle-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 13px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      white-space: nowrap;
      border: 1px solid transparent;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }}
    .skill-toggle-pill.active {{
      background: rgba(16, 185, 129, 0.16);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.45);
      box-shadow: 0 2px 8px rgba(16, 185, 129, 0.18);
    }}
    .skill-toggle-pill.active:hover {{
      background: rgba(16, 185, 129, 0.28);
      border-color: #34d399;
      transform: translateY(-1px);
    }}
    .skill-toggle-pill.inactive {{
      background: rgba(15, 23, 42, 0.7);
      color: #64748b;
      border: 1px dashed #334155;
      opacity: 0.75;
    }}
    .skill-toggle-pill.inactive:hover {{
      background: #1e293b;
      color: #94a3b8;
      border-color: #475569;
      opacity: 1;
      transform: translateY(-1px);
    }}
    .pill-icon {{
      font-size: 11px;
      font-weight: 800;
    }}
    .pill-del {{
      font-size: 11px;
      margin-left: 4px;
      color: #ef4444;
      opacity: 0.7;
      padding: 0 4px;
      border-radius: 4px;
    }}
    .pill-del:hover {{
      opacity: 1;
      background: rgba(239, 68, 68, 0.25);
    }}

    .pill-control-btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid #334155;
      color: #94a3b8;
      padding: 3px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
    }}
    .pill-control-btn:hover {{
      background: #1e293b;
      color: #38bdf8;
      border-color: #38bdf8;
    }}
    .pill-control-btn.reset:hover {{
      color: #f59e0b;
      border-color: #f59e0b;
    }}

    /* Location Filter Bar */
    .location-filter-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}
    .location-filter-btn {{
      background: #1e293b;
      color: #94a3b8;
      border: 1px solid #334155;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .location-filter-btn:hover {{
      color: #fff;
      background: #334155;
    }}
    .location-filter-btn.active {{
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #fff;
      border-color: #38bdf8;
      box-shadow: 0 2px 8px rgba(56, 189, 248, 0.25);
    }}

    .loc-pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.3px;
    }}
    .loc-uae {{
      background: rgba(245, 158, 11, 0.18);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.4);
    }}
    .loc-jp {{
      background: rgba(239, 68, 68, 0.18);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }}
    .loc-kr {{
      background: rgba(59, 130, 246, 0.18);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.4);
    }}
    .loc-in {{
      background: rgba(16, 185, 129, 0.18);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
    }}
    .loc-remote {{
      background: rgba(168, 85, 247, 0.18);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.4);
    }}

    /* Portal Filter Bar */
    .portal-filter-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 18px;
    }}
    .portal-filter-btn {{
      background: #1e293b;
      color: #94a3b8;
      border: 1px solid #334155;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .portal-filter-btn:hover {{
      color: #fff;
      background: #334155;
    }}
    .portal-filter-btn.active {{
      background: #2563eb;
      color: #fff;
      border-color: #60a5fa;
    }}

    .portal-badge {{
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      border: 1px solid transparent;
      letter-spacing: 0.3px;
    }}

    .stats-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
    }}
    .stat-card::after {{
      content: "";
      position: absolute;
      top: 0; left: 0; height: 4px; width: 100%;
    }}
    .c-blue::after {{ background: #3b82f6; }}
    .c-green::after {{ background: #10b981; }}
    .c-purple::after {{ background: #8b5cf6; }}
    .c-amber::after {{ background: #f59e0b; }}
    
    .stat-num {{ font-size: 32px; font-weight: 800; color: #fff; }}
    .stat-desc {{ font-size: 13px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-top: 4px; }}

    .layout-grid {{
      display: grid;
      grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
      gap: 24px;
    }}
    @media (max-width: 1040px) {{
      .layout-grid {{ grid-template-columns: minmax(0, 1fr); }}
    }}

    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .card-title {{
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .search-input {{
      width: 100%;
      background: #0f172a;
      border: 1px solid #334155;
      padding: 12px 16px;
      border-radius: 10px;
      color: #fff;
      font-size: 14px;
      margin-bottom: 18px;
    }}
    .search-input:focus {{ outline: none; border-color: var(--accent-light); }}

    .job-list {{ display: flex; flex-direction: column; gap: 14px; }}
    .job-item {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 18px 20px;
      transition: all 0.3s ease;
    }}
    .job-item:hover {{
      border-color: var(--accent-light);
      transform: translateY(-2px);
    }}
    .job-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }}
    .role-title {{ font-size: 17px; font-weight: 700; color: #fff; }}
    .company-name {{ font-size: 14px; color: #38bdf8; font-weight: 600; margin-top: 2px; }}
    .match-tag {{
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
      transition: all 0.3s ease;
    }}
    .job-meta-row {{
      display: flex;
      gap: 14px;
      font-size: 12px;
      color: #94a3b8;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}
    .pill-group {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
    .pill {{
      background: #0f172a;
      color: #cbd5e1;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 500;
      border: 1px solid #334155;
      transition: all 0.2s;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}
    .pill:hover {{
      border-color: #38bdf8;
      color: #38bdf8;
      transform: translateY(-1px);
    }}
    .pill.matched {{
      background: rgba(16, 185, 129, 0.18);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.4);
      font-weight: 600;
    }}
    .pill.matched:hover {{
      background: rgba(16, 185, 129, 0.28);
      border-color: #34d399;
    }}

    .job-note-bar {{
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.2);
      border-radius: 8px;
      padding: 9px 13px;
      margin-bottom: 12px;
      font-size: 12.5px;
      color: #6ee7b7;
      display: flex;
      align-items: center;
      gap: 8px;
      line-height: 1.4;
      word-break: break-word;
    }}
    .job-button-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .btn {{
      background: #2563eb;
      color: #ffffff;
      text-decoration: none;
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s;
      border: none;
      cursor: pointer;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .btn:hover {{ filter: brightness(1.15); transform: translateY(-1px); }}
    .btn-prep {{
      background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }}
    .btn-link {{ background: #334155; color: #cbd5e1; }}
    .btn-cv {{ background: #10b981; color: #fff; font-weight: 700; text-decoration: none; }}
    .btn-tailor {{
      background: linear-gradient(135deg, #059669 0%, #10b981 100%);
      color: #ffffff;
      font-weight: 700;
      border: 1px solid rgba(52, 211, 153, 0.4);
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }}
    .btn-tailor:hover {{
      background: linear-gradient(135deg, #047857 0%, #059669 100%);
      box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
    }}
    .btn-apply-track {{
      background: #1e293b;
      border: 1px solid #10b981;
      color: #34d399;
      font-size: 12px;
      font-weight: 700;
      padding: 7px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .btn-apply-track:hover {{
      background: #10b981;
      color: #fff;
    }}
    .btn-applied-undo {{
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      color: #f87171;
      font-size: 12px;
      font-weight: 700;
      padding: 7px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .btn-applied-undo:hover {{
      background: #ef4444;
      color: #fff;
    }}
    .btn-delete {{
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.35);
      color: #f87171;
      font-size: 12px;
      font-weight: 700;
      padding: 7px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .btn-delete:hover {{
      background: #ef4444;
      color: #fff;
      border-color: #ef4444;
      transform: translateY(-1px);
    }}

    /* View Mode Tabs (Fresh, All, Applied) */
    .view-mode-tabs {{
      display: flex;
      gap: 8px;
      margin-bottom: 14px;
      background: #0f172a;
      padding: 6px;
      border-radius: 12px;
      border: 1px solid #1e293b;
      overflow-x: auto;
    }}
    .view-tab-btn {{
      background: transparent;
      border: 1px solid transparent;
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 13.5px;
      font-weight: 700;
      color: #94a3b8;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
      white-space: nowrap;
    }}
    .view-tab-btn:hover {{
      color: #fff;
      background: rgba(255, 255, 255, 0.05);
    }}
    .view-tab-btn.active {{
      background: #1e293b;
      color: #38bdf8;
      border-color: #38bdf8;
      box-shadow: 0 2px 10px rgba(56, 189, 248, 0.2);
    }}
    .view-tab-btn.active.fresh-tab {{
      color: #fb923c;
      border-color: #f97316;
      box-shadow: 0 2px 10px rgba(249, 115, 22, 0.25);
    }}
    .view-tab-btn.active.applied-tab {{
      color: #34d399;
      border-color: #10b981;
      box-shadow: 0 2px 10px rgba(16, 185, 129, 0.25);
    }}
    .pill-count {{
      font-size: 11px;
      background: rgba(255, 255, 255, 0.12);
      padding: 2px 8px;
      border-radius: 10px;
      color: #e2e8f0;
      font-weight: 800;
    }}

    /* Freshness Badges */
    .badge-fresh-pill {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 6px;
      background: rgba(249, 115, 22, 0.18);
      color: #fb923c;
      border: 1px solid rgba(249, 115, 22, 0.4);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .badge-fresh-pill.today {{
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.4);
    }}
    .badge-older-pill {{
      font-size: 11.5px;
      font-weight: 500;
      padding: 2px 8px;
      border-radius: 6px;
      background: rgba(148, 163, 184, 0.12);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.2);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .btn-roadmap {{
      background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
      color: #fff;
      padding: 8px 18px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid #f472b6;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(236, 72, 153, 0.35);
      transition: all 0.2s ease;
    }}
    .btn-roadmap:hover {{
      filter: brightness(1.2);
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(236, 72, 153, 0.5);
    }}

    .btn-top-refresh {{
      background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #0284c7 100%);
      color: #fff;
      padding: 8px 20px;
      border-radius: 10px;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid #38bdf8;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 16px rgba(37, 99, 235, 0.45);
      transition: all 0.25s ease;
    }}
    .btn-top-refresh:hover {{
      filter: brightness(1.2);
      transform: translateY(-2px);
      box-shadow: 0 6px 22px rgba(56, 189, 248, 0.6);
    }}
    .btn-top-refresh:active {{
      transform: translateY(0);
    }}
    .btn-top-refresh:disabled {{
      opacity: 0.65;
      cursor: not-allowed;
      transform: none;
    }}
    .live-scan-bar {{
      background: linear-gradient(135deg, #131d35 0%, #0f172a 100%);
      border: 1px solid #38bdf8;
      border-radius: 12px;
      padding: 12px 18px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 13px;
      animation: fadeIn 0.3s ease;
    }}
    .scan-spinner {{
      display: inline-block;
      animation: spin 1s linear infinite;
    }}
    @keyframes spin {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      border: 1px solid #10b981;
      color: #fff;
      padding: 14px 22px;
      border-radius: 12px;
      box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.7);
      display: none;
      align-items: center;
      gap: 12px;
      z-index: 100000;
      animation: toastSlideUp 0.3s ease;
    }}
    @keyframes toastSlideUp {{
      from {{ transform: translateY(20px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}

    /* Generator Box */
    .gen-input {{
      width: 100%;
      background: #0f172a;
      border: 1px solid #334155;
      padding: 10px 14px;
      border-radius: 8px;
      color: #fff;
      font-size: 13px;
      margin-bottom: 10px;
    }}
    .gen-input:focus {{ outline: none; border-color: #8b5cf6; }}
    .btn-gen {{
      width: 100%;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      padding: 10px;
      font-size: 14px;
      font-weight: 700;
      border-radius: 8px;
      cursor: pointer;
      border: none;
      color: #fff;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
      transition: all 0.2s;
    }}
    .btn-gen:hover {{ filter: brightness(1.1); transform: translateY(-1px); }}

    /* Roadmap UI Components */
    .roadmap-phase-nav {{
      display: flex;
      gap: 8px;
      padding: 12px 24px;
      background: #0f172a;
      border-bottom: 1px solid #1f2937;
      overflow-x: auto;
    }}
    .phase-tab-btn {{
      background: #1e293b;
      border: 1px solid #334155;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 600;
      color: #94a3b8;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .phase-tab-btn:hover {{
      color: #fff;
      background: #334155;
    }}
    .phase-tab-btn.active {{
      background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
      color: #fff;
      border-color: #f472b6;
      box-shadow: 0 2px 10px rgba(236, 72, 153, 0.4);
    }}
    .skip-box {{
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 16px;
    }}
    .checklist-item {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 12px 14px;
      margin-bottom: 8px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      transition: background 0.15s;
    }}
    .checklist-item:hover {{
      background: #243047;
    }}
    .checklist-item input[type="checkbox"] {{
      margin-top: 3px;
      accent-color: #ec4899;
      width: 17px;
      height: 17px;
      cursor: pointer;
    }}
    .study-material-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 10px;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .study-material-card:hover {{
      border-color: #8b5cf6;
      transform: translateY(-2px);
      box-shadow: 0 4px 14px rgba(139, 92, 246, 0.25);
    }}
    .material-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 6px;
      display: inline-block;
      width: fit-content;
    }}
    .badge-docs {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .badge-repo {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }}
    .badge-course {{ background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }}
    .badge-video {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .badge-guide {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}

    /* Modal Styles */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.82);
      backdrop-filter: blur(8px);
      z-index: 10000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .modal-box {{
      background: #111827;
      border: 1px solid #374151;
      border-radius: 16px;
      width: 100%;
      max-width: 960px;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.9);
      overflow: hidden;
      animation: modalSlideIn 0.25s ease-out;
    }}
    @keyframes modalSlideIn {{
      from {{ transform: scale(0.95) translateY(10px); opacity: 0; }}
      to {{ transform: scale(1) translateY(0); opacity: 1; }}
    }}
    .modal-header {{
      padding: 20px 26px;
      background: #1f2937;
      border-bottom: 1px solid #374151;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
    }}
    .modal-title {{ font-size: 20px; font-weight: 800; color: #fff; }}
    .modal-sub {{ font-size: 13px; color: #9ca3af; margin-top: 4px; }}
    .close-btn {{
      background: transparent;
      border: none;
      color: #9ca3af;
      font-size: 24px;
      cursor: pointer;
      line-height: 1;
      transition: color 0.15s;
    }}
    .close-btn:hover {{ color: #fff; }}

    .modal-tabs {{
      display: flex;
      gap: 6px;
      background: #0f172a;
      padding: 12px 24px;
      border-bottom: 1px solid #1f2937;
      overflow-x: auto;
    }}
    .tab-btn {{
      background: transparent;
      border: 1px solid transparent;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      color: #94a3b8;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
    }}
    .tab-btn:hover {{ color: #fff; background: rgba(255, 255, 255, 0.05); }}
    .tab-btn.active {{
      background: #2563eb;
      color: #fff;
      border-color: #3b82f6;
    }}

    .modal-body {{
      padding: 26px;
      overflow-y: auto;
      flex: 1;
      color: #e2e8f0;
      font-size: 14px;
      line-height: 1.7;
    }}
    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}

    .prep-section {{
      margin-bottom: 24px;
    }}
    .prep-section-title {{
      font-size: 16px;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .star-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 16px 18px;
      margin-bottom: 14px;
    }}
    .star-title {{ font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 8px; }}
    .star-row {{ margin-bottom: 6px; }}
    .star-lbl {{ font-weight: 700; color: #a78bfa; margin-right: 6px; }}
    .pitch-box {{
      background: rgba(16, 185, 129, 0.12);
      border-left: 3px solid #10b981;
      padding: 10px 14px;
      border-radius: 6px;
      margin-top: 10px;
      font-size: 13px;
      color: #6ee7b7;
      font-style: italic;
    }}

    .qa-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 16px;
    }}
    .qa-q {{ font-size: 15px; font-weight: 700; color: #f59e0b; margin-bottom: 8px; }}
    .qa-a {{ color: #cbd5e1; font-size: 13.5px; line-height: 1.65; }}

    .gap-card {{
      background: rgba(239, 68, 68, 0.08);
      border: 1px solid rgba(239, 68, 68, 0.25);
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 10px;
    }}

    .modal-footer {{
      padding: 16px 26px;
      background: #1f2937;
      border-top: 1px solid #374151;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .footer-actions {{ display: flex; gap: 10px; }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Local File Protocol Detection & Switch to Live Server Banner -->
    <div id="fileProtocolNotice" style="display: none; background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%); border: 2px solid #3b82f6; border-radius: 12px; padding: 14px 20px; margin-bottom: 20px; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25);">
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 26px;">🌐</span>
        <div>
          <div style="font-weight: 800; font-size: 15px; color: #fff;">Currently Viewing as Local File (file://) — Switch to Live Web Mode</div>
          <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 3px;">
            To enable instant live scraping and on-spot ModernCV LaTeX PDF generation without browser security blocks, open the dashboard via the local server on port 5000:
          </div>
        </div>
      </div>
      <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
        <a href="http://127.0.0.1:5000/reports/application-dashboard.html" class="btn" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); font-weight: 700; font-size: 13px; padding: 8px 18px; text-decoration: none;">
          🚀 Open Live Server Dashboard (Port 5000) ↗
        </a>
      </div>
    </div>

    <header>
      <div class="header-top">
        <div>
          <h1>Roshan Moger</h1>
          <div class="subtitle">Full Stack Developer (2.5+ Yrs) | React.js &bull; TypeScript &bull; ASP.NET Core &bull; C# &bull; AI/MCP &bull; AWS &bull; Redis</div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
          <button id="btnTopDailySearch" onclick="triggerDailyLiveSearch()" class="btn-top-refresh" title="Scan all portals for today's new vacancies, recalculate match fit against your resume, and update fresh roles">
            <span id="topRefreshIcon" class="refresh-icon">🔄</span> Search & Refresh New Jobs Today
          </button>
          <button id="btnPurgeFreshCrawl" onclick="triggerPurgeAndFreshCrawl()" class="btn-top-refresh" style="background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); border-color: rgba(244,63,94,0.4);" title="Clear all previous stored jobs and run a 100% fresh crawl for today">
            <span id="purgeRefreshIcon" class="refresh-icon">🧹</span> Clear & Fresh Crawl
          </button>
          <button onclick="openRoadmapModal()" class="btn-roadmap">🗺️ Full Stack Study Roadmap & Materials Hub</button>
          <div class="status-pill"><span class="pulse"></span> Multi-Portal Live Search Active</div>
        </div>
      </div>
      <div class="meta-bar">
        <span class="meta-tag">📍 Bangalore &bull; 🇦🇪 Dubai (UAE) &bull; 🇯🇵 Japan (Tokyo) &bull; 🇰🇷 South Korea (Seoul) &bull; 🌐 Remote</span>
        <span class="meta-tag">💼 Current: Associate Software Engineer (ExcelSoft)</span>
        <span class="meta-tag">🎯 Targeted Tier: Strictly 2 to 4 Years (Associate / Mid-Level)</span>
        <span class="meta-tag">🌐 <a href="https://roshan-devhub.netlify.app" target="_blank">roshan-devhub.netlify.app</a></span>
        <span class="meta-tag">🔗 <a href="https://linkedin.com/in/roshan-moger" target="_blank">LinkedIn</a></span>
        <span class="meta-tag">💻 <a href="https://github.com/Roshan-moger" target="_blank">GitHub</a></span>
        <span class="meta-tag">📧 roshanmoger502@gmail.com</span>
      </div>
    </header>

    <!-- Live Scan Activity / Notification Banner -->
    <div id="liveScanFeedbackBar" class="live-scan-bar" style="display: none;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <span id="scanBarIcon" class="scan-spinner" style="font-size: 18px;">🔄</span>
        <div>
          <div id="scanBarTitle" style="font-weight: 700; color: #fff;">Searching live job portals...</div>
          <div id="scanBarDesc" style="font-size: 12px; color: #94a3b8;">Connecting to live multi-portal scraper & recalculating resume fit for today...</div>
        </div>
      </div>
      <div id="scanBarTime" style="font-size: 12px; color: #38bdf8; font-weight: 600;"></div>
    </div>

    <!-- Cross-Portal 1-Click Search Launcher Bar -->
    <div class="portal-launcher-bar">
      <div class="launcher-title">
        <span>🌐 Live Openings Across All Job Boards (Resume-Matched • Max 3 Days • Strictly 2-4 Yrs):</span>
      </div>
      <div class="launcher-grid" id="launcherGrid">
        <a id="linkLinkedInDubai" href="https://www.linkedin.com/jobs/search/?keywords=React%20.NET%20Developer&location=Dubai%2C%20United%20Arab%20Emirates" target="_blank" class="launcher-link" style="border-color: #f59e0b; color: #fcd34d;">
          🇦🇪 LinkedIn Dubai (2-4 Yrs) ↗
        </a>
        <a id="linkNaukriGulf" href="https://www.naukrigulf.com/net-developer-jobs-in-dubai" target="_blank" class="launcher-link" style="border-color: #ea580c; color: #fdba74;">
          🇦🇪 Naukrigulf Dubai (2-4 Yrs) ↗
        </a>
        <a id="linkBaytDubai" href="https://www.bayt.com/en/uae/jobs/net-developer-jobs-in-dubai/" target="_blank" class="launcher-link" style="border-color: #10b981; color: #6ee7b7;">
          🇦🇪 Bayt Dubai (2-4 Yrs) ↗
        </a>
        <a id="linkNaukri" href="https://www.naukri.com/react-dot-net-full-stack-jobs-in-bangalore-bengaluru?k=react%2C%20c%23%2C%20.net%20core%2C%20full%20stack&l=bangalore%2Fbengaluru&experience=2&experience=3&experience=4&jobAge=3" target="_blank" class="launcher-link" style="border-color: #f97316; color: #fdba74;">
          🇮🇳 Naukri India (2-4 Yrs) ↗
        </a>
        <a id="linkLinkedIn" href="https://www.linkedin.com/jobs/search/?keywords=React%20.NET%20Developer&location=Bengaluru%2C%20Karnataka%2C%20India" target="_blank" class="launcher-link" style="border-color: #0ea5e9; color: #7dd3fc;">
          🇮🇳 LinkedIn India (2-4 Yrs) ↗
        </a>
        <a id="linkIndeedIndia" href="https://in.indeed.com/jobs?q=React+.NET+Developer&l=Bengaluru%2C+Karnataka" target="_blank" class="launcher-link" style="border-color: #3b82f6; color: #93c5fd;">
          🇮🇳 Indeed India (2-4 Yrs) ↗
        </a>
      </div>
    </div>

    <!-- Interactive Resume Profile & Match Recalculator Panel -->
    <div class="recalc-card">
      <div class="recalc-top">
        <div>
          <div class="recalc-title">
            <span>⚡ Live Resume Match & Profile Recalculator</span>
            <span id="activeResumeBadge" class="active-resume-badge default">🟢 Default Profile</span>
          </div>
          <p id="candidateProfileText" style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
            Candidate: <strong id="candidateNameDisplay">Roshan Moger</strong> &bull; Experience: <strong id="candidateExpDisplay">2.5+ Years</strong> (<span id="candidateTitleDisplay">Associate Software Engineer, ExcelSoft</span>)
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
          <button id="btnUploadResumeTrigger" onclick="openResumeUploadModal()" class="btn-upload-resume">
            📁 Upload New Resume (PDF / TXT)
          </button>
          <button id="btnRecalculate" onclick="recalculateAllCompanies()" class="btn-refresh">
            <span id="recalcIcon" class="refresh-icon">🔄</span> Refresh & Recalculate Fit
          </button>
        </div>
      </div>

      <!-- Uploaded Resume Status Banner -->
      <div id="uploadedResumeBanner" style="display: none; margin-top: 14px; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 10px 16px; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px; font-size: 13px;">
          <span style="font-size: 18px;">📄</span>
          <div>
            <span style="font-weight: 700; color: #93c5fd;" id="uploadedFileName">Active Uploaded Resume</span>
            <span style="color: #cbd5e1;" id="uploadedSkillsCount"> &bull; Replaced manual profile with extracted skills</span>
          </div>
        </div>
        <button type="button" onclick="revertToDefaultResume()" class="btn" style="background: #334155; padding: 5px 12px; font-size: 12px;">
          ↺ Revert to Roshan Moger Default Profile
        </button>
      </div>

      <div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid #1e293b;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
          <span style="font-size: 12px; color: #cbd5e1; font-weight: 700; text-transform: uppercase;">
            Active Skills from Resume (Click pill to toggle ON/OFF & recalculate):
          </span>
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button type="button" onclick="enableAllSkills()" class="pill-control-btn" title="Enable all skills">✓ Enable All</button>
            <button type="button" onclick="disableAllSkills()" class="pill-control-btn" title="Disable all skills">✕ Disable All</button>
            <button type="button" onclick="resetProfileSkills()" class="pill-control-btn reset" title="Reset to current resume baseline">↺ Reset Defaults</button>
          </div>
        </div>

        <div id="skillsPillContainer" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;"></div>

        <div style="display: flex; gap: 8px; max-width: 500px;">
          <input type="text" id="newSkillInput" class="gen-input" style="margin-bottom:0; padding:8px 12px;" placeholder="Add skill to profile (e.g. Next.js, GraphQL, Python)..." onkeydown="if(event.key==='Enter') addSkillToProfile()">
          <button onclick="addSkillToProfile()" class="btn" style="background: #3b82f6; white-space: nowrap;">+ Add & Recalculate</button>
        </div>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card c-blue">
        <div class="stat-num" id="statRoleCount">{len(jobs_data)}</div>
        <div class="stat-desc">Multi-Portal Roles</div>
      </div>
      <div class="stat-card c-green">
        <div class="stat-num" id="statTopScore">96%</div>
        <div class="stat-desc">Highest Fit Score</div>
      </div>
      <div class="stat-card c-purple">
        <div class="stat-num">7 Portals</div>
        <div class="stat-desc">Naukri, Indeed, Instahyre, etc.</div>
      </div>
      <div class="stat-card c-amber">
        <div class="stat-num" id="statAvgScore">92%</div>
        <div class="stat-desc">Average Match Score</div>
      </div>
    </div>

    <div class="layout-grid">
      <!-- Left: Job Feed -->
      <div>
        <div class="card">
          <div class="card-title" style="justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <span>🎯 Open Vacancies Across All Job Boards (Strictly 2-4 Yrs)</span>
              <button type="button" onclick="openAddJobModal()" class="btn-add-job" title="Add a newly found opening from any job portal or careers site">
                ➕ Add Live Job by URL
              </button>
            </div>
            <span style="font-size: 13px; color: #10b981; font-weight: 600;" id="rankedIndicator">Ranked by Resume Fit</span>
          </div>

          <!-- View Mode Tabs (Fresh Max 3 Days vs All Active vs Applied Archive) -->
          <div class="view-mode-tabs">
            <button id="viewBtnFresh" class="view-tab-btn active fresh-tab" onclick="setViewMode('fresh')">
              🔥 Fresh Openings (Max 3 Days) <span id="countFreshBadge" class="pill-count">0</span>
            </button>
            <button id="viewBtnAll" class="view-tab-btn" onclick="setViewMode('all')">
              📂 All Active Roles <span id="countAllBadge" class="pill-count">0</span>
            </button>
            <button id="viewBtnApplied" class="view-tab-btn applied-tab" onclick="setViewMode('applied')">
              ✅ Applied Archive <span id="countAppliedBadge" class="pill-count">0</span>
            </button>
          </div>

          <!-- Location Filter Tabs (Dubai & India ONLY) -->
          <div class="location-filter-bar">
            <button class="location-filter-btn active" onclick="filterByLocation('all')">🌍 All Locations</button>
            <button class="location-filter-btn" onclick="filterByLocation('dubai')">🇦🇪 Dubai / UAE</button>
            <button class="location-filter-btn" onclick="filterByLocation('india')">🇮🇳 India / Bengaluru</button>
          </div>

          <!-- Platform Filter Tabs -->
          <div class="portal-filter-bar">
            <button class="portal-filter-btn active" onclick="filterByPortal('all')">🌐 All Portals</button>
            <button class="portal-filter-btn" onclick="filterByPortal('Naukri')">🟠 Naukri.com</button>
            <button class="portal-filter-btn" onclick="filterByPortal('Indeed')">🔵 Indeed</button>
            <button class="portal-filter-btn" onclick="filterByPortal('Instahyre')">🟣 Instahyre</button>
            <button class="portal-filter-btn" onclick="filterByPortal('Wellfound')">🔴 Wellfound</button>
            <button class="portal-filter-btn" onclick="filterByPortal('Company Portal')">🟢 Company Portals</button>
            <button class="portal-filter-btn" onclick="filterByPortal('LinkedIn')">🔷 LinkedIn</button>
            <button class="portal-filter-btn" onclick="filterByPortal('freehire.me')">🌐 freehire ATS</button>
          </div>

          <input type="text" id="filterBox" class="search-input" placeholder="Search roles by keyword, company, or tech stack (e.g. Swiggy, Siemens, Accenture, React, C#)..." onkeyup="filter()">

          <!-- Empty State Message -->
          <div id="emptyStateMsg" style="display: none; padding: 32px 20px; text-align: center; background: #0f172a; border-radius: 12px; margin-bottom: 16px; border: 1px dashed #334155;">
            <div style="font-size: 32px; margin-bottom: 8px;" id="emptyIcon">🔍</div>
            <div style="font-size: 16px; font-weight: 700; color: #fff;" id="emptyTitle">No roles matching criteria</div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 6px; max-width: 480px; margin-left: auto; margin-right: auto;" id="emptyDesc">
              Try switching to "All Active Roles" or click Refresh.
            </div>
          </div>

          <div class="job-list" id="jobContainer">
            {jobs_html}
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div>
        <!-- Full Stack Study Roadmap Card -->
        <div class="card" style="border: 2px solid #ec4899; background: linear-gradient(135deg, #201026 0%, #111827 100%);">
          <div class="card-title" style="color: #f472b6; justify-content: space-between;">
            <span>🗺️ Full Stack Upskilling Roadmap</span>
            <span style="font-size: 11px; background: rgba(236,72,153,0.25); color: #f472b6; padding: 2px 8px; border-radius: 6px; font-weight: 700;">2+ Yrs -> Senior</span>
          </div>
          <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 12px; line-height: 1.6;">
            Personalized to your resume. Skip the junior basics you already know, master high-yield topics, and access top-tier free study materials:
          </p>
          <div style="font-size: 12.5px; color: #e2e8f0; line-height: 1.8; margin-bottom: 14px;">
            <div>&bull; <strong>Phase 1:</strong> Next.js App Router, RSC & Web Vitals (~18h)</div>
            <div>&bull; <strong>Phase 2:</strong> Clean Architecture & CQRS (.NET Core) (~20h)</div>
            <div>&bull; <strong>Phase 3:</strong> High-Scale SQL Indexing & Redis Caching (~16h)</div>
            <div>&bull; <strong>Phase 4:</strong> AWS Cloud & Production CI/CD (~14h)</div>
            <div>&bull; <strong>Phase 5:</strong> System Design (LLD & HLD Patterns) (~18h)</div>
          </div>
          <button onclick="openRoadmapModal()" class="btn" style="width: 100%; background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 10px; font-weight: 700; border-radius: 8px;">
            📖 Open Interactive Roadmap & Free Study Materials
          </button>
        </div>

        <!-- Instant Custom Generator Card -->
        <div class="card" style="border: 2px solid #8b5cf6; background: #13172c;">
          <div class="card-title" style="color: #c084fc;">
            <span>⚡ Any Company Interview Generator</span>
          </div>
          <p style="font-size: 13px; color: #94a3b8; margin-bottom: 14px;">
            Found another opening on any website or job board? Type the company and required stack below to dynamically generate a tailored interview preparation guide based on your resume:
          </p>
          <input type="text" id="customCompany" class="gen-input" placeholder="Company Name (e.g. Swiggy, Zepto, Microsoft)">
          <input type="text" id="customRole" class="gen-input" placeholder="Role Title (e.g. SDE 1 Full Stack)">
          <input type="text" id="customSkills" class="gen-input" placeholder="Key Skills (e.g. React, Node.js, Redis, AWS, SQL)">
          <button onclick="generateCustomPrep()" class="btn-gen">🚀 Generate Custom Prep Guide</button>
        </div>

        <div class="card">
          <div class="card-title">🌐 Multi-Portal Search Coverage</div>
          <div style="font-size: 13px; color: #cbd5e1; line-height: 1.7;">
            <p style="margin-bottom: 10px;">Your job search is now scanning across <strong>7 major channels</strong>:</p>
            <p style="color: #fdba74; margin-bottom: 6px;">&bull; <strong>Naukri.com:</strong> Direct recruiter postings in Bangalore IT parks.</p>
            <p style="color: #93c5fd; margin-bottom: 6px;">&bull; <strong>Indeed India:</strong> High-volume global MNC and enterprise roles.</p>
            <p style="color: #c4b5fd; margin-bottom: 6px;">&bull; <strong>Instahyre:</strong> AI-matched hiring for top funded unicorns (Swiggy, PhonePe, Zepto).</p>
            <p style="color: #fca5a5; margin-bottom: 6px;">&bull; <strong>Wellfound:</strong> Fast-scaling venture-backed tech startups.</p>
            <p style="color: #6ee7b7; margin-bottom: 6px;">&bull; <strong>Direct Career Sites:</strong> Direct enterprise ATS applications (Quest Global, PwC, Truemeds).</p>
            <p style="color: #7dd3fc;">&bull; <strong>freehire.me:</strong> Open-source aggregator pulling from ~50 ATS platforms.</p>
          </div>
        </div>

        <div class="card">
          <div class="card-title">💬 Assistant Quick Commands</div>
          <div style="font-size: 13px; color: #cbd5e1; line-height: 1.7;">
            <p style="margin-bottom: 6px;">Tell me in chat anytime:</p>
            <p style="color: #38bdf8;">&bull; <em>"Prepare me for Swiggy SDE 1 interview"</em></p>
            <p style="color: #38bdf8;">&bull; <em>"Apply to Siemens Junior Full Stack Developer"</em></p>
            <p style="color: #38bdf8;">&bull; <em>"Prepare me for Accenture Application Developer"</em></p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toastNotification" class="toast">
    <span style="font-size: 18px;">✅</span>
    <span id="toastMessage">Recalculation complete!</span>
  </div>

  <!-- Dynamic Interview Preparation Modal -->
  <div class="modal-backdrop" id="prepModal">
    <div class="modal-box">
      <div class="modal-header">
        <div>
          <div class="modal-title" id="modalTitle">Company Interview Preparation</div>
          <div class="modal-sub" id="modalSub">Full Stack Developer | Dynamic Prep Pack for Roshan Moger</div>
        </div>
        <button class="close-btn" onclick="closePrepModal()">&times;</button>
      </div>

      <div class="modal-tabs">
        <button class="tab-btn active" onclick="switchTab('tab-fit')">📊 Resume Fit & Gaps</button>
        <button class="tab-btn" onclick="switchTab('tab-star')">🚀 Tailored STAR Stories</button>
        <button class="tab-btn" onclick="switchTab('tab-qa')">💻 Technical Deep Dive</button>
        <button class="tab-btn" onclick="switchTab('tab-design')">🏗️ System Design</button>
        <button class="tab-btn" onclick="switchTab('tab-reverse')">🙋 Questions to Ask</button>
      </div>

      <div class="modal-body">
        <!-- Tab 1: Resume Fit & Gaps -->
        <div id="tab-fit" class="tab-pane active">
          <div class="prep-section">
            <div class="prep-section-title">✅ Direct Matches on Your Resume</div>
            <div id="directMatchesList" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px;"></div>
          </div>

          <div class="prep-section">
            <div class="prep-section-title">🔍 Areas to Brush Up Based on Your Resume</div>
            <div id="gapAdviceList"></div>
          </div>
        </div>

        <!-- Tab 2: Tailored STAR Stories -->
        <div id="tab-star" class="tab-pane">
          <div class="prep-section">
            <div class="prep-section-title">🌟 Tailored Behavioral & Technical STAR Stories</div>
            <p style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">These stories are specifically adapted to this company's business challenges, ready for you to speak in 1-2 minutes:</p>
            <div id="starStoriesList"></div>
          </div>
        </div>

        <!-- Tab 3: Technical Q&A -->
        <div id="tab-qa" class="tab-pane">
          <div class="prep-section">
            <div class="prep-section-title">💻 High-Probability Technical Questions & Model Answers</div>
            <div id="qaList"></div>
          </div>
        </div>

        <!-- Tab 4: System Design -->
        <div id="tab-design" class="tab-pane">
          <div class="prep-section">
            <div class="prep-section-title">🏗️ Architectural & System Design Scenario</div>
            <div class="qa-card">
              <div class="qa-q" id="designTitle">System Design Challenge</div>
              <div class="qa-a" id="designSteps">
                <ol style="padding-left: 20px; margin-top: 8px; line-height: 1.8;">
                  <li><strong>Clarify Scope:</strong> Pin down read vs. write volume, consistency needs, and peak latency SLA.</li>
                  <li><strong>API Contracts:</strong> Detail RESTful or WebSocket endpoints with payload schemas and auth tokens.</li>
                  <li><strong>Data & Caching Tier:</strong> Utilize Redis caching for frequently read metadata; back with SQL / NoSQL database with proper indexes.</li>
                  <li><strong>Resilience & Scalability:</strong> Horizontal container scaling (Docker / K8s), circuit breakers, and rate limiters.</li>
                </ol>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 5: Reverse Questions -->
        <div id="tab-reverse" class="tab-pane">
          <div class="prep-section">
            <div class="prep-section-title">🙋 High-Signal Questions You Should Ask the Interviewer</div>
            <div id="reverseQuestionsList" style="line-height: 1.8;"></div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <div style="font-size: 12px; color: #94a3b8;" id="modalFooterNote">Custom synthesized for Roshan Moger</div>
        <div class="footer-actions">
          <button class="btn" style="background: #334155;" onclick="copyGuideToClipboard()">📋 Copy Markdown</button>
          <button class="btn" style="background: #10b981;" onclick="downloadGuideMarkdown()">📥 Download .md</button>
          <button class="btn" style="background: #2563eb;" onclick="window.print()">🖨️ Print</button>
          <button class="btn" style="background: #ef4444;" onclick="closePrepModal()">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Full Stack Developer Upskilling Roadmap Modal -->
  <div id="roadmapModal" class="modal-backdrop" onclick="if(event.target===this) closeRoadmapModal()">
    <div class="modal-box" style="max-width: 1020px;">
      <div class="modal-header" style="border-bottom: 2px solid #ec4899; background: linear-gradient(135deg, #201026 0%, #111827 100%);">
        <div>
          <div class="modal-title" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <span>🗺️ Tailored Full Stack Developer Upskilling Roadmap</span>
            <span style="font-size: 12px; background: rgba(236,72,153,0.25); color: #f472b6; padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(236,72,153,0.4);">
              Associate (2+ Yrs) ➔ Senior SDE
            </span>
          </div>
          <div class="modal-sub" style="color: #cbd5e1; margin-top: 6px;">
            Synthesized dynamically for <strong>Roshan Moger</strong> based on verified resume baseline & production stack.
          </div>
        </div>
        <button class="close-btn" onclick="closeRoadmapModal()">&times;</button>
      </div>

      <!-- Roadmap Phase Tabs -->
      <div class="roadmap-phase-nav" id="roadmapTabs"></div>

      <!-- Roadmap Modal Body -->
      <div class="modal-body" id="roadmapModalBody" style="background: #0d1321; max-height: 65vh;"></div>

      <!-- Modal Footer -->
      <div class="modal-footer" style="background: #111827; border-top: 1px solid #1f2937;">
        <div style="font-size: 12px; color: #94a3b8;">
          💡 Complete 8-Week plan (~75-90 study hours). Checkbox progress saves automatically in your browser.
        </div>
        <div class="footer-actions">
          <button class="btn" style="background: #334155;" onclick="copyRoadmapMarkdown()">📋 Copy Full Roadmap (.md)</button>
          <button class="btn" style="background: #ec4899;" onclick="downloadRoadmapMarkdown()">📥 Download Roadmap (.md)</button>
          <button class="btn" style="background: #374151;" onclick="closeRoadmapModal()">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Upload New Resume Modal -->
  <div id="resumeUploadModal" class="modal-backdrop" onclick="if(event.target===this) closeResumeUploadModal()">
    <div class="modal-box" style="max-width: 680px;">
      <div class="modal-header" style="border-bottom: 2px solid #10b981; background: linear-gradient(135deg, #0e271f 0%, #111827 100%);">
        <div>
          <div class="modal-title" style="display: flex; align-items: center; gap: 10px;">
            <span>📄 Upload New Resume</span>
            <span style="font-size: 11px; background: rgba(16, 185, 129, 0.25); color: #34d399; padding: 2px 8px; border-radius: 6px; font-weight: 700;">Client-Side Parser</span>
          </div>
          <div class="modal-sub">
            Upload your resume (.pdf, .txt, .docx, .json) or paste text. It will automatically extract your technical skills, experience, and title, and <strong>replace the manual profile</strong> to re-score all vacancies instantly!
          </div>
        </div>
        <button class="close-btn" onclick="closeResumeUploadModal()">&times;</button>
      </div>

      <div class="modal-body" style="background: #0d1321; padding: 24px;">
        <!-- Dropzone -->
        <div id="resumeDropZone" class="upload-dropzone" onclick="document.getElementById('resumeFileInput').click()" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)">
          <input type="file" id="resumeFileInput" accept=".pdf,.txt,.docx,.json,.md" style="display:none" onchange="handleResumeFileSelect(event)">
          <div style="font-size: 38px; margin-bottom: 8px;">📥</div>
          <div style="font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 4px;">Drag & Drop Your Resume PDF / File Here</div>
          <div style="font-size: 13px; color: #94a3b8; margin-bottom: 12px;">Supports PDF, TXT, DOCX, MD, JSON files (parsed locally in browser)</div>
          <button type="button" class="btn" style="background: #10b981; pointer-events: none;">Browse File from Computer</button>
        </div>

        <div style="display: flex; align-items: center; margin: 18px 0; gap: 12px;">
          <div style="flex: 1; height: 1px; background: #334155;"></div>
          <span style="font-size: 12px; color: #64748b; font-weight: 700; text-transform: uppercase;">Or Paste Resume Text</span>
          <div style="flex: 1; height: 1px; background: #334155;"></div>
        </div>

        <div>
          <textarea id="resumeTextPaste" class="gen-input" style="height: 110px; font-family: monospace; font-size: 12px; resize: vertical;" placeholder="Paste raw text or markdown from your resume here (e.g. John Doe, Full Stack Engineer with 3+ years experience in React, Python, PostgreSQL, AWS, Docker...)..."></textarea>
          <div style="display: flex; justify-content: flex-end; margin-top: 8px;">
            <button type="button" onclick="parsePastedResumeText()" class="btn" style="background: #2563eb;">
              ⚡ Parse Pasted Text
            </button>
          </div>
        </div>

        <div id="uploadLoadingSpinner" style="display: none; text-align: center; padding: 20px;">
          <div class="spinning" style="font-size: 28px; display: inline-block;">⏳</div>
          <div style="font-size: 13px; color: #93c5fd; margin-top: 6px;">Extracting skills and profile details from resume...</div>
        </div>

        <!-- Live Extraction Feedback Preview -->
        <div id="uploadResultPreview" style="display: none; margin-top: 18px; background: #1e293b; border: 1px solid #10b981; border-radius: 10px; padding: 16px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #34d399; font-weight: 700; font-size: 14px;">✅ Resume Successfully Parsed!</span>
            <span id="previewSkillsCountBadge" style="font-size: 11px; background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 8px; border-radius: 6px; font-weight: 700;">0 Skills</span>
          </div>
          <div id="extractedDetailsBox" style="font-size: 13px; color: #cbd5e1; line-height: 1.6;"></div>
          <div style="margin-top: 10px; font-size: 12px; color: #94a3b8; font-weight: 600;">Extracted Skills (will replace manual profile):</div>
          <div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px; max-height: 120px; overflow-y: auto;" id="extractedSkillsPills"></div>
          <div style="margin-top: 16px; display: flex; justify-content: flex-end; gap: 10px;">
            <button type="button" class="btn" style="background: #334155;" onclick="closeResumeUploadModal()">Cancel</button>
            <button type="button" class="btn" style="background: #10b981; font-weight: 700;" onclick="applyUploadedResume()">
              🚀 Apply & Replace Manual Profile
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer" style="background: #111827;">
        <div style="font-size: 12px; color: #94a3b8;">💡 Extracted skills will replace the manual list and automatically update all match rankings.</div>
        <button class="btn" style="background: #475569;" onclick="closeResumeUploadModal()">Close</button>
      </div>
    </div>
  </div>

  <!-- Add Custom Job Vacancy Modal -->
  <div id="addJobModal" class="modal-backdrop" onclick="if(event.target===this) closeAddJobModal()">
    <div class="modal-box" style="max-width: 640px;">
      <div class="modal-header" style="border-bottom: 2px solid #8b5cf6; background: linear-gradient(135deg, #1e1335 0%, #111827 100%);">
        <div>
          <div class="modal-title" style="display: flex; align-items: center; gap: 10px;">
            <span>➕ Add Vacancy from Any Job Board</span>
          </div>
          <div class="modal-sub">
            Found an opening on Naukri, Indeed, LinkedIn, or a company site? Paste it here to score it against your resume and generate dynamic interview prep!
          </div>
        </div>
        <button class="close-btn" onclick="closeAddJobModal()">&times;</button>
      </div>

      <div class="modal-body" style="background: #0d1321; padding: 24px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
          <div>
            <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Company Name *</label>
            <input type="text" id="newJobCompany" class="gen-input" placeholder="e.g. Swiggy, Zepto, Microsoft..." required>
          </div>
          <div>
            <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Role Title *</label>
            <input type="text" id="newJobTitle" class="gen-input" placeholder="e.g. Full Stack Engineer I..." required>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
          <div>
            <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Portal / Source</label>
            <select id="newJobPortal" class="gen-input" style="height: 38px;">
              <option value="Naukri">Naukri.com</option>
              <option value="Indeed">Indeed</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="Instahyre">Instahyre</option>
              <option value="Wellfound">Wellfound</option>
              <option value="Company Portal" selected>Company Career Page</option>
              <option value="Other">Other Job Board</option>
            </select>
          </div>
          <div>
            <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Location</label>
            <input type="text" id="newJobLocation" class="gen-input" placeholder="e.g. Bengaluru, Karnataka / Remote">
          </div>
        </div>

        <div style="margin-bottom: 12px;">
          <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Application URL *</label>
          <input type="url" id="newJobUrl" class="gen-input" placeholder="https://careers.company.com/job/12345" required>
        </div>

        <div style="margin-bottom: 12px;">
          <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Required Tech Stack / Skills (comma separated) *</label>
          <input type="text" id="newJobSkills" class="gen-input" placeholder="e.g. React, TypeScript, Node.js, AWS, Redis..." required>
        </div>

        <div style="margin-bottom: 12px;">
          <label style="font-size: 12px; color: #94a3b8; font-weight: 600; display: block; margin-bottom: 4px;">Quick Note / Highlights</label>
          <input type="text" id="newJobNote" class="gen-input" placeholder="e.g. Direct opening posted today on company careers page.">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px;">
          <button type="button" class="btn" style="background: #334155;" onclick="closeAddJobModal()">Cancel</button>
          <button type="button" class="btn" style="background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); font-weight: 700;" onclick="submitCustomJob()">
            🎯 Add Vacancy & Analyze Fit
          </button>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Embedded Jobs Data across all portals and Precomputed Guides
    const jobsList = {json.dumps(jobs_data)};
    const prepDatabase = {json.dumps(prep_database)};
    const roadmapPhases = {json.dumps(ROADMAP_PHASES)};
    const roadmapMarkdownRaw = {json.dumps(generate_roadmap_markdown())};
    let activePhaseNum = 1;
    let currentPrepData = null;
    let selectedPortal = "all";
    let selectedLocation = "all";

    // Applied Tracking State (Stored persistently in browser localStorage)
    let appliedJobIds = [];
    try {{
      appliedJobIds = JSON.parse(localStorage.getItem("roshan_applied_jobs") || "[]");
    }} catch(e) {{
      appliedJobIds = [];
    }}

    // View Mode: 'fresh' (Max 3 Days, default), 'all' (All Active Roles), or 'applied' (Applied Archive)
    let currentViewMode = "fresh";

    function setViewMode(mode) {{
      currentViewMode = mode;
      const bFresh = document.getElementById("viewBtnFresh");
      const bAll = document.getElementById("viewBtnAll");
      const bApplied = document.getElementById("viewBtnApplied");
      if (bFresh) bFresh.classList.toggle("active", mode === "fresh");
      if (bAll) bAll.classList.toggle("active", mode === "all");
      if (bApplied) bApplied.classList.toggle("active", mode === "applied");
      filter();
    }}

    function toggleApplyJob(jobId) {{
      const job = jobsList.find(j => j.id === jobId);
      const companyName = job ? job.company : "Role";
      
      if (appliedJobIds.includes(jobId)) {{
        appliedJobIds = appliedJobIds.filter(id => id !== jobId);
        showToast(`↩️ ${{companyName}} restored to Active Vacancies!`);
      }} else {{
        appliedJobIds.push(jobId);
        showToast(`✅ ${{companyName}} marked as Applied! Moved to Applied Archive.`);
      }}
      localStorage.setItem("roshan_applied_jobs", JSON.stringify(appliedJobIds));
      filter();
    }}

    // Deleted Roles Tracking (Stored persistently in browser localStorage & synced to backend)
    let deletedJobIds = new Set();
    try {{
      const storedDeleted = JSON.parse(localStorage.getItem("roshan_deleted_jobs") || "[]");
      deletedJobIds = new Set(storedDeleted);
    }} catch(e) {{
      deletedJobIds = new Set();
    }}

    async function deleteJobRole(jobId, event) {{
      if (event) event.stopPropagation();
      const job = jobsList.find(j => j.id === jobId);
      const companyName = job ? `${{job.company}} (${{job.title}})` : "this role";

      if (!confirm(`Are you sure you want to permanently delete ${{companyName}}?`)) {{
        return;
      }}

      // 1. Add to deletedJobIds
      deletedJobIds.add(jobId);
      localStorage.setItem("roshan_deleted_jobs", JSON.stringify(Array.from(deletedJobIds)));

      // 2. Remove from appliedJobIds if present
      if (appliedJobIds.includes(jobId)) {{
        appliedJobIds = appliedJobIds.filter(id => id !== jobId);
        localStorage.setItem("roshan_applied_jobs", JSON.stringify(appliedJobIds));
      }}

      // 3. Remove from custom jobs if present
      try {{
        let storedCustomJobs = JSON.parse(localStorage.getItem("roshan_custom_jobs") || "[]");
        storedCustomJobs = storedCustomJobs.filter(j => j.id !== jobId);
        localStorage.setItem("roshan_custom_jobs", JSON.stringify(storedCustomJobs));
      }} catch(e) {{}}

      // 4. Animate and remove from DOM
      const card = document.querySelector(`.job-item[data-id="${{jobId}}"]`);
      if (card) {{
        card.style.transition = "all 0.3s ease";
        card.style.opacity = "0";
        card.style.transform = "scale(0.95)";
        setTimeout(() => {{
          card.remove();
          filter();
        }}, 300);
      }} else {{
        filter();
      }}

      showToast(`🗑️ Permanently removed ${{companyName}}.`);

      // 5. Notify backend server to permanently delete from data/jobs_database.json
      try {{
        const deleteUrl = window.location.origin.includes("5000") ? "/api/delete-job" : "http://127.0.0.1:5000/api/delete-job";
        fetch(deleteUrl, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ id: jobId }})
        }}).catch(() => {{}});
      }} catch(e) {{}}
    }}

    // Canonical Resume Skills for Roshan Moger
    const defaultSkills = [
      "React.js", "TypeScript", "JavaScript", "ASP.NET Core", "C#", "REST APIs",
      "Model Context Protocol (MCP)", "AWS Bedrock", "Google Gemini",
      "Redux", "Tailwind CSS", "Redis", "WebSockets", "Docker", "Kubernetes",
      "AWS", "PostgreSQL", "MongoDB", "SQL Server", "Node.js", "Express.js"
    ];
    let allProfileSkills = [...defaultSkills];
    let disabledSkillSet = new Set();
    let activeSkills = [...defaultSkills];

    function updateActiveSkills() {{
      activeSkills = allProfileSkills.filter(s => !disabledSkillSet.has(s));
    }}

    // Render Skill Toggle Pills without removing elements from DOM
    function renderSkillToggles() {{
      const container = document.getElementById("skillsPillContainer");
      if (!container) return;
      container.innerHTML = "";
      allProfileSkills.forEach(skill => {{
        const isOff = disabledSkillSet.has(skill);
        const isCustom = !defaultSkills.includes(skill);
        const pill = document.createElement("div");
        pill.className = `skill-toggle-pill ${{isOff ? 'inactive' : 'active'}}`;
        pill.title = isOff ? `Click to re-enable "${{skill}}"` : `Click to temporarily disable "${{skill}}"`;

        const iconSpan = document.createElement("span");
        iconSpan.className = "pill-icon";
        iconSpan.innerText = isOff ? "+" : "✓";
        pill.appendChild(iconSpan);

        const textSpan = document.createElement("span");
        textSpan.innerText = " " + skill;
        pill.appendChild(textSpan);

        if (isCustom) {{
          const delSpan = document.createElement("span");
          delSpan.className = "pill-del";
          delSpan.innerHTML = "&times;";
          delSpan.title = "Delete custom skill";
          delSpan.onclick = (e) => {{
            e.stopPropagation();
            deleteCustomSkill(skill);
          }};
          pill.appendChild(delSpan);
        }}

        pill.onclick = () => toggleSkill(skill);
        container.appendChild(pill);
      }});
    }}

    function toggleSkill(skill) {{
      if (disabledSkillSet.has(skill)) {{
        disabledSkillSet.delete(skill);
      }} else {{
        disabledSkillSet.add(skill);
      }}
      updateActiveSkills();
      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
    }}

    function enableAllSkills() {{
      disabledSkillSet.clear();
      updateActiveSkills();
      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
    }}

    function disableAllSkills() {{
      allProfileSkills.forEach(s => disabledSkillSet.add(s));
      updateActiveSkills();
      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
    }}

    function deleteCustomSkill(skill) {{
      allProfileSkills = allProfileSkills.filter(s => s !== skill);
      disabledSkillSet.delete(skill);
      updateActiveSkills();
      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
    }}

    function addSkillToProfile() {{
      const input = document.getElementById("newSkillInput");
      const val = input.value.trim();
      if (!val) return;
      if (!allProfileSkills.some(s => s.toLowerCase() === val.toLowerCase())) {{
        allProfileSkills.push(val);
      }}
      disabledSkillSet.delete(val);
      input.value = "";
      updateActiveSkills();
      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
    }}

    function resetProfileSkills() {{
      try {{
        const storedResume = JSON.parse(localStorage.getItem("roshan_custom_resume") || "null");
        if (storedResume && storedResume.skills && storedResume.skills.length) {{
          allProfileSkills = [...storedResume.skills];
        }} else {{
          allProfileSkills = [...defaultSkills];
        }}
      }} catch(e) {{
        allProfileSkills = [...defaultSkills];
      }}
      disabledSkillSet.clear();
      updateActiveSkills();
      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
      updatePortalLauncherLinks();
    }}

    // Technical Skills Taxonomy for Resume Extraction
    const TECH_DATABASE = [
      {{ name: "React.js", tokens: ["react", "react.js", "reactjs"] }},
      {{ name: "TypeScript", tokens: ["typescript", "ts"] }},
      {{ name: "JavaScript", tokens: ["javascript", "js", "es6"] }},
      {{ name: "Next.js", tokens: ["next.js", "nextjs", "next"] }},
      {{ name: "ASP.NET Core", tokens: ["asp.net core", ".net core", "asp.net", "dotnet core"] }},
      {{ name: "C#", tokens: ["c#", "csharp"] }},
      {{ name: ".NET", tokens: [".net", "dotnet"] }},
      {{ name: "Node.js", tokens: ["node.js", "nodejs", "node"] }},
      {{ name: "Express.js", tokens: ["express.js", "expressjs", "express"] }},
      {{ name: "REST APIs", tokens: ["rest api", "rest apis", "restful", "rest"] }},
      {{ name: "Redux", tokens: ["redux", "rtk", "redux toolkit"] }},
      {{ name: "Tailwind CSS", tokens: ["tailwind", "tailwindcss"] }},
      {{ name: "Redis", tokens: ["redis"] }},
      {{ name: "WebSockets", tokens: ["websocket", "websockets", "socket.io"] }},
      {{ name: "Docker", tokens: ["docker"] }},
      {{ name: "Kubernetes", tokens: ["kubernetes", "k8s"] }},
      {{ name: "AWS", tokens: ["aws", "amazon web services", "ec2", "s3", "lambda"] }},
      {{ name: "Azure", tokens: ["azure"] }},
      {{ name: "GCP", tokens: ["gcp", "google cloud"] }},
      {{ name: "SQL", tokens: ["sql", "mysql", "sql server", "tsql"] }},
      {{ name: "PostgreSQL", tokens: ["postgresql", "postgres"] }},
      {{ name: "MongoDB", tokens: ["mongodb", "mongo"] }},
      {{ name: "GraphQL", tokens: ["graphql"] }},
      {{ name: "Python", tokens: ["python"] }},
      {{ name: "Django", tokens: ["django"] }},
      {{ name: "FastAPI", tokens: ["fastapi"] }},
      {{ name: "Java", tokens: ["java", "spring boot", "spring"] }},
      {{ name: "Golang", tokens: ["golang", "go"] }},
      {{ name: "Microservices", tokens: ["microservices", "microservice"] }},
      {{ name: "CI/CD", tokens: ["ci/cd", "cicd", "github actions", "jenkins"] }},
      {{ name: "Kafka", tokens: ["kafka"] }},
      {{ name: "Elasticsearch", tokens: ["elasticsearch"] }},
      {{ name: "HTML5", tokens: ["html5", "html"] }},
      {{ name: "CSS3", tokens: ["css3", "css", "sass", "scss"] }},
      {{ name: "Jest", tokens: ["jest"] }},
      {{ name: "Cypress", tokens: ["cypress"] }},
      {{ name: "Git", tokens: ["git", "github", "gitlab"] }}
    ];

    let pendingResumeData = null;

    function openResumeUploadModal() {{
      const m = document.getElementById("resumeUploadModal");
      if (m) m.style.display = "flex";
      document.body.style.overflow = "hidden";
    }}

    function closeResumeUploadModal() {{
      const m = document.getElementById("resumeUploadModal");
      if (m) m.style.display = "none";
      document.body.style.overflow = "auto";
      const preview = document.getElementById("uploadResultPreview");
      if (preview) preview.style.display = "none";
      pendingResumeData = null;
    }}

    function handleDragOver(e) {{
      e.preventDefault();
      const dropZone = document.getElementById("resumeDropZone");
      if (dropZone) dropZone.classList.add("dragover");
    }}

    function handleDragLeave(e) {{
      e.preventDefault();
      const dropZone = document.getElementById("resumeDropZone");
      if (dropZone) dropZone.classList.remove("dragover");
    }}

    function handleDrop(e) {{
      e.preventDefault();
      const dropZone = document.getElementById("resumeDropZone");
      if (dropZone) dropZone.classList.remove("dragover");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {{
        processSelectedResumeFile(e.dataTransfer.files[0]);
      }}
    }}

    function handleResumeFileSelect(e) {{
      if (e.target.files && e.target.files.length > 0) {{
        processSelectedResumeFile(e.target.files[0]);
      }}
    }}

    async function processSelectedResumeFile(file) {{
      const spinner = document.getElementById("uploadLoadingSpinner");
      if (spinner) spinner.style.display = "block";
      const preview = document.getElementById("uploadResultPreview");
      if (preview) preview.style.display = "none";

      const fileName = file.name;
      const lowerName = fileName.toLowerCase();

      try {{
        let extractedText = "";
        if (lowerName.endsWith(".pdf")) {{
          extractedText = await extractTextFromPdf(file);
        }} else {{
          extractedText = await extractTextFromTextFile(file);
        }}
        if (spinner) spinner.style.display = "none";
        parseAndDisplayResume(extractedText, fileName);
      }} catch(err) {{
        if (spinner) spinner.style.display = "none";
        alert("Notice when reading file: " + err.message + "\\nYou can also paste your resume text directly into the box below.");
      }}
    }}

    function extractTextFromTextFile(file) {{
      return new Promise((resolve, reject) => {{
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(new Error("Unable to read file text"));
        reader.readAsText(file);
      }});
    }}

    async function extractTextFromPdf(file) {{
      if (!window.pdfjsLib) {{
        throw new Error("PDF parser loading. Please paste text directly if offline.");
      }}
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({{ data: arrayBuffer }}).promise;
      let fullText = "";
      for (let i = 1; i <= pdf.numPages; i++) {{
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        fullText += textContent.items.map(item => item.str).join(" ") + "\\n";
      }}
      return fullText;
    }}

    function parsePastedResumeText() {{
      const text = document.getElementById("resumeTextPaste").value.trim();
      if (!text) {{
        alert("Please paste your resume text or markdown into the box.");
        return;
      }}
      parseAndDisplayResume(text, "Pasted_Resume_Text");
    }}

    function parseAndDisplayResume(rawText, fileName) {{
      if (!rawText || rawText.trim().length < 15) {{
        alert("Insufficient text detected. Please paste your resume text directly.");
        return;
      }}

      // Clean text for matching
      const normText = (" " + rawText.toLowerCase().replace(/[\\r\\n\\t,;()\\[\\]{{}}:\\"\\']/g, " ") + " ").replace(/\\s+/g, " ");

      const matchedSkills = [];
      TECH_DATABASE.forEach(tech => {{
        const isMatch = tech.tokens.some(t => normText.includes(" " + t + " "));
        if (isMatch) {{
          matchedSkills.push(tech.name);
        }}
      }});

      if (matchedSkills.length === 0) {{
        matchedSkills.push("Software Engineering", "Full Stack", "APIs", "Web Development");
      }}

      // Candidate Name extraction
      const rawLines = rawText.split(/[\\r\\n]+/).map(l => l.trim()).filter(l => l.length > 2);
      let candidateName = "Uploaded Candidate";
      for (let i = 0; i < Math.min(rawLines.length, 6); i++) {{
        const l = rawLines[i];
        if (l.length < 35 && !l.includes("@") && !l.includes("http") && !/resume|curriculum|phone|email|linkedin|github|profile|summary/i.test(l)) {{
          candidateName = l;
          break;
        }}
      }}

      let candidateExp = "2.5+ Years Experience";
      let candidateTitle = "Full Stack Engineer";
      const expMatch = rawText.match(/(\\d+[\\+]?\\s*(?:years|yrs)(?:\\s*of)?\\s*experience)/i);
      if (expMatch) {{
        candidateExp = expMatch[1];
      }}
      const titleMatch = rawText.match(/((?:Senior|Associate|Lead|Staff|Junior)?\\s*(?:Full\\s*Stack|Frontend|Backend|Software)\\s*(?:Engineer|Developer))/i);
      if (titleMatch) {{
        candidateTitle = titleMatch[1];
      }}

      pendingResumeData = {{
        name: candidateName,
        exp: candidateExp,
        title: candidateTitle,
        skills: matchedSkills,
        fileName: fileName,
        timestamp: Date.now()
      }};

      const preview = document.getElementById("uploadResultPreview");
      const detailsBox = document.getElementById("extractedDetailsBox");
      const pillsContainer = document.getElementById("extractedSkillsPills");
      const countBadge = document.getElementById("previewSkillsCountBadge");

      if (detailsBox) {{
        detailsBox.innerHTML = `
          <div>Candidate Name: <strong style="color:#fff;">${{candidateName}}</strong></div>
          <div>Experience / Title: <strong style="color:#38bdf8;">${{candidateExp}}</strong> (${{candidateTitle}})</div>
          <div>Source File: <span style="color:#94a3b8;">${{fileName}}</span></div>
        `;
      }}

      if (countBadge) {{
        countBadge.innerText = `${{matchedSkills.length}} Skills Detected`;
      }}

      if (pillsContainer) {{
        pillsContainer.innerHTML = matchedSkills.map(s => `
          <span class="pill matched" style="font-size: 11px; padding: 3px 9px;">✓ ${{s}}</span>
        `).join("");
      }}

      if (preview) preview.style.display = "block";
    }}

    function applyUploadedResume() {{
      if (!pendingResumeData) return;

      // Replace manual profile skills with extracted resume skills
      allProfileSkills = [...pendingResumeData.skills];
      disabledSkillSet.clear();
      updateActiveSkills();

      const nameEl = document.getElementById("candidateNameDisplay");
      const expEl = document.getElementById("candidateExpDisplay");
      const titleEl = document.getElementById("candidateTitleDisplay");
      if (nameEl) nameEl.innerText = pendingResumeData.name;
      if (expEl) expEl.innerText = pendingResumeData.exp;
      if (titleEl) titleEl.innerText = pendingResumeData.title;

      const banner = document.getElementById("uploadedResumeBanner");
      const fileNameEl = document.getElementById("uploadedFileName");
      const skillsCountEl = document.getElementById("uploadedSkillsCount");
      const activeBadge = document.getElementById("activeResumeBadge");

      if (banner) banner.style.display = "flex";
      if (fileNameEl) fileNameEl.innerText = `Active Resume: ${{pendingResumeData.fileName || 'Uploaded Resume'}} (${{pendingResumeData.name}})`;
      if (skillsCountEl) skillsCountEl.innerText = ` • Replaced manual profile with ${{pendingResumeData.skills.length}} extracted skills`;
      if (activeBadge) {{
        activeBadge.className = "active-resume-badge custom";
        activeBadge.innerText = "✨ Uploaded Profile";
      }}

      try {{
        localStorage.setItem("roshan_custom_resume", JSON.stringify(pendingResumeData));
      }} catch(e) {{}}

      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
      updatePortalLauncherLinks();

      closeResumeUploadModal();
      showToast(`🎉 Replaced manual profile with ${{pendingResumeData.name}}'s resume (${{pendingResumeData.skills.length}} skills)! All vacancies re-scored.`);
    }}

    function revertToDefaultResume() {{
      try {{
        localStorage.removeItem("roshan_custom_resume");
      }} catch(e) {{}}

      allProfileSkills = [...defaultSkills];
      disabledSkillSet.clear();
      updateActiveSkills();

      const nameEl = document.getElementById("candidateNameDisplay");
      const expEl = document.getElementById("candidateExpDisplay");
      const titleEl = document.getElementById("candidateTitleDisplay");
      if (nameEl) nameEl.innerText = "Roshan Moger";
      if (expEl) expEl.innerText = "2.5+ Years";
      if (titleEl) titleEl.innerText = "Associate Software Engineer, ExcelSoft";

      const banner = document.getElementById("uploadedResumeBanner");
      const activeBadge = document.getElementById("activeResumeBadge");
      if (banner) banner.style.display = "none";
      if (activeBadge) {{
        activeBadge.className = "active-resume-badge default";
        activeBadge.innerText = "🟢 Default Profile";
      }}

      renderSkillToggles();
      recalculateAllCompanies({{ animateScroll: false }});
      updatePortalLauncherLinks();
      showToast("↩️ Reverted to Roshan Moger's default profile & skills.");
    }}

    // Dynamically update Portal Launcher URLs to search for active resume skills
    function updatePortalLauncherLinks() {{
      const currentSkills = activeSkills.length ? activeSkills : defaultSkills;
      const topSkills = currentSkills.slice(0, 3);
      const skillQuery = encodeURIComponent(topSkills.join(" "));
      const labelStack = topSkills.slice(0, 2).join(" + ");

      const lLinkedInDubai = document.getElementById("linkLinkedInDubai");
      const lNaukriGulf = document.getElementById("linkNaukriGulf");
      const lBaytDubai = document.getElementById("linkBaytDubai");
      const lNaukri = document.getElementById("linkNaukri");
      const lLinkedIn = document.getElementById("linkLinkedIn");
      const lIndeed = document.getElementById("linkIndeedIndia");

      if (lLinkedInDubai) {{
        lLinkedInDubai.href = `https://www.linkedin.com/jobs/search/?keywords=${{skillQuery}}&location=Dubai%2C%20United%20Arab%20Emirates`;
        lLinkedInDubai.innerText = `🇦🇪 LinkedIn Dubai (2-4 Yrs • ${{labelStack}}) ↗`;
      }}
      if (lNaukriGulf) {{
        lNaukriGulf.href = `https://www.naukrigulf.com/net-developer-jobs-in-dubai`;
        lNaukriGulf.innerText = `🇦🇪 Naukrigulf Dubai (2-4 Yrs) ↗`;
      }}
      if (lBaytDubai) {{
        lBaytDubai.href = `https://www.bayt.com/en/uae/jobs/net-developer-jobs-in-dubai/`;
        lBaytDubai.innerText = `🇦🇪 Bayt Dubai (2-4 Yrs) ↗`;
      }}
      if (lNaukri) {{
        lNaukri.href = `https://www.naukri.com/react-dot-net-full-stack-jobs-in-bangalore-bengaluru?k=${{skillQuery}}&l=bangalore%2Fbengaluru&experience=2&experience=3&experience=4&jobAge=3`;
        lNaukri.innerText = `🇮🇳 Naukri India (2-4 Yrs • ${{labelStack}}) ↗`;
      }}
      if (lLinkedIn) {{
        lLinkedIn.href = `https://www.linkedin.com/jobs/search/?keywords=${{skillQuery}}&location=Bengaluru%2C%20Karnataka%2C%20India`;
        lLinkedIn.innerText = `🇮🇳 LinkedIn India (2-4 Yrs • ${{labelStack}}) ↗`;
      }}
      if (lIndeed) {{
        lIndeed.href = `https://in.indeed.com/jobs?q=${{skillQuery}}&l=Bengaluru%2C+Karnataka`;
        lIndeed.innerText = `🇮🇳 Indeed India (2-4 Yrs • ${{labelStack}}) ↗`;
      }}
    }}

    // Custom Job Vacancy Management (Add Vacancy from Any Job Board)
    function openAddJobModal() {{
      const m = document.getElementById("addJobModal");
      if (m) m.style.display = "flex";
      document.body.style.overflow = "hidden";
    }}

    function closeAddJobModal() {{
      const m = document.getElementById("addJobModal");
      if (m) m.style.display = "none";
      document.body.style.overflow = "auto";
    }}

    function submitCustomJob() {{
      const company = document.getElementById("newJobCompany").value.trim();
      const title = document.getElementById("newJobTitle").value.trim();
      const portal = document.getElementById("newJobPortal").value;
      const url = document.getElementById("newJobUrl").value.trim();
      const skillsRaw = document.getElementById("newJobSkills").value.trim();
      const location = document.getElementById("newJobLocation").value.trim() || "Bengaluru / Remote";
      const note = document.getElementById("newJobNote").value.trim() || `Added live by you from ${{portal}}`;

      if (!company || !title || !url || !skillsRaw) {{
        alert("Please fill in the required fields: Company, Title, Application URL, and Skills.");
        return;
      }}

      const skills = skillsRaw.split(/[,;]+/).map(s => s.trim()).filter(Boolean);
      const newJobId = "custom-job-" + Date.now();

      const portalColors = {{
        "Naukri": "#f97316",
        "Indeed": "#2563eb",
        "LinkedIn": "#0ea5e9",
        "Instahyre": "#8b5cf6",
        "Wellfound": "#ef4444",
        "Company Portal": "#10b981",
        "Other": "#64748b"
      }};
      const portalBadges = {{
        "Naukri": "🟠 Naukri.com",
        "Indeed": "🔵 Indeed",
        "LinkedIn": "🔷 LinkedIn",
        "Instahyre": "🟣 Instahyre",
        "Wellfound": "🔴 Wellfound",
        "Company Portal": "🟢 Company Portal",
        "Other": "🌐 Job Board"
      }};

      const newJob = {{
        id: newJobId,
        company: company,
        title: title,
        portal: portal,
        portal_badge: portalBadges[portal] || "🌐 Job Board",
        portal_color: portalColors[portal] || "#3b82f6",
        location: location,
        date: "Today",
        days_ago: 0,
        exp: "2-4 Years",
        score: "94% Match ★ NEW",
        base_score: 92,
        skills: skills,
        url: url,
        note: note
      }};

      jobsList.unshift(newJob);

      // Synthesize dynamic interview prep for the new job
      prepDatabase[newJobId] = {{
        company: company,
        role: title,
        location: location,
        experience_req: "2-4 Years",
        domain: "Technology & Web Engineering",
        domain_priorities: "Scalable architecture, API reliability, real-time data handling.",
        direct_matches: skills.filter(s => activeSkills.some(a => a.toLowerCase() === s.toLowerCase())),
        resume_gap_advice: [],
        tailored_stars: [
          {{
            theme: "High-Performance Delivery",
            title: `Optimizing Web Infrastructure (${{company}} Focus)`,
            situation: `High traffic required responsive state management and optimized queries.`,
            task: `Deliver sub-second response times and high availability.`,
            action: `Implemented caching with Redis, decoupled API contracts, and optimized React component renders.`,
            result: `Achieved 60% reduction in DB contention and stabilized client load.`,
            pitch_line: `My production experience delivering fast, resilient full-stack systems directly applies to ${{company}}'s needs.`
          }}
        ],
        technical_qa: [
          [`How do you ensure reliability for this stack at ${{company}}?`, `Implement robust TypeScript contracts, automated integration tests, and structured logging.`],
          [`How do you optimize state and data fetching?`, `Use React hooks or state management with cache invalidation to prevent redundant re-renders.`]
        ],
        system_design_scenario: `Design an End-to-End Service Architecture for ${{company}}.`,
        reverse_questions: [
          `What are the immediate engineering goals for this team at ${{company}}?`,
          `How does the team handle code reviews, deployments, and testing?`
        ]
      }};

      const container = document.getElementById("jobContainer");
      if (container) {{
        const pillsHtml = skills.map(s => `<span class="pill" onclick="filterBySkill('${{s.replace(/'/g, "\\\\'")}}')" title="Click to filter by ${{s}}">${{s}}</span>`).join("");
        
        const locLow = location.toLowerCase();
        let customLocCat = "india";
        let customLocBadge = '<span class="loc-pill loc-in">🇮🇳 India</span>';
        if (locLow.includes("dubai") || locLow.includes("uae") || locLow.includes("emirates") || locLow.includes("abu dhabi") || locLow.includes("sharjah")) {{
          customLocCat = "dubai";
          customLocBadge = '<span class="loc-pill loc-uae">🇦🇪 Dubai, UAE</span>';
        }}

        const cardDiv = document.createElement("div");
        cardDiv.className = "job-item";
        cardDiv.setAttribute("data-id", newJobId);
        cardDiv.setAttribute("data-portal", portal);
        cardDiv.setAttribute("data-location-cat", customLocCat);
        cardDiv.setAttribute("data-base", "92");
        cardDiv.setAttribute("data-days", "0");
        cardDiv.setAttribute("data-exp", "2-4 Years");
        cardDiv.innerHTML = `
          <div class="job-top">
            <div>
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                <span class="portal-badge" style="background: ${{newJob.portal_color}}22; color: ${{newJob.portal_color}}; border-color: ${{newJob.portal_color}}55;">
                  ${{newJob.portal_badge}}
                </span>
                ${{customLocBadge}}
                <span class="badge-fresh-pill today">🔥 Added Today</span>
                <span style="font-size: 13px; color: #a78bfa; font-weight: 600;">2-4 Years</span>
              </div>
              <div class="role-title">${{title}}</div>
              <div class="company-name">${{company}} &bull; <span style="color:#94a3b8; font-weight: normal;">${{location}}</span></div>
            </div>
            <div class="match-tag" id="tag-${{newJobId}}">94% Match ★ NEW</div>
          </div>
          <div class="job-meta-row">
            <span>📅 Posted: <strong>Today</strong></span>
            <span>🌐 Portal: <strong>${{portal}}</strong></span>
            <span>📍 <strong>${{location}}</strong></span>
          </div>
          <div class="pill-group" id="pills-${{newJobId}}">${{pillsHtml}}</div>
          <div class="job-note-bar">
            <span class="note-icon">💡</span>
            <span class="note-text">${{note}}</span>
          </div>
          <div class="job-button-bar">
            <button onclick="openPrepModal('${{newJobId}}')" class="btn btn-prep">🎯 Prepare Interview</button>
            <a href="${{url}}" target="_blank" class="btn btn-link" style="border-left: 2px solid ${{newJob.portal_color}};">🚀 View & Apply (${{portal}}) ↗</a>
            <button id="btn-apply-${{newJobId}}" onclick="toggleApplyJob('${{newJobId}}')" class="btn btn-apply-track">✅ Mark as Applied</button>
            <button onclick="deleteJobRole('${{newJobId}}', event)" class="btn btn-delete" title="Delete this role">🗑️ Delete</button>
          </div>
        `;
        container.prepend(cardDiv);
      }}

      try {{
        const storedCustomJobs = JSON.parse(localStorage.getItem("roshan_custom_jobs") || "[]");
        storedCustomJobs.unshift(newJob);
        localStorage.setItem("roshan_custom_jobs", JSON.stringify(storedCustomJobs));
      }} catch(e) {{}}

      document.getElementById("newJobCompany").value = "";
      document.getElementById("newJobTitle").value = "";
      document.getElementById("newJobUrl").value = "";
      document.getElementById("newJobSkills").value = "";
      document.getElementById("newJobNote").value = "";

      closeAddJobModal();
      recalculateAllCompanies({{ animateScroll: false }});
      showToast(`✨ Successfully added "${{company}} - ${{title}}"! Scored against your resume.`);
    }}

    // Clickable Job Card Pill handler
    function filterBySkill(skillName) {{
      const box = document.getElementById("filterBox");
      if (!box) return;
      if (box.value.toLowerCase() === skillName.toLowerCase()) {{
        box.value = "";
        showToast("Cleared skill filter.");
      }} else {{
        box.value = skillName;
        showToast(`🔍 Filtering jobs by skill: "${{skillName}}"`);
      }}
      filter();
    }}

    // Filter by Location
    function filterByLocation(loc) {{
      selectedLocation = loc;
      document.querySelectorAll(".location-filter-btn").forEach(btn => {{
        btn.classList.toggle("active", btn.getAttribute("onclick").includes(`'${{loc}}'`));
      }});
      filter();
    }}

    // Filter by Portal
    function filterByPortal(portal) {{
      selectedPortal = portal;
      document.querySelectorAll(".portal-filter-btn").forEach(btn => {{
        btn.classList.toggle("active", btn.getAttribute("onclick").includes(`'${{portal}}'`));
      }});
      filter();
    }}

    // Filter job list in real-time
    function filter() {{
      const q = document.getElementById("filterBox").value.toLowerCase();
      const items = document.querySelectorAll(".job-item");
      
      let countFresh = 0;
      let countAll = 0;
      let countApplied = 0;
      let visibleCount = 0;

      items.forEach(item => {{
        const jobId = item.getAttribute("data-id");
        if (deletedJobIds.has(jobId)) {{
          item.style.display = "none";
          return;
        }}
        const portal = item.getAttribute("data-portal");
        const days = parseInt(item.getAttribute("data-days") || "99", 10);
        const isApplied = appliedJobIds.includes(jobId);

        // Update button state on card
        const btn = document.getElementById("btn-apply-" + jobId);
        if (btn) {{
          if (isApplied) {{
            btn.className = "btn btn-applied-undo";
            btn.innerText = "↩️ Undo Applied";
          }} else {{
            btn.className = "btn btn-apply-track";
            btn.innerText = "✅ Mark as Applied";
          }}
        }}

        // Calculate counts
        if (isApplied) {{
          countApplied++;
        }} else {{
          countAll++;
          if (days <= 3) countFresh++;
        }}

        // Match view mode
        let matchesViewMode = false;
        if (currentViewMode === "fresh") {{
          matchesViewMode = (!isApplied && days <= 3);
        }} else if (currentViewMode === "all") {{
          matchesViewMode = !isApplied;
        }} else if (currentViewMode === "applied") {{
          matchesViewMode = isApplied;
        }}

        const matchesPortal = (selectedPortal === "all" || portal === selectedPortal);
        const locCat = item.getAttribute("data-location-cat") || "india";
        const exp = item.getAttribute("data-exp") || "";
        const matchesExp = exp.includes("2-4");
        const matchesLocation = (selectedLocation === "all" || locCat === selectedLocation);
        const text = item.innerText.toLowerCase();
        const matchesSearch = text.includes(q);

        const shouldShow = matchesViewMode && matchesPortal && matchesLocation && matchesSearch;
        item.style.display = shouldShow ? "block" : "none";
        if (shouldShow) visibleCount++;
      }});

      // Update count badges
      const bFresh = document.getElementById("countFreshBadge");
      const bAll = document.getElementById("countAllBadge");
      const bApplied = document.getElementById("countAppliedBadge");
      if (bFresh) bFresh.innerText = countFresh;
      if (bAll) bAll.innerText = countAll;
      if (bApplied) bApplied.innerText = countApplied;

      // Update empty state banner
      const emptyMsg = document.getElementById("emptyStateMsg");
      if (emptyMsg) {{
        emptyMsg.style.display = visibleCount === 0 ? "block" : "none";
        const emptyTitle = document.getElementById("emptyTitle");
        const emptyDesc = document.getElementById("emptyDesc");
        if (currentViewMode === "applied" && countApplied === 0) {{
          emptyTitle.innerText = "No Applied Roles Yet";
          emptyDesc.innerText = "Click '✅ Mark as Applied' on any vacancy to track your submitted applications here and remove them from active search.";
        }} else if (currentViewMode === "fresh" && countFresh === 0) {{
          emptyTitle.innerText = "All Fresh Roles Applied or None in Last 3 Days";
          emptyDesc.innerText = "Switch to '📂 All Active Roles' to see all enterprise openings or click Refresh.";
        }} else {{
          emptyTitle.innerText = "No roles match your search or filter";
          emptyDesc.innerText = "Try clearing your search query or selecting 'All Portals'.";
        }}
      }}

      // Update stat role count
      const statRoleCount = document.getElementById("statRoleCount");
      if (statRoleCount) {{
        statRoleCount.innerText = currentViewMode === "applied" ? countApplied : (currentViewMode === "fresh" ? countFresh : countAll);
      }}
    }}

    // Dynamic Recalculation Engine
    function recalculateAllCompanies(options = {{}}) {{
      const isManualRefresh = !options || options.animateScroll !== false;
      const icon = document.getElementById("recalcIcon");

      if (isManualRefresh) {{
        if (icon) {{
          icon.classList.add("spinning");
          setTimeout(() => icon.classList.remove("spinning"), 600);
        }}
        // On manual refresh button click, default to fresh (Max 3 Days) mode
        currentViewMode = "fresh";
        const bFresh = document.getElementById("viewBtnFresh");
        const bAll = document.getElementById("viewBtnAll");
        const bApplied = document.getElementById("viewBtnApplied");
        if (bFresh) bFresh.classList.add("active");
        if (bAll) bAll.classList.remove("active");
        if (bApplied) bApplied.classList.remove("active");
      }}

      // Ensure activeSkills is synced with enabled pills
      updateActiveSkills();
      const activeLower = activeSkills.map(s => s.toLowerCase());

      let scores = [];

      jobsList.forEach(job => {{
        const jobReqs = job.skills.map(s => s.toLowerCase());

        let directMatches = 0;
        let matchedSkillNames = [];

        job.skills.forEach(skill => {{
          const sLow = skill.toLowerCase();
          const isMatched = activeLower.some(act => act.includes(sLow) || sLow.includes(act));
          if (isMatched) {{
            directMatches++;
            matchedSkillNames.push(skill);
          }}
        }});

        // Overlap ratio (40%)
        const skillRatio = directMatches / Math.max(job.skills.length, 1);
        
        // Domain & Tech Synergy Bonus (30%)
        let bonus = 0;
        const jobStr = (job.title + " " + job.skills.join(" ")).toLowerCase();
        if (jobStr.includes("c#") && activeLower.some(s => s.includes("c#"))) bonus += 0.04;
        if (jobStr.includes(".net") && activeLower.some(s => s.includes(".net"))) bonus += 0.04;
        if (jobStr.includes("websocket") && activeLower.some(s => s.includes("websocket"))) bonus += 0.04;
        if (jobStr.includes("redis") && activeLower.some(s => s.includes("redis"))) bonus += 0.04;
        if (jobStr.includes("aws") && activeLower.some(s => s.includes("aws"))) bonus += 0.03;
        if (jobStr.includes("next") && activeLower.some(s => s.includes("next"))) bonus += 0.06;

        // Base computation: minimum 72%, maximum 98%
        let calculatedScore = Math.round(72 + (skillRatio * 20) + (bonus * 100));
        if (calculatedScore > 98) calculatedScore = 98;
        if (calculatedScore < 70) calculatedScore = 70;

        job.calculatedScore = calculatedScore;
        scores.push(calculatedScore);

        // Update tag in DOM
        const tag = document.getElementById("tag-" + job.id);
        if (tag) {{
          const isTailored = job.id === "quest-global";
          tag.innerText = calculatedScore + "% Match" + (isTailored ? " ★ TAILORED" : "");
          tag.style.background = calculatedScore >= 90 ? "rgba(16, 185, 129, 0.25)" : "rgba(59, 130, 246, 0.2)";
          tag.style.color = calculatedScore >= 90 ? "#34d399" : "#60a5fa";
        }}

        // Update skill pills matched highlights
        const pillBox = document.getElementById("pills-" + job.id);
        if (pillBox) {{
          const pills = pillBox.querySelectorAll(".pill");
          pills.forEach(p => {{
            const pText = p.innerText.toLowerCase();
            const matched = matchedSkillNames.some(m => m.toLowerCase() === pText);
            if (matched) p.classList.add("matched");
            else p.classList.remove("matched");
          }});
        }}

        // Update prep database direct matches
        if (prepDatabase[job.id]) {{
          prepDatabase[job.id].direct_matches = matchedSkillNames;
          prepDatabase[job.id].skills_to_review = job.skills.filter(s => !matchedSkillNames.includes(s));
        }}
      }});

      // Re-sort DOM job cards in container from highest match to lowest
      const container = document.getElementById("jobContainer");
      if (container) {{
        const items = Array.from(container.children);
        items.sort((a, b) => {{
          const idA = a.getAttribute("data-id");
          const idB = b.getAttribute("data-id");
          const jobA = jobsList.find(j => j.id === idA);
          const jobB = jobsList.find(j => j.id === idB);
          return (jobB ? jobB.calculatedScore : 0) - (jobA ? jobA.calculatedScore : 0);
        }});
        items.forEach(el => container.appendChild(el));
      }}

      // Update Header Stats
      const maxScore = scores.length ? Math.max(...scores) : 0;
      const avgScore = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
      const topEl = document.getElementById("statTopScore");
      const avgEl = document.getElementById("statAvgScore");
      if (topEl) topEl.innerText = maxScore + "%";
      if (avgEl) avgEl.innerText = avgScore + "%";

      filter();
      updatePortalLauncherLinks();
      if (isManualRefresh) {{
        showToast(`🔄 Refreshed! Showing fresh applications from the last 3 days matching your resume (Top: ${{maxScore}}%).`);
      }}
    }}

    function showToast(msg) {{
      const t = document.getElementById("toastNotification");
      document.getElementById("toastMessage").innerText = msg;
      t.style.display = "flex";
      setTimeout(() => {{
        t.style.display = "none";
      }}, 3200);
    }}

    // Recalculate Job Freshness & Dynamic Relative Dates (In-Browser Calendar Sync)
    function recalculateJobFreshnessAndDates() {{
      const now = new Date();
      const currentYear = now.getFullYear();
      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate());

      const items = document.querySelectorAll(".job-item");
      items.forEach(item => {{
        const jobId = item.getAttribute("data-id");
        const job = jobsList.find(j => j.id === jobId);
        if (!job || !job.date) return;

        let jobDate;
        if (job.date.toLowerCase() === "today") {{
          jobDate = todayMidnight;
        }} else {{
          jobDate = new Date(job.date);
          if (isNaN(jobDate.getTime())) {{
            jobDate = new Date(job.date + " " + currentYear);
          }}
        }}

        if (!isNaN(jobDate.getTime())) {{
          const jobMidnight = new Date(jobDate.getFullYear(), jobDate.getMonth(), jobDate.getDate());
          const diffMs = todayMidnight - jobMidnight;
          let daysAgo = Math.floor(diffMs / (1000 * 60 * 60 * 24));
          if (daysAgo < 0) daysAgo = 0;

          item.setAttribute("data-days", daysAgo);
          job.days_ago = daysAgo;

          const pill = item.querySelector(".badge-fresh-pill, .badge-older-pill");
          if (pill) {{
            const jobMonthDay = `${{monthNames[jobDate.getMonth()]}} ${{String(jobDate.getDate()).padStart(2, '0')}}`;
            if (daysAgo === 0) {{
              pill.className = "badge-fresh-pill today";
              pill.innerText = `🔥 Posted Today (${{jobMonthDay}})`;
            }} else if (daysAgo === 1) {{
              pill.className = "badge-fresh-pill";
              pill.innerText = `🔥 1d ago (${{jobMonthDay}})`;
            }} else if (daysAgo === 2) {{
              pill.className = "badge-fresh-pill";
              pill.innerText = `🔥 2d ago (${{jobMonthDay}})`;
            }} else if (daysAgo === 3) {{
              pill.className = "badge-fresh-pill";
              pill.innerText = `🔥 3d ago (${{jobMonthDay}})`;
            }} else {{
              pill.className = "badge-older-pill";
              pill.innerText = `📅 ${{jobMonthDay}}, ${{jobDate.getFullYear()}}`;
            }}
          }}
        }}
      }});
    }}

    // Top Button: Trigger Daily Live Multi-Portal Search & Recalculate
    async function triggerDailyLiveSearch(options = {{}}) {{
      if (window.location.protocol === "file:") {{
        showToast("⚠️ Browser security blocks server requests from file://. Opening live server...");
        window.location.href = "http://127.0.0.1:5000/reports/application-dashboard.html";
        return;
      }}
      const isAuto = options && options.auto === true;
      const icon = document.getElementById("topRefreshIcon");
      const btn = document.getElementById("btnTopDailySearch");
      const scanBar = document.getElementById("liveScanFeedbackBar");
      const scanTitle = document.getElementById("scanBarTitle");
      const scanDesc = document.getElementById("scanBarDesc");
      const scanTime = document.getElementById("scanBarTime");

      if (icon) icon.classList.add("spinning");
      if (btn) btn.disabled = true;

      if (scanBar) {{
        scanBar.style.display = "flex";
        if (scanTitle) scanTitle.innerText = isAuto ? "🌅 Auto-syncing today's fresh .NET & React openings..." : "Scanning live job portals for today's new openings...";
        if (scanDesc) scanDesc.innerText = "Checking LinkedIn, freehire ATS, Naukri, Indeed, and Company Career Portals...";
        if (scanTime) scanTime.innerText = new Date().toLocaleTimeString();
      }}

      showToast(isAuto ? "🌅 New day detected! Auto-syncing today's fresh .NET & React jobs..." : "🌐 Scanning live job portals across the web for today's openings...");

      // 1. Try local live server API
      let serverOnline = false;
      try {{
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 90000);
        const refreshUrl = window.location.origin.includes("5000") ? "/api/refresh" : "http://127.0.0.1:5000/api/refresh";
        const res = await fetch(refreshUrl, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          signal: controller.signal
        }});
        clearTimeout(timeoutId);

        if (res.ok) {{
          const data = await res.json();
          serverOnline = true;
          if (scanTitle) scanTitle.innerText = "✅ Daily Multi-Portal Search Complete!";
          if (scanDesc) scanDesc.innerText = `${{data.message}} (Synced at ${{data.timestamp}})`;
          showToast(`🎉 Scan Complete! Refreshed with latest jobs for ${{data.today_formatted}}.`);
          setTimeout(() => {{
            window.location.reload();
          }}, 900);
          return;
        }}
      }} catch (e) {{
        console.log("Local live_server.py not responding; executing instant in-browser calendar & resume sync.");
      }}

      // 2. Client-side instant date, freshness, and resume fit recalculation
      recalculateJobFreshnessAndDates();
      recalculateAllCompanies({{ animateScroll: false }});

      if (icon) icon.classList.remove("spinning");
      if (btn) btn.disabled = false;

      if (scanBar) {{
        if (scanTitle) scanTitle.innerText = "⚡ In-Browser Daily Sync Complete!";
        const todayFormatted = new Date().toLocaleDateString(undefined, {{ month: 'short', day: 'numeric', year: 'numeric' }});
        if (scanDesc) scanDesc.innerText = `All dates and freshness tabs dynamically recalculated for ${{todayFormatted}}! (To run background web scraping, double-click run_live_dashboard.bat)`;
        if (scanTime) scanTime.innerText = new Date().toLocaleTimeString();
      }}

      showToast("⚡ All vacancy dates, 3-day filters, and resume scores updated for today!");
    }}

    // Top Button: Purge All Stored Jobs & Trigger 100% Fresh Daily Crawl
    async function triggerPurgeAndFreshCrawl() {{
      if (window.location.protocol === "file:") {{
        showToast("⚠️ Browser security blocks server requests from file://. Opening live server...");
        window.location.href = "http://127.0.0.1:5000/reports/application-dashboard.html";
        return;
      }}
      if (!confirm("Are you sure you want to clear all previous stored jobs and run a 100% fresh crawl for today?")) {{
        return;
      }}
      const icon = document.getElementById("purgeRefreshIcon");
      const btn = document.getElementById("btnPurgeFreshCrawl");
      const scanBar = document.getElementById("liveScanFeedbackBar");
      const scanTitle = document.getElementById("scanBarTitle");
      const scanDesc = document.getElementById("scanBarDesc");
      const scanTime = document.getElementById("scanBarTime");

      if (icon) icon.classList.add("spinning");
      if (btn) btn.disabled = true;

      if (scanBar) {{
        scanBar.style.display = "flex";
        if (scanTitle) scanTitle.innerText = "🧹 Clearing old jobs & running fresh crawl for today...";
        if (scanDesc) scanDesc.innerText = "Purging previous records and querying live LinkedIn & ATS aggregators...";
        if (scanTime) scanTime.innerText = new Date().toLocaleTimeString();
      }}

      showToast("🧹 Clearing old jobs and launching 100% fresh live crawl...");

      try {{
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000);
        const refreshUrl = window.location.origin.includes("5000") ? "/api/refresh?purge=true" : "http://127.0.0.1:5000/api/refresh?purge=true";
        const res = await fetch(refreshUrl, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          signal: controller.signal
        }});
        clearTimeout(timeoutId);

        if (res.ok) {{
          const data = await res.json();
          if (scanTitle) scanTitle.innerText = "✅ Fresh Multi-Portal Crawl Complete!";
          if (scanDesc) scanDesc.innerText = `${{data.message}} (Clean crawl at ${{data.timestamp}})`;
          showToast(`🎉 Clean crawl complete! Loaded ${{data.total_jobs}} fresh jobs for ${{data.today_formatted}}.`);
          setTimeout(() => {{
            window.location.reload();
          }}, 900);
          return;
        }}
      }} catch (e) {{
        console.log("Error during purge refresh:", e);
        showToast("⚠️ Could not contact server. Run run_live_dashboard.bat to enable background live crawling.");
      }}

      if (icon) icon.classList.remove("spinning");
      if (btn) btn.disabled = false;
    }}

    // Generate Tailored Resume On-The-Spot for any specific company
    async function generateTailoredResumeOnSpot(jobId, btn) {{
      if (window.location.protocol === "file:") {{
        showToast("⚠️ Browser security blocks server requests from file://. Opening live server...");
        window.location.href = "http://127.0.0.1:5000/reports/application-dashboard.html";
        return;
      }}
      if (!btn) btn = document.getElementById("btn-tailor-" + jobId);
      const originalHtml = btn ? btn.innerHTML : "✨ Tailor Resume (On-Spot)";
      if (btn) {{
        btn.disabled = true;
        btn.innerHTML = "⏳ Compiling LaTeX CV...";
        btn.style.opacity = "0.85";
      }}

      showToast("⚙️ Synthesizing role requirements & compiling tailored ModernCV PDF...");

      try {{
        const tailorUrl = window.location.origin.includes("5000") ? "/api/tailor-resume" : "http://127.0.0.1:5000/api/tailor-resume";
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000);

        const res = await fetch(tailorUrl, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ id: jobId }}),
          signal: controller.signal
        }});
        clearTimeout(timeoutId);

        if (res.ok) {{
          const data = await res.json();
          const pdfUrl = data.pdf_url || ("/cv/main_" + jobId.replace(/[^a-zA-Z0-9]+/g, "_") + ".pdf");
          showToast("🎉 Tailored Resume generated on the spot! Opening PDF...");

          if (btn) {{
            btn.disabled = false;
            btn.style.opacity = "1";
            // Replace button with permanent PDF link
            const a = document.createElement("a");
            a.href = pdfUrl;
            a.target = "_blank";
            a.className = "btn btn-cv";
            a.innerHTML = "📄 View Tailored CV (PDF) ↗";
            btn.parentNode.replaceChild(a, btn);
          }}

          // Open the compiled PDF in a new tab
          window.open(pdfUrl, "_blank");
          return;
        }} else {{
          throw new Error("Server returned " + res.status);
        }}
      }} catch (err) {{
        console.error("Tailor resume failed:", err);
        showToast("⚠️ Could not reach server. Run run_live_dashboard.bat to enable on-spot LaTeX compilation.");
        if (btn) {{
          btn.disabled = false;
          btn.innerHTML = originalHtml;
          btn.style.opacity = "1";
        }}
      }}
    }}

    // Switch tabs inside prep modal
    function switchTab(tabId) {{
      document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
      
      const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick").includes(tabId));
      if (activeBtn) activeBtn.classList.add("active");
      
      const targetPane = document.getElementById(tabId);
      if (targetPane) targetPane.classList.add("active");
    }}

    // Open Prep Modal for any role in the list
    function openPrepModal(jobId) {{
      const prep = prepDatabase[jobId];
      if (!prep) return;
      currentPrepData = prep;
      renderPrepModal(prep);
    }}

    // Render data into the modal elements
    function renderPrepModal(prep) {{
      document.getElementById("modalTitle").innerText = "🎯 " + prep.company + " - " + prep.role;
      document.getElementById("modalSub").innerText = "Domain: " + prep.domain + " | " + prep.location + " | Target: " + prep.experience_req;
      document.getElementById("modalFooterNote").innerText = "Synthesized for Roshan Moger | " + prep.company;

      // Direct matches
      const matchContainer = document.getElementById("directMatchesList");
      matchContainer.innerHTML = "";
      prep.direct_matches.forEach(m => {{
        const span = document.createElement("span");
        span.className = "pill";
        span.style.background = "rgba(16, 185, 129, 0.2)";
        span.style.color = "#34d399";
        span.style.borderColor = "rgba(16, 185, 129, 0.4)";
        span.style.fontSize = "12px";
        span.innerText = "✓ " + m;
        matchContainer.appendChild(span);
      }});

      // Gap Advice
      const gapContainer = document.getElementById("gapAdviceList");
      gapContainer.innerHTML = "";
      if (prep.resume_gap_advice && prep.resume_gap_advice.length > 0) {{
        prep.resume_gap_advice.forEach(g => {{
          const div = document.createElement("div");
          div.className = "gap-card";
          div.innerHTML = `
            <div style="font-weight: 700; color: #f87171; margin-bottom: 4px;">⚡ Target Requirement: ${{g.skill}}</div>
            <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 4px;"><strong>Your Resume Bridge:</strong> ${{g.resume_bridge}}</div>
            <div style="font-size: 13px; color: #93c5fd;"><strong>What to Prepare Before Interview:</strong> ${{g.what_to_prepare}}</div>
          `;
          gapContainer.appendChild(div);
        }});
      }} else {{
        gapContainer.innerHTML = "<div style='color: #34d399; font-size: 13px;'>✓ 100% direct alignment with your active resume skills! No major tech gaps identified.</div>";
      }}

      // STAR Stories
      const starContainer = document.getElementById("starStoriesList");
      starContainer.innerHTML = "";
      prep.tailored_stars.forEach(s => {{
        const div = document.createElement("div");
        div.className = "star-card";
        div.innerHTML = `
          <div class="star-title">${{s.title}}</div>
          <div class="star-row"><span class="star-lbl">S:</span> ${{s.situation}}</div>
          <div class="star-row"><span class="star-lbl">T:</span> ${{s.task}}</div>
          <div class="star-row"><span class="star-lbl">A:</span> ${{s.action}}</div>
          <div class="star-row"><span class="star-lbl">R:</span> ${{s.result}}</div>
          <div class="pitch-box">💡 <strong>Winning Pitch Line:</strong> ${{s.pitch_line}}</div>
        `;
        starContainer.appendChild(div);
      }});

      // Technical Q&A
      const qaContainer = document.getElementById("qaList");
      qaContainer.innerHTML = "";
      prep.technical_qa.forEach((qa, idx) => {{
        const div = document.createElement("div");
        div.className = "qa-card";
        div.innerHTML = `
          <div class="qa-q">Q${{idx + 1}}: ${{qa[0]}}</div>
          <div class="qa-a"><strong>Model Answer (Roshan's 2+ Yrs Perspective):</strong><br>${{qa[1]}}</div>
        `;
        qaContainer.appendChild(div);
      }});

      // System Design
      document.getElementById("designTitle").innerText = "Challenge: " + prep.system_design_scenario;

      // Reverse Questions
      const revContainer = document.getElementById("reverseQuestionsList");
      revContainer.innerHTML = "";
      prep.reverse_questions.forEach(q => {{
        const p = document.createElement("p");
        p.style.marginBottom = "8px";
        p.innerHTML = `<span style="color: #38bdf8;">&bull;</span> <em>"${{q}}"</em>`;
        revContainer.appendChild(p);
      }});

      // Show modal & default to first tab
      switchTab('tab-fit');
      document.getElementById("prepModal").style.display = "flex";
    }}

    function closePrepModal() {{
      document.getElementById("prepModal").style.display = "none";
    }}

    // Close on escape key or clicking backdrop
    window.onclick = function(event) {{
      const modal = document.getElementById("prepModal");
      if (event.target === modal) {{
        modal.style.display = "none";
      }}
    }};
    window.onkeydown = function(e) {{
      if (e.key === "Escape") closePrepModal();
    }};

    // Dynamic Generator for ANY custom company
    function generateCustomPrep() {{
      const company = document.getElementById("customCompany").value.trim();
      const role = document.getElementById("customRole").value.trim() || "Full Stack Developer";
      const rawSkills = document.getElementById("customSkills").value.trim();

      if (!company) {{
        alert("Please enter a company name (e.g. Swiggy, PhonePe, Microsoft).");
        return;
      }}

      const skills = rawSkills ? rawSkills.split(/[,\\s]+/).filter(Boolean) : ["React", "TypeScript", "Node.js", "REST"];
      
      let domain = "Enterprise & Cloud Services";
      let priorities = "Clean architecture, high-availability APIs, distributed caching, secure auth.";
      let qa = [
        ["How do you optimize API latency and database bottlenecks in high-traffic applications?", "Implement Redis distributed caching with cache-aside pattern, analyze slow SQL query plans, and add targeted indexes on foreign keys and filter columns."],
        ["How do you manage complex asynchronous state in React?", "Utilize Redux Toolkit or custom React hooks with clean lifecycle management, avoiding redundant re-renders via useMemo and useCallback."],
        ["How do you secure web applications against common vulnerabilities?", "Enforce JWT authentication with short TTLs and secure HTTP-only refresh tokens, implement route-level RBAC, sanitize inputs to prevent XSS/SQLi, and configure CORS policies."]
      ];
      let designScenario = "Design a Scalable User & Event Processing Platform with Real-Time Notifications.";

      const compLow = company.toLowerCase() + " " + role.toLowerCase();
      if (compLow.includes("pay") || compLow.includes("bank") || compLow.includes("credit") || compLow.includes("fin")) {{
        domain = "FinTech & Financial Services";
        priorities = "Idempotent payment transactions, strict audit logging, high-security state handling.";
        qa = [
          ["How do you guarantee idempotency in financial transactions?", "Require client-generated Idempotency-Key headers and check atomically in Redis before running business logic."],
          ["How do you prevent double-spending in high-concurrency balance updates?", "Use optimistic concurrency control with row versioning or Redis distributed locks (Redlock)."],
          ["Where should sensitive auth tokens be stored in frontend apps?", "In HTTP-only Secure SameSite cookies, never in localStorage (XSS exposure)."]
        ];
        designScenario = "Design an Idempotent Real-Time Payment & Balance Notification Service.";
      }} else if (compLow.includes("shop") || compLow.includes("cart") || compLow.includes("store") || compLow.includes("commerce") || compLow.includes("zepto") || compLow.includes("blinkit") || compLow.includes("swiggy")) {{
        domain = "E-Commerce & Quick Commerce";
        priorities = "High-concurrency flash sales, cart checkout persistence, sub-second inventory decrement.";
        qa = [
          ["How do you handle inventory reservation during high-concurrency sales?", "Use Redis atomic DECR operations to hold stock before writing orders to SQL."],
          ["How do you optimize Core Web Vitals for product browsing?", "Preload LCP images via CDN, set explicit dimensions to prevent CLS, and code-split bundles using React.lazy."],
          ["How do you synchronize cart state across multiple tabs?", "Use Redux synchronized with BroadcastChannel API or localStorage events."]
        ];
        designScenario = "Design a High-Concurrency Flash Sale Inventory & Order Processing Pipeline.";
      }}

      // Check matches against active resume skills
      const directMatches = [];
      const gaps = [];
      skills.forEach(s => {{
        const matched = activeSkills.find(r => r.toLowerCase().includes(s.toLowerCase()) || s.toLowerCase().includes(r.toLowerCase()));
        if (matched) directMatches.push(matched);
        else gaps.push(s);
      }});

      const gapAdvice = gaps.map(g => ({{
        skill: g,
        resume_bridge: "Your 2.5+ years full-stack foundation in React, C#/.NET Core, and AI integration provides fast ramp-up capability.",
        what_to_prepare: "Review core API design, standard architecture patterns, and common lifecycle methods for " + g + "."
      }}));

      const customPrep = {{
        company: company,
        role: role,
        location: "Bengaluru, India / Remote",
        experience_req: "1-3 Years (Associate / SDE 1)",
        domain: domain,
        domain_priorities: priorities,
        direct_matches: directMatches.length ? directMatches : ["React.js", "TypeScript", "ASP.NET Core", "REST APIs", "AWS"],
        resume_gap_advice: gapAdvice,
        tailored_stars: [
          {{
            theme: "Backend Caching",
            title: "Redis Distributed Caching to Eliminate DB Bottlenecks (" + company + " Focus)",
            situation: "On enterprise platforms, peak query traffic caused heavy database contention and latency spikes.",
            task: "Cut database roundtrips by >60% and ensure sub-150ms API response times.",
            action: "Designed a Redis distributed caching layer with TTL expiration and reactive invalidation.",
            result: "Drastically reduced database load and stabilized API throughput under concurrent load.",
            pitch_line: "At ExcelSoft, I implemented Redis caching to handle massive traffic spikes, which directly translates to " + company + "'s scalability needs."
          }},
          {{
            theme: "AI Integration & MCP",
            title: "Model Context Protocol (MCP) Server & LLM Integration (" + company + " Focus)",
            situation: "Bridging internal SaaS business logic and workflows with LLMs securely without exposing raw database tables.",
            task: "Expose SaaS platform workflows as standardized AI tools and build an in-product conversational assistant.",
            action: "Built an MCP server using .NET and integrated Google Gemini (via AWS Bedrock) with streaming response telemetry.",
            result: "Delivered automated assessment querying and report summarization, boosting operational efficiency.",
            pitch_line: "I engineered an MCP server in .NET and integrated Google Gemini via AWS Bedrock, bringing production AI capabilities to " + company + "."
          }},
          {{
            theme: "Real-Time Telemetry",
            title: "Sub-Second Live Data Streaming with WebSockets (" + company + " Focus)",
            situation: "Client applications required real-time state synchronization without constant HTTP polling.",
            task: "Build a responsive bi-directional event stream between React and backend microservices.",
            action: "Implemented WebSocket connection managers with auto-reconnect backoff and custom React hooks.",
            result: "Achieved sub-second alert broadcasts while eliminating thousands of redundant polling requests.",
            pitch_line: "My experience building real-time WebSocket pipelines enables me to implement instant, reliable user interactions for " + company + "."
          }}
        ],
        technical_qa: qa,
        system_design_scenario: designScenario,
        reverse_questions: [
          "What does the engineering architecture look like at " + company + " for this team?",
          "What is the biggest technical challenge or scaling goal this team is looking to solve in the next 6 months?",
          "How does " + company + " approach testing, code reviews, and CI/CD releases?",
          "What does mentorship and growth look like for an engineer with 2.5+ years of experience coming into this role?"
        ]
      }};

      currentPrepData = customPrep;
      renderPrepModal(customPrep);
    }}

    // Copy guide to clipboard as markdown
    function copyGuideToClipboard() {{
      if (!currentPrepData) return;
      const md = buildMarkdownText(currentPrepData);
      navigator.clipboard.writeText(md).then(() => {{
        alert("✅ Interview Preparation Guide copied to clipboard as Markdown!");
      }}).catch(err => {{
        alert("Could not copy automatically. You can download the .md file instead.");
      }});
    }}

    // Download guide as .md file
    function downloadGuideMarkdown() {{
      if (!currentPrepData) return;
      const md = buildMarkdownText(currentPrepData);
      const blob = new Blob([md], {{ type: "text/markdown;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${{currentPrepData.company.replace(/\\s+/g, "_")}}_Interview_Prep.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}

    function buildMarkdownText(p) {{
      let t = `# 🎯 Dynamic Interview Preparation Guide: ${{p.company}}\\n`;
      t += `### Role: ${{p.role}} | Target Level: ${{p.experience_req}}\\n`;
      t += `**Candidate:** Roshan Moger (2.5+ Years Full Stack Experience)\\n`;
      t += `**Domain:** ${{p.domain}} | Focus: ${{p.domain_priorities}}\\n\\n---\\n\\n`;
      t += `## 1. Resume Fit & Matches\\n`;
      t += `### Direct Matches:\\n` + p.direct_matches.map(m => `- **${{m}}** (Production-proven)`).join("\\n") + "\\n\\n";
      if (p.resume_gap_advice && p.resume_gap_advice.length) {{
        t += `### Gaps & Areas to Brush Up:\\n` + p.resume_gap_advice.map(g => `- **${{g.skill}}**: ${{g.what_to_prepare}} (Bridge: ${{g.resume_bridge}})`).join("\\n") + "\\n\\n";
      }}
      t += `---\\n\\n## 2. Tailored STAR Stories\\n`;
      t += p.tailored_stars.map(s => `### ${{s.title}}\\n- **Situation:** ${{s.situation}}\\n- **Task:** ${{s.task}}\\n- **Action:** ${{s.action}}\\n- **Result:** ${{s.result}}\\n> 💡 Pitch: ${{s.pitch_line}}\\n`).join("\\n");
      t += `---\\n\\n## 3. High-Probability Technical Q&A\\n`;
      t += p.technical_qa.map((qa, i) => `### Q${{i+1}}: ${{qa[0]}}\\n**Answer:** ${{qa[1]}}\\n`).join("\\n");
      t += `---\\n\\n## 4. System Design Challenge\\n**Challenge:** ${{p.system_design_scenario}}\\n\\n`;
      t += `---\\n\\n## 5. Questions to Ask the Interviewer\\n` + p.reverse_questions.map(q => `- "${{q}}"`).join("\\n") + "\\n";
      return t;
    }}

    // Roadmap Modal Operations
    function openRoadmapModal() {{
      renderRoadmapTabs();
      renderRoadmapPhase(activePhaseNum);
      const modal = document.getElementById("roadmapModal");
      modal.style.display = "flex";
      document.body.style.overflow = "hidden";
    }}

    function closeRoadmapModal() {{
      const modal = document.getElementById("roadmapModal");
      modal.style.display = "none";
      document.body.style.overflow = "auto";
    }}

    function renderRoadmapTabs() {{
      const container = document.getElementById("roadmapTabs");
      container.innerHTML = roadmapPhases.map(p => `
        <button class="phase-tab-btn ${{p.phase_num === activePhaseNum ? 'active' : ''}}" onclick="switchRoadmapPhase(${{p.phase_num}})">
          Phase ${{p.phase_num}}: ${{p.title.split('&')[0].trim()}}
        </button>
      `).join("");
    }}

    function switchRoadmapPhase(num) {{
      activePhaseNum = num;
      renderRoadmapTabs();
      renderRoadmapPhase(num);
    }}

    function toggleRoadmapCheck(phaseNum, taskIdx) {{
      const key = `roadmap_p${{phaseNum}}_t${{taskIdx}}`;
      const cur = localStorage.getItem(key) === "true";
      localStorage.setItem(key, (!cur).toString());
      renderRoadmapPhase(phaseNum);
    }}

    function renderRoadmapPhase(num) {{
      const phase = roadmapPhases.find(p => p.phase_num === num) || roadmapPhases[0];
      const body = document.getElementById("roadmapModalBody");

      let completedCount = 0;
      phase.must_learn.forEach((_, idx) => {{
        if (localStorage.getItem(`roadmap_p${{phase.phase_num}}_t${{idx}}`) === "true") {{
          completedCount++;
        }}
      }});
      const progressPercent = Math.round((completedCount / phase.must_learn.length) * 100);

      let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <div>
            <div style="font-size: 18px; font-weight: 800; color: #f472b6;">
              Phase ${{phase.phase_num}}: ${{phase.title}}
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 2px;">
              ${{phase.subtitle}} &bull; <span style="color: #38bdf8; font-weight: 600;">⏱️ ${{phase.est_hours}}</span>
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 10px; background: #1e293b; padding: 6px 14px; border-radius: 8px; border: 1px solid #334155;">
            <div style="font-size: 12px; color: #cbd5e1; font-weight: 600;">Phase Progress:</div>
            <div style="width: 80px; height: 8px; background: #334155; border-radius: 4px; overflow: hidden;">
              <div style="width: ${{progressPercent}}%; height: 100%; background: #ec4899; transition: width 0.3s;"></div>
            </div>
            <div style="font-size: 12px; font-weight: 700; color: #f472b6;">${{progressPercent}}%</div>
          </div>
        </div>

        <div class="skip-box">
          <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #34d399; margin-bottom: 4px; font-size: 13.5px;">
            <span>⚡ What You Already Have Proven & Can SKIP:</span>
          </div>
          <p style="font-size: 13px; color: #a7f3d0; margin-bottom: 4px;">${{phase.skip_advice}}</p>
          <div style="font-size: 12px; color: #94a3b8;"><strong>Resume Baseline:</strong> ${{phase.candidate_baseline}}</div>
        </div>

        <div class="prep-section">
          <div class="prep-section-title" style="color: #ec4899;">
            <span>🎯 High-Yield Topics to Master (Click checkbox to track completion):</span>
          </div>
          <div>
            ${{phase.must_learn.map((item, idx) => {{
              const checked = localStorage.getItem(`roadmap_p${{phase.phase_num}}_t${{idx}}`) === "true";
              return `
                <div class="checklist-item" style="${{checked ? 'opacity: 0.6; border-color: #10b981;' : ''}}">
                  <input type="checkbox" ${{checked ? 'checked' : ''}} onchange="toggleRoadmapCheck(${{phase.phase_num}}, ${{idx}})">
                  <div style="font-size: 13.5px; color: ${{checked ? '#94a3b8' : '#e2e8f0'}}; ${{checked ? 'text-decoration: line-through;' : ''}}">
                    ${{item}}
                  </div>
                </div>
              `;
            }}).join("")}}
          </div>
        </div>

        <div class="prep-section">
          <div class="prep-section-title" style="color: #a78bfa;">
            <span>📚 Curated Free Study Materials, Documentation & Repos:</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px;">
            ${{phase.study_materials.map(mat => {{
              let badgeClass = "badge-docs";
              if (mat.type.includes("Repo")) badgeClass = "badge-repo";
              else if (mat.type.includes("Course")) badgeClass = "badge-course";
              else if (mat.type.includes("Video")) badgeClass = "badge-video";
              else if (mat.type.includes("Guide")) badgeClass = "badge-guide";

              return `
                <div class="study-material-card">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                    <span class="material-badge ${{badgeClass}}">${{mat.type}}</span>
                    <a href="${{mat.url}}" target="_blank" class="btn" style="padding: 3px 10px; font-size: 11px; background: #3b82f6; text-decoration: none;">Open ↗</a>
                  </div>
                  <div style="font-size: 14px; font-weight: 700; color: #fff;">${{mat.name}}</div>
                  <div style="font-size: 12.5px; color: #94a3b8; line-height: 1.5;">${{mat.desc}}</div>
                </div>
              `;
            }}).join("")}}
          </div>
        </div>

        <div class="pitch-box" style="margin-top: 14px; background: rgba(139, 92, 246, 0.12); border-left-color: #8b5cf6; color: #c4b5fd;">
          <strong>🎙️ How to Pitch This in Interviews (SDE 2 Bar):</strong><br>
          <span style="font-size: 13px; font-style: normal; color: #e2e8f0; margin-top: 4px; display: inline-block;">
            ${{phase.interview_talking_point}}
          </span>
        </div>
      `;

      body.innerHTML = html;
    }}

    function copyRoadmapMarkdown() {{
      navigator.clipboard.writeText(roadmapMarkdownRaw).then(() => {{
        alert("🗺️ Full Stack Roadmap copied to clipboard as Markdown!");
      }}).catch(() => {{
        alert("Could not copy automatically. You can download the .md file directly.");
      }});
    }}

    function downloadRoadmapMarkdown() {{
      const blob = new Blob([roadmapMarkdownRaw], {{ type: "text/markdown;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Roshan_Moger_FullStack_Roadmap.md";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}

    // Initial render on load
    window.addEventListener("DOMContentLoaded", () => {{
      // 0. Automatic Live Server Detection & Redirection from file:// to http://127.0.0.1:5000
      if (window.location.protocol === "file:") {{
        const fileNotice = document.getElementById("fileProtocolNotice");
        if (fileNotice) fileNotice.style.display = "flex";

        // Probe live server via image (bypasses browser CORS / PNA restrictions on file://)
        const probe = new Image();
        probe.onload = function() {{
          console.log("Live server detected on port 5000. Redirecting from file:// to http://127.0.0.1:5000...");
          window.location.replace("http://127.0.0.1:5000/reports/application-dashboard.html");
        }};
        probe.src = "http://127.0.0.1:5000/api/ping?t=" + Date.now();
      }}

      // 1. Check for stored custom jobs
      try {{
        const storedCustomJobs = JSON.parse(localStorage.getItem("roshan_custom_jobs") || "[]");
        if (storedCustomJobs && storedCustomJobs.length) {{
          const container = document.getElementById("jobContainer");
          storedCustomJobs.forEach(cj => {{
            if (!jobsList.some(j => j.id === cj.id)) {{
              jobsList.unshift(cj);
              if (container && !document.querySelector(`.job-item[data-id="${{cj.id}}"]`)) {{
                const pillsHtml = cj.skills.map(s => `<span class="pill" onclick="filterBySkill('${{s.replace(/'/g, "\\\\'")}}')" title="Click to filter by ${{s}}">${{s}}</span>`).join("");
                const cardDiv = document.createElement("div");
                cardDiv.className = "job-item";
                cardDiv.setAttribute("data-id", cj.id);
                cardDiv.setAttribute("data-portal", cj.portal);
                cardDiv.setAttribute("data-base", cj.base_score || "92");
                cardDiv.setAttribute("data-days", cj.days_ago || "0");
                cardDiv.innerHTML = `
                  <div class="job-top">
                    <div>
                      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                        <span class="portal-badge" style="background: ${{cj.portal_color || '#3b82f6'}}22; color: ${{cj.portal_color || '#3b82f6'}}; border-color: ${{cj.portal_color || '#3b82f6'}}55;">
                          ${{cj.portal_badge || '🌐 Job Board'}}
                        </span>
                        <span class="badge-fresh-pill today">🔥 Added by You</span>
                        <span style="font-size: 13px; color: #a78bfa; font-weight: 600;">2-4 Years</span>
                      </div>
                      <div class="role-title">${{cj.title}}</div>
                      <div class="company-name">${{cj.company}} &bull; <span style="color:#94a3b8; font-weight: normal;">${{cj.location}}</span></div>
                    </div>
                    <div class="match-tag" id="tag-${{cj.id}}">${{cj.score || "92% Match"}}</div>
                  </div>
                  <div class="job-meta-row">
                    <span>📅 Posted: <strong>${{cj.date || 'Today'}}</strong></span>
                    <span>🌐 Portal: <strong>${{cj.portal}}</strong></span>
                    <span>📍 <strong>${{cj.location}}</strong></span>
                  </div>
                  <div class="pill-group" id="pills-${{cj.id}}">${{pillsHtml}}</div>
                  <div class="job-note-bar">
                    <span class="note-icon">💡</span>
                    <span class="note-text">${{cj.note || ''}}</span>
                  </div>
                  <div class="job-button-bar">
                    <button onclick="openPrepModal('${{cj.id}}')" class="btn btn-prep">🎯 Prepare Interview</button>
                    <a href="${{cj.url}}" target="_blank" class="btn btn-link" style="border-left: 2px solid ${{cj.portal_color || '#3b82f6'}};">🚀 View & Apply (${{cj.portal}}) ↗</a>
                    <button id="btn-apply-${{cj.id}}" onclick="toggleApplyJob('${{cj.id}}')" class="btn btn-apply-track">✅ Mark as Applied</button>
                    <button onclick="deleteJobRole('${{cj.id}}', event)" class="btn btn-delete" title="Delete this role">🗑️ Delete</button>
                  </div>
                `;
                container.prepend(cardDiv);
              }}
            }}
          }});
        }}
      }} catch(e) {{}}

      // 2. Check for uploaded custom resume
      try {{
        const storedResume = JSON.parse(localStorage.getItem("roshan_custom_resume") || "null");
        if (storedResume && storedResume.skills && storedResume.skills.length) {{
          allProfileSkills = [...storedResume.skills];
          disabledSkillSet.clear();
          updateActiveSkills();

          const nameEl = document.getElementById("candidateNameDisplay");
          const expEl = document.getElementById("candidateExpDisplay");
          const titleEl = document.getElementById("candidateTitleDisplay");
          if (nameEl) nameEl.innerText = storedResume.name || "Uploaded Candidate";
          if (expEl) expEl.innerText = storedResume.exp || "2.5+ Years";
          if (titleEl) titleEl.innerText = storedResume.title || "Software Engineer";

          const banner = document.getElementById("uploadedResumeBanner");
          const fileNameEl = document.getElementById("uploadedFileName");
          const skillsCountEl = document.getElementById("uploadedSkillsCount");
          const activeBadge = document.getElementById("activeResumeBadge");

          if (banner) banner.style.display = "flex";
          if (fileNameEl) fileNameEl.innerText = `Active Resume: ${{storedResume.fileName || 'Uploaded Resume'}} (${{storedResume.name}})`;
          if (skillsCountEl) skillsCountEl.innerText = ` • Replaced manual profile with ${{storedResume.skills.length}} extracted skills`;
          if (activeBadge) {{
            activeBadge.className = "active-resume-badge custom";
            activeBadge.innerText = "✨ Uploaded Profile";
          }}
        }}
      }} catch(e) {{}}

      recalculateJobFreshnessAndDates();
      renderSkillToggles();
      recalculateAllCompanies();
      updatePortalLauncherLinks();

      // 3. Zero-Prompt Daily Auto-Crawl on date rollover
      try {{
        const todayObj = new Date();
        const todayIso = todayObj.getFullYear() + "-" + String(todayObj.getMonth() + 1).padStart(2, "0") + "-" + String(todayObj.getDate()).padStart(2, "0");
        const lastCrawlDate = localStorage.getItem("roshan_last_crawl_date");

        if (lastCrawlDate !== todayIso) {{
          console.log(`🌅 Date change detected (last: ${{lastCrawlDate}}, today: ${{todayIso}}). Auto-syncing fresh .NET & React jobs...`);
          localStorage.setItem("roshan_last_crawl_date", todayIso);
          setTimeout(() => {{
            triggerDailyLiveSearch({{ auto: true }});
          }}, 1200);
        }}
      }} catch(e) {{}}
    }});
  </script>
</body>
</html>
"""

Path("reports").mkdir(exist_ok=True)
with open("reports/application-dashboard.html", "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"Successfully generated multi-portal dashboard with {len(jobs_data)} roles across all job boards.")
