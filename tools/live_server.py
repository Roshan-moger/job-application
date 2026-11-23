#!/usr/bin/env python3
"""
Live Local Server & Scraper API for AI Job Search Dashboard
Enables the dashboard's "Search & Refresh New Jobs Today" button to trigger
live portal searches, regenerate prep guides, and stream fresh vacancies
directly to the browser without requiring manual chat commands.
"""

import sys
import os
import json
import subprocess
import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
PORT = 5000

class DashboardApiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORKSPACE_DIR), **kwargs)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            # Redirect to the main dashboard
            self.send_response(302)
            self.send_header("Location", "/reports/application-dashboard.html")
            self.end_headers()
            return
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        elif self.path.startswith("/api/ping"):
            self.send_response(200)
            self.send_header("Content-Type", "image/gif")
            self._send_cors_headers()
            self.end_headers()
            # 1x1 transparent GIF
            self.wfile.write(b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")
            return
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            payload = {
                "status": "online",
                "today": datetime.date.today().isoformat(),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "workspace": str(WORKSPACE_DIR)
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return
        elif self.path == "/api/refresh":
            self._handle_refresh()
            return

        # Default file serving
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/refresh"):
            self._handle_refresh()
            return
        elif self.path in ["/api/tailor-resume", "/api/tailor_resume"]:
            self._handle_tailor_resume()
            return
        elif self.path in ["/api/delete-job", "/api/delete_job"]:
            self._handle_delete_job()
            return
        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()

    def _handle_delete_job(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            target_id = data.get("id", "").strip()

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Received /api/delete-job request for: {target_id}")

            db_path = WORKSPACE_DIR / "data" / "jobs_database.json"
            if db_path.exists() and target_id:
                jobs = json.loads(db_path.read_text(encoding="utf-8"))
                initial_count = len(jobs)
                jobs = [j for j in jobs if j.get("id") != target_id]
                db_path.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"✅ Deleted job {target_id}. Jobs count: {initial_count} -> {len(jobs)}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "deleted_id": target_id}).encode("utf-8"))
        except Exception as e:
            print(f"Error during delete job: {e}", file=sys.stderr)
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

    def _handle_tailor_resume(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            target_id = data.get("id") or data.get("company") or ""

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Received /api/tailor-resume request for: {target_id}")

            tailor_script = WORKSPACE_DIR / "tools" / "tailor_resume.py"
            res = subprocess.run(
                [sys.executable, str(tailor_script), str(target_id)],
                cwd=str(WORKSPACE_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60
            )

            # Look up generated cv_link from data/jobs_database.json
            db_path = WORKSPACE_DIR / "data" / "jobs_database.json"
            pdf_url = ""
            if db_path.exists():
                try:
                    jobs = json.loads(db_path.read_text(encoding="utf-8"))
                    for j in jobs:
                        if j.get("id") == target_id or target_id.lower() in j.get("company", "").lower():
                            pdf_url = j.get("cv_link", "")
                            break
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()

            payload = {
                "status": "success",
                "message": f"Tailored resume successfully generated for {target_id}!",
                "pdf_url": pdf_url,
                "output": res.stdout.strip()
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        except Exception as e:
            print(f"Error during tailor resume: {e}", file=sys.stderr)
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

    def _handle_refresh(self):
        today = datetime.date.today()
        is_purge = "purge" in self.path.lower()
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Received /api/refresh request for date: {today} (purge={is_purge})")

        try:
            # 1. Run live crawler to search LinkedIn & freehire ATS
            crawler_script = WORKSPACE_DIR / "tools" / "live_crawler.py"
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Running live crawler across portals...")
            cmd = [sys.executable, str(crawler_script), "3"]
            if is_purge:
                cmd.append("--purge")

            crawler_res = subprocess.run(
                cmd,
                cwd=str(WORKSPACE_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120
            )
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Crawler output: {crawler_res.stdout.strip()[-300:]}")

            # 2. Run generator script to re-score, update dates, and refresh all prep guides
            gen_script = WORKSPACE_DIR / "tools" / "generate_1to3yr_dashboard.py"
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Rebuilding dashboard HTML...")
            gen_res = subprocess.run(
                [sys.executable, str(gen_script)],
                cwd=str(WORKSPACE_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60
            )

            # Read total jobs from database
            db_path = WORKSPACE_DIR / "data" / "jobs_database.json"
            total_jobs = 0
            if db_path.exists():
                try:
                    jobs = json.loads(db_path.read_text(encoding="utf-8"))
                    total_jobs = len(jobs)
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()

            payload = {
                "status": "success",
                "message": f"Multi-portal crawl complete! {total_jobs} verified openings synchronized for {today.strftime('%b %d, %Y')}.",
                "today": today.isoformat(),
                "today_formatted": today.strftime("%b %d, %Y"),
                "timestamp": datetime.datetime.now().strftime("%I:%M:%S %p"),
                "total_jobs": total_jobs,
                "crawler_summary": crawler_res.stdout.strip()[-300:],
                "dashboard_url": "/reports/application-dashboard.html"
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        except Exception as e:
            print(f"Error during refresh: {e}", file=sys.stderr)
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

def run_server(port=PORT):
    socketserver.TCPServer.allow_reuse_address = True
    for try_port in [port, 5001, 5002, 8080]:
        try:
            with socketserver.TCPServer(("", try_port), DashboardApiHandler) as httpd:
                print(f"==================================================", flush=True)
                print(f"🚀 AI Job Search Live Server running at:", flush=True)
                print(f"   http://localhost:{try_port}/", flush=True)
                print(f"   http://127.0.0.1:{try_port}/reports/application-dashboard.html", flush=True)
                print(f"   API Status: http://localhost:{try_port}/api/status", flush=True)
                print(f"   Refresh API: http://localhost:{try_port}/api/refresh", flush=True)
                print(f"==================================================", flush=True)
                httpd.serve_forever()
        except OSError:
            print(f"Port {try_port} busy, trying next port...", flush=True)
            continue

if __name__ == "__main__":
    run_server()

