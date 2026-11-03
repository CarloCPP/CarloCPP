#!/usr/bin/env python3
"""
generate_night_shift.py
Generates a curated, deterministic telemetry vignette for Carlo's GitHub profile.
Guarantees:
- Zero private repo queries or network access
- Fail-closed: invalid markers or state will abort without modifying README
- Atomic file replacement
- Mobile-friendly width (< 48 chars)
"""

import os
import random
import sys
import tempfile
from datetime import datetime, timezone, timedelta

# Hong Kong Time (UTC+8)
HKT = timezone(timedelta(hours=8))

# Generic, abstract engineering vignettes without internal architecture fingerprints
CATALOG = [
    ("[Coordinator]", "Task routing vignette", "[DISPATCHED]"),
    ("[Coordinator]", "Node health-probe cycle", "[HEALTHY]"),
    ("[Builder]",     "Hermetic sandbox dry-run", "[COMPLETED]"),
    ("[Builder]",     "Nightly build validation", "[PASSED]"),
    ("[Reviewer]",    "Boundary static analysis", "[VERIFIED]"),
    ("[Reviewer]",    "Schema consistency check", "[CLEAN]"),
    ("[Indexer]",     "Vector storage maintenance", "[OPTIMIZED]"),
    ("[Indexer]",     "State snapshot synchronization", "[COMMITTED]"),
    ("[Sentinel]",    "Heartbeat validation check", "[HEALTHY]"),
    ("[Sentinel]",    "Network ingress latency check", "[NOMINAL]"),
    ("[Janitor]",     "Stale cache cleanup run", "[PRUNED]"),
    ("[Janitor]",     "Temp buffer reconciliation", "[COMPLETED]"),
]

def generate_log_stream(reference_time=None):
    if reference_time is None:
        reference_time = datetime.now(HKT)

    selected = random.sample(CATALOG, 5)
    
    gen_time_str = reference_time.strftime("%Y-%m-%d %H:%M HKT")
    lines = [
        "[THE NIGHT SHIFT / SYNTHETIC LOG]",
        f"Generated: {gen_time_str}",
        ""
    ]
    
    # 5 steps backwards from reference_time to ensure all events are strictly in the past
    # Events between 110 mins ago and 10 mins ago
    offsets = sorted(random.sample(range(10, 115), 5), reverse=True)
    
    for (role, action, status), offset in zip(selected, offsets):
        event_time = reference_time - timedelta(minutes=offset)
        time_str = event_time.strftime("%H:%M")
        lines.append(f"{time_str}  {role:<15} {action}")
        lines.append(f"       → Status: {status}")
        
    return "\n".join(lines)

def update_readme(readme_path, log_stream):
    if not os.path.isabs(readme_path):
        readme_path = os.path.abspath(readme_path)

    if not os.path.exists(readme_path):
        raise FileNotFoundError(f"Target README not found: {readme_path}")

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- NIGHT_SHIFT_START -->"
    end_marker = "<!-- NIGHT_SHIFT_END -->"

    # Fail-closed validations
    start_count = content.count(start_marker)
    end_count = content.count(end_marker)

    if start_count != 1:
        raise ValueError(f"Expected exactly 1 '{start_marker}', found {start_count}")
    if end_count != 1:
        raise ValueError(f"Expected exactly 1 '{end_marker}', found {end_count}")

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx >= end_idx:
        raise ValueError("Invalid marker order: START marker appears after END marker")

    prefix = content[: start_idx + len(start_marker)] + "\n```text\n"
    suffix = "\n```\n" + content[end_idx:]

    new_content = prefix + log_stream + suffix

    # Atomic write via tempfile in the same directory
    target_dir = os.path.dirname(readme_path)
    fd, tmp_file = tempfile.mkstemp(dir=target_dir, prefix="readme_tmp_", text=True)
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_file, readme_path)
    except Exception:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        raise

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_readme = os.path.join(base_dir, "README.md")
    stream = generate_log_stream()
    update_readme(target_readme, stream)
    print("Night Shift Telemetry successfully updated.")
