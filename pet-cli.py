#!/usr/bin/env python3
"""Codex Desktop Pet - Command Line Controller (pet-cli)

Usage:
  python pet-cli.py <state> [message] [--timeout SECONDS] [--mood MOOD]
  python pet-cli.py say <message> [--mood MOOD]
  python pet-cli.py char <sakura|dewey|fireball|codebot|neko|slime>
  python pet-cli.py <wake|sleep|poke|reset|console>
  python pet-cli.py status

Examples:
  python pet-cli.py working "Compiling Rust binary..."
  python pet-cli.py done "Build succeeded! 42 tests passed."
  python pet-cli.py error "Build failed with 1 error!"
  python pet-cli.py thinking "Analyzing codebase..."
  python pet-cli.py waiting "Waiting for user confirmation..."
  python pet-cli.py say "Take a 5-minute break!"
  python pet-cli.py char sakura
  python pet-cli.py wake
  python pet-cli.py sleep
  python pet-cli.py reset
"""

import sys
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API_URL = "http://127.0.0.1:8765"

def post_json(endpoint: str, data: dict):
    url = f"{API_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            res = resp.read().decode("utf-8")
            return json.loads(res)
    except urllib.error.URLError as e:
        print(f"[pet-cli] Error connecting to Pet at {API_URL}: {e}")
        print("Please make sure the Desktop Pet is running!")
        sys.exit(1)

def get_json(endpoint: str):
    url = f"{API_URL}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            res = resp.read().decode("utf-8")
            return json.loads(res)
    except urllib.error.URLError as e:
        print(f"[pet-cli] Error connecting to Pet at {API_URL}: {e}")
        print("Please make sure the Desktop Pet is running!")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        info = get_json("/api/status")
        print(f"🐾 Character : {info.get('character')}")
        print(f"⚡ State     : {info.get('state')} ({info.get('description')})")
        return

    if cmd == "say":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hello!"
        mood = "info"
        res = post_json("/api/say", {"message": msg, "mood": mood})
        print(f"[pet-cli] Pet says: {msg}")
        return

    if cmd in ("char", "character"):
        if len(sys.argv) < 3:
            print("Usage: python pet-cli.py char <sakura|dewey|fireball|codebot|neko|slime>")
            return
        name = sys.argv[2].lower()
        res = post_json("/api/character", {"character": name})
        cname = res.get("display_name", name)
        print(f"[pet-cli] Switched character to: {name} ({cname})")
        return

    if cmd in ("wake", "sleep", "poke", "click", "reset", "reset_pos", "console", "bar", "quick_bar"):
        act_map = {
            "poke": "click",
            "reset_pos": "reset",
            "bar": "quick_bar",
            "console": "quick_bar"
        }
        action = act_map.get(cmd, cmd)
        res = post_json("/api/action", {"action": action})
        print(f"[pet-cli] Triggered action: {action}")
        return

    # Treat as state
    state = cmd
    msg = sys.argv[2] if len(sys.argv) > 2 else ""
    mood = "info"
    if state == "done":
        mood = "success"
    elif state == "error":
        mood = "error"
    elif state == "waiting":
        mood = "warning"

    # State specific timeouts:
    # working stays active (300s) until explicitly completed with done or idle
    default_timeouts = {
        "working": 300.0,
        "thinking": 120.0,
        "done": 15.0,
        "error": 20.0,
        "waiting": 60.0,
        "clicked": 3.0
    }
    timeout = default_timeouts.get(state, None)

    # Check for custom --timeout
    if "--timeout" in sys.argv:
        idx = sys.argv.index("--timeout")
        if idx + 1 < len(sys.argv):
            timeout = float(sys.argv[idx + 1])

    payload = {
        "state": state,
        "text": msg,
        "timeout": timeout,
        "mood": mood
    }

    res = post_json("/api/state", payload)
    print(f"[pet-cli] Set state to '{state}' (message: '{msg}')")

if __name__ == "__main__":
    main()
