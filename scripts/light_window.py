#!/usr/bin/env python3
"""
light_window.py
Handles the "Light a Window" visitor interaction for Kowloon Compute.
- Validates and sanitizes GitHub username
- Fail-closed parsing of README.md
- Atomic file replacement
- Keeps recent 10 unique glowing windows
"""

import os
import re
import sys
import tempfile

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$")

def sanitize_username(raw):
    cleaned = raw.strip().lstrip("@")
    if not USERNAME_REGEX.match(cleaned):
        raise ValueError(f"Invalid GitHub username: {raw}")
    return cleaned

def parse_existing_windows(block_text):
    users = []
    for line in block_text.splitlines():
        # Match lines like "🏮 Window #XX ── @username"
        match = re.search(r"@([a-zA-Z0-9-]+)", line)
        if match:
            u = match.group(1)
            if u not in users:
                users.append(u)
    return users

def format_windows_block(users):
    lines = [
        "[KOWLOON COMPUTE / ROSTER OF GLOWING WINDOWS]",
        f"Total Illuminated: {len(users)} | Grid Health: 100%",
        ""
    ]
    for idx, u in enumerate(users, start=1):
        role_tag = " (City Architect)" if u.lower() == "carlocpp" else ""
        lines.append(f"🏮 Window #{idx:02d} ── @{u}{role_tag}")
    return "\n".join(lines)

def update_readme(readme_path, new_user):
    new_user = sanitize_username(new_user)

    if not os.path.exists(readme_path):
        raise FileNotFoundError(f"README not found: {readme_path}")

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- CITY_LIGHTS_START -->"
    end_marker = "<!-- CITY_LIGHTS_END -->"

    if content.count(start_marker) != 1 or content.count(end_marker) != 1:
        raise ValueError("Invalid markers: START or END marker missing or duplicate")

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx >= end_idx:
        raise ValueError("Invalid marker order")

    existing_block = content[start_idx + len(start_marker) : end_idx]
    current_users = parse_existing_windows(existing_block)

    # Always ensure CarloCPP is in the list
    if "CarloCPP" not in current_users:
        current_users.insert(0, "CarloCPP")

    # Add or move new user to the top after CarloCPP
    if new_user in current_users:
        current_users.remove(new_user)
    
    # If not CarloCPP, insert at position 1 (right after architect)
    if new_user.lower() == "carlocpp":
        current_users.insert(0, "CarloCPP")
    else:
        current_users.insert(1, new_user)

    # Keep top 12 windows
    trimmed_users = current_users[:12]
    new_block = format_windows_block(trimmed_users)

    prefix = content[: start_idx + len(start_marker)] + "\n```text\n"
    suffix = "\n```\n" + content[end_idx:]

    new_content = prefix + new_block + suffix

    # Atomic write
    target_dir = os.path.dirname(os.path.abspath(readme_path))
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
    if len(sys.argv) < 2:
        print("Usage: python3 light_window.py <github_username>")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_file = os.path.join(base_dir, "README.md")
    username_arg = sys.argv[1]
    update_readme(readme_file, username_arg)
    print(f"Successfully lit window for @{username_arg}!")
