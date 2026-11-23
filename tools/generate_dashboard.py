import json
import csv
from pathlib import Path

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Job Search Dashboard - Roshan Moger</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f2937;
      --card-hover: #374151;
      --text-main: #f9fafb;
      --text-muted: #9ca3af;
      --accent: #2563eb;
      --accent-light: #3b82f6;
      --success: #10b981;
      --warning: #f59e0b;
      --purple: #8b5cf6;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      padding: 24px;
      line-height: 1.5;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    
    header {
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .header-top { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
    h1 { font-size: 30px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; }
    .status-pill {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .pulse { width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981; }
    .subtitle { color: #94a3b8; font-size: 16px; margin-top: 8px; font-weight: 400; }
    
    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }
    .meta-tag {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid #334155;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      color: #cbd5e1;
      text-decoration: none;
    }
    .meta-tag a { color: #38bdf8; text-decoration: none; }
    .meta-tag a:hover { text-decoration: underline; }

    .stats-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
    }
    .stat-card::after {
      content: "";
      position: absolute;
      top: 0; left: 0; height: 4px; width: 100%;
    }
    .c-blue::after { background: #3b82f6; }
    .c-green::after { background: #10b981; }
    .c-purple::after { background: #8b5cf6; }
    .c-amber::after { background: #f59e0b; }
    
    .stat-num { font-size: 32px; font-weight: 800; color: #fff; }
    .stat-desc { font-size: 13px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-top: 4px; }

    .layout-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }
    @media (max-width: 960px) {
      .layout-grid { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 24px;
    }
    .card-title {
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .search-input {
      width: 100%;
      background: #0f172a;
      border: 1px solid #334155;
      padding: 12px 16px;
      border-radius: 10px;
      color: #fff;
      font-size: 14px;
      margin-bottom: 18px;
    }
    .search-input:focus {
      outline: none;
      border-color: var(--accent-light);
    }

    .job-list { display: flex; flex-direction: column; gap: 14px; }
    .job-item {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 18px 20px;
      transition: all 0.2s ease;
    }
    .job-item:hover {
      border-color: var(--accent-light);
      transform: translateY(-2px);
    }
    .job-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
    .role-title { font-size: 17px; font-weight: 700; color: #fff; }
    .company-name { font-size: 14px; color: #38bdf8; font-weight: 600; margin-top: 2px; }
    .match-tag {
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
    }
    .job-meta-row { display: flex; gap: 14px; font-size: 13px; color: var(--text-muted); margin: 8px 0 12px 0; }
    .pill-group { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
    .pill {
      background: #0f172a;
      color: #cbd5e1;
      padding: 3px 9px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 500;
      border: 1px solid #334155;
    }
    .job-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .btn {
      background: #2563eb;
      color: #ffffff;
      text-decoration: none;
      padding: 7px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      display: inline-block;
      transition: background 0.2s;
    }
    .btn:hover { background: #1d4ed8; }

    .score-row { margin-bottom: 14px; }
    .score-label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; }
    .bar-bg { height: 7px; background: #334155; border-radius: 9999px; overflow: hidden; }
    .bar-val { height: 100%; border-radius: 9999px; }

    .instructions-box {
      background: #0f172a;
      border: 1px dashed #334155;
      border-radius: 10px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.6;
    }
    .instructions-box code {
      background: #1e293b;
      color: #38bdf8;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-top">
        <h1>Roshan Moger</h1>
        <div class="status-pill"><span class="pulse"></span> AI Assistant Framework Active</div>
      </div>
      <div class="subtitle">Full Stack Developer | React.js &bull; TypeScript &bull; ASP.NET Core &bull; C# &bull; AWS &bull; Redis</div>
      <div class="meta-bar">
        <span class="meta-tag">📍 Mysore, Karnataka, India</span>
        <span class="meta-tag">💼 Associate Software Engineer (ExcelSoft)</span>
        <span class="meta-tag">🎓 B.E. Electrical & Electronics (NIE Institute)</span>
        <span class="meta-tag">🔗 <a href="https://linkedin.com/in/roshan-moger" target="_blank">LinkedIn Profile</a></span>
        <span class="meta-tag">💻 <a href="https://github.com/Roshan-moger" target="_blank">GitHub Profile</a></span>
        <span class="meta-tag">📧 roshanmoger502@gmail.com</span>
      </div>
    </header>

    <div class="stats-row">
      <div class="stat-card c-blue">
        <div class="stat-num">5</div>
        <div class="stat-desc">Live Jobs Scraped</div>
      </div>
      <div class="stat-card c-green">
        <div class="stat-num">90%</div>
        <div class="stat-desc">Top Match Score</div>
      </div>
      <div class="stat-card c-purple">
        <div class="stat-num">2+ Yrs</div>
        <div class="stat-desc">Full-Stack Experience</div>
      </div>
      <div class="stat-card c-amber">
        <div class="stat-num">LaTeX Ready</div>
        <div class="stat-desc">PDF Generation Active</div>
      </div>
    </div>

    <div class="layout-grid">
      <!-- Left Column -->
      <div>
        <div class="card">
          <div class="card-title">
            <span>🎯 Matched Jobs (Bangalore & Remote)</span>
          </div>

          <input type="text" id="filterBox" class="search-input" placeholder="Search by role, company, or tech (e.g. React, .NET, AWS)..." onkeyup="filter()">

          <div class="job-list" id="jobContainer">
            <!-- Job 1 -->
            <div class="job-item">
              <div class="job-top">
                <div>
                  <div class="role-title">Fullstack Developer - .NET Core, React, AWS</div>
                  <div class="company-name">Quest Global</div>
                </div>
                <div class="match-tag">90% Match</div>
              </div>
              <div class="job-meta-row">
                <span>📍 Bengaluru, Karnataka</span>
                <span>📅 Posted Aug 31, 2026</span>
                <span>⚡ Full-Time</span>
              </div>
              <div class="pill-group">
                <span class="pill">C#</span>
                <span class="pill">.NET Core</span>
                <span class="pill">React</span>
                <span class="pill">AWS</span>
                <span class="pill">REST API</span>
                <span class="pill">Microservices</span>
                <span class="pill">Docker</span>
                <span class="pill">Redux</span>
              </div>
              <div class="job-actions">
                <span style="font-size: 13px; color: #10b981;">✓ Direct match with Roshan's daily tech stack at ExcelSoft</span>
                <a href="https://www.linkedin.com/jobs/view/4459793842" target="_blank" class="btn">View on LinkedIn ↗</a>
              </div>
            </div>

            <!-- Job 2 -->
            <div class="job-item">
              <div class="job-top">
                <div>
                  <div class="role-title">Full-Stack Developer (.NET & ReactJS)</div>
                  <div class="company-name">Merck Group</div>
                </div>
                <div class="match-tag">88% Match</div>
              </div>
              <div class="job-meta-row">
                <span>📍 Bengaluru, Karnataka</span>
                <span>📅 Posted Aug 19, 2026</span>
                <span>⚡ Full-Time</span>
              </div>
              <div class="pill-group">
                <span class="pill">ReactJS</span>
                <span class="pill">.NET Core</span>
                <span class="pill">RESTful APIs</span>
                <span class="pill">SQL Server</span>
                <span class="pill">MongoDB</span>
                <span class="pill">Agile</span>
              </div>
              <div class="job-actions">
                <span style="font-size: 13px; color: #10b981;">✓ Enterprise application engineering match</span>
                <a href="https://www.linkedin.com/jobs/view/4437862282" target="_blank" class="btn">View on LinkedIn ↗</a>
              </div>
            </div>

            <!-- Job 3 -->
            <div class="job-item">
              <div class="job-top">
                <div>
                  <div class="role-title">Frontend Developer (React JS, Next JS)</div>
                  <div class="company-name">Kavintech Corporation</div>
                </div>
                <div class="match-tag">84% Match</div>
              </div>
              <div class="job-meta-row">
                <span>📍 Bengaluru, Karnataka</span>
                <span>📅 Posted Sep 04, 2026</span>
                <span>⚡ Full-Time</span>
              </div>
              <div class="pill-group">
                <span class="pill">React.js</span>
                <span class="pill">TypeScript</span>
                <span class="pill">Next.js</span>
                <span class="pill">Redux</span>
                <span class="pill">Tailwind CSS</span>
              </div>
              <div class="job-actions">
                <span style="font-size: 13px; color: #94a3b8;">✓ Modern single page UI architecture</span>
                <a href="https://www.linkedin.com/jobs/view/4463323804" target="_blank" class="btn">View on LinkedIn ↗</a>
              </div>
            </div>

            <!-- Job 4 -->
            <div class="job-item">
              <div class="job-top">
                <div>
                  <div class="role-title">React JS Developer - SDE 1</div>
                  <div class="company-name">Truemeds</div>
                </div>
                <div class="match-tag">85% Match</div>
              </div>
              <div class="job-meta-row">
                <span>📍 Bengaluru, Karnataka</span>
                <span>📅 Posted Aug 26, 2026</span>
                <span>⚡ Full-Time</span>
              </div>
              <div class="pill-group">
                <span class="pill">React.js</span>
                <span class="pill">JavaScript</span>
                <span class="pill">Redux</span>
                <span class="pill">REST APIs</span>
              </div>
              <div class="job-actions">
                <span style="font-size: 13px; color: #94a3b8;">✓ High-growth consumer tech app</span>
                <a href="https://www.linkedin.com/jobs/view/4457244557" target="_blank" class="btn">View on LinkedIn ↗</a>
              </div>
            </div>

            <!-- Job 5 -->
            <div class="job-item">
              <div class="job-top">
                <div>
                  <div class="role-title">React Developer (Remote)</div>
                  <div class="company-name">Sequoia Connect</div>
                </div>
                <div class="match-tag">82% Match</div>
              </div>
              <div class="job-meta-row">
                <span>📍 100% Remote</span>
                <span>📅 Posted Sep 04, 2026</span>
                <span>⚡ Global Remote</span>
              </div>
              <div class="pill-group">
                <span class="pill">React.js</span>
                <span class="pill">TypeScript</span>
                <span class="pill">Redux</span>
                <span class="pill">REST</span>
                <span class="pill">Git</span>
              </div>
              <div class="job-actions">
                <span style="font-size: 13px; color: #94a3b8;">✓ International remote role via freehire.me</span>
                <a href="https://freehire.me" target="_blank" class="btn">View on Freehire ↗</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div>
        <div class="card">
          <div class="card-title">⚡ Quest Global Fit Analysis</div>
          <div class="score-row">
            <div class="score-label">
              <span>Technical Skills Match</span>
              <span style="color: #10b981; font-weight: 700;">92%</span>
            </div>
            <div class="bar-bg"><div class="bar-val" style="width: 92%; background: #10b981;"></div></div>
          </div>
          <div class="score-row">
            <div class="score-label">
              <span>Experience & Domain</span>
              <span style="color: #38bdf8; font-weight: 700;">85%</span>
            </div>
            <div class="bar-bg"><div class="bar-val" style="width: 85%; background: #38bdf8;"></div></div>
          </div>
          <div class="score-row">
            <div class="score-label">
              <span>Culture & Agile Fit</span>
              <span style="color: #8b5cf6; font-weight: 700;">88%</span>
            </div>
            <div class="bar-bg"><div class="bar-val" style="width: 88%; background: #8b5cf6;"></div></div>
          </div>
          <div class="score-row">
            <div class="score-label">
              <span>Career Growth Potential</span>
              <span style="color: #f59e0b; font-weight: 700;">90%</span>
            </div>
            <div class="bar-bg"><div class="bar-val" style="width: 90%; background: #f59e0b;"></div></div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">🛠️ Technical Stack</div>
          <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
            <p><strong style="color: #38bdf8;">Frontend:</strong> React.js, TypeScript, Redux, React Router, Tailwind CSS</p>
            <p><strong style="color: #38bdf8;">Backend:</strong> ASP.NET Core, C#, Node.js, Express.js, REST APIs, WebSockets</p>
            <p><strong style="color: #38bdf8;">Cloud & DevOps:</strong> AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, CI/CD</p>
            <p><strong style="color: #38bdf8;">Data & Cache:</strong> Redis, PostgreSQL, MySQL, MongoDB</p>
          </div>
        </div>

        <div class="card">
          <div class="card-title">💬 Next Agent Actions</div>
          <div class="instructions-box">
            <p style="margin-bottom: 8px;">You can trigger actions right in our chat:</p>
            <p style="margin-bottom: 6px;">&bull; <code>Apply to Quest Global</code> to generate targeted LaTeX CV + cover letter.</p>
            <p style="margin-bottom: 6px;">&bull; <code>Prepare me for Quest Global interview</code> for STAR prep pack.</p>
            <p>&bull; <code>Search jobs for &lt;keyword&gt;</code> for live scrape.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    function filter() {
      const q = document.getElementById("filterBox").value.toLowerCase();
      const items = document.querySelectorAll(".job-item");
      items.forEach(item => {
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(q) ? "block" : "none";
      });
    }
  </script>
</body>
</html>
"""

Path("reports").mkdir(exist_ok=True)
with open("reports/application-dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Dashboard created successfully at reports/application-dashboard.html")
