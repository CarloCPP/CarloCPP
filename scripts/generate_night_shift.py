#!/usr/bin/env python3
"""
generate_night_shift.py
Generates a curated, deterministic telemetry log stream for Carlo's GitHub profile.
Guarantees 100% privacy: zero private repo inspection, zero network calls, zero token leakage.
"""

import os
import random
from datetime import datetime, timezone, timedelta

# Hong Kong Time (UTC+8)
HKT = timezone(timedelta(hours=8))
now = datetime.now(HKT)

SUBSYSTEMS = [
    ("[Fairy-Core]", "Automated multi-account failover check", "[PASS] 0-downtime"),
    ("[Fairy-Core]", "Routine health probe across local nodes", "[HEALTHY] 200 OK"),
    ("[Astra-Oracle]", "Static analysis & boundary gate review", "[VERIFIED] clean"),
    ("[Astra-Oracle]", "Architectural dependency tree audit", "[APPROVED] zero-leak"),
    ("[System-CI]", "End-to-end sandbox pipeline dry-run", "[OK] 16/16 passed"),
    ("[System-CI]", "Hermetic environment container lint", "[PASS] exit 0"),
    ("[Librarian]", "Compact memory indexes & state sync", "[COMMITTED]"),
    ("[Librarian]", "Prune stale vector embeddings cache", "[OPTIMIZED] -12MB"),
    ("[Sentinel-Bot]", "Zero-port tunnel heartbeat validation", "[HEALTHY] 200 OK"),
    ("[Sentinel-Bot]", "Tailscale egress latency benchmark", "[LOW-LATENCY] 18ms"),
    ("[Builder]", "Nightly build matrix: arm64/Darwin pass", "[SUCCESS] v1.4.2"),
    ("[Janitor]", "Garbage collect dead sockets & temp spool", "[CLEANED] 0 errors"),
]

def generate_log_stream():
    # Pick 5 distinct events
    selected = random.sample(SUBSYSTEMS, 5)
    
    # Generate realistic timestamps in chronological order over the last few hours
    base_minutes = random.randint(10, 50)
    lines = [
        "TIMESTAMP (HKT)   SUBSYSTEM        EVENT & PIPELINE ACTION               STATUS",
        "───────────────────────────────────────────────────────────────────────────────"
    ]
    
    current_time = now - timedelta(hours=2)
    for subsystem, event, status in selected:
        current_time += timedelta(minutes=random.randint(8, 25), seconds=random.randint(5, 55))
        time_str = current_time.strftime("%H:%M:%S")
        lines.append(f"{time_str:<17} {subsystem:<16} {event:<37} {status}")
    
    return "\n".join(lines)

def update_readme(log_stream):
    readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
    if not os.path.exists(readme_path):
        readme_path = "README.md"
        
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- NIGHT_SHIFT_START -->"
    end_marker = "<!-- NIGHT_SHIFT_END -->"

    if start_marker not in content or end_marker not in content:
        raise ValueError("Missing markers in README.md")

    prefix = content.split(start_marker)[0] + start_marker + "\n```text\n"
    suffix = "\n```\n" + end_marker + content.split(end_marker)[1]

    new_content = prefix + log_stream + suffix

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    stream = generate_log_stream()
    update_readme(stream)
    print("Night Shift Telemetry successfully updated.")
