import re
from pathlib import Path

dashboard_file = Path("tools/generate_1to3yr_dashboard.py")
content = dashboard_file.read_text(encoding="utf-8")

# Extract dictionaries roughly
import ast

start_idx = content.find("jobs_data = [")
end_marker = "\n]\n\n# Pre-generate prep guides for all roles"
end_idx = content.find(end_marker)

jobs_code = content[start_idx + len("jobs_data = "):end_idx + 2]
jobs = ast.literal_eval(jobs_code)

print(f"Loaded {len(jobs)} jobs successfully via ast.literal_eval!")
for j in jobs:
    print(f"{j['id']}: date='{j.get('date')}', days_ago={j.get('days_ago')}")

