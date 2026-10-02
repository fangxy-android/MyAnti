#!/usr/bin/env python3
"""Antigravity Lifecycle Hook Handler for Codex Desktop Pet.
Listens to Antigravity IDE events and automatically syncs desktop pet state.
"""

import sys
import json
import urllib.request

API_URL = "http://127.0.0.1:8765"

def notify_pet(state: str, text: str = "", mood: str = "info", timeout: float = 300.0):
    try:
        req = urllib.request.Request(
            f"{API_URL}/api/state",
            data=json.dumps({
                "state": state,
                "text": text,
                "mood": mood,
                "timeout": timeout
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=1.0)
    except Exception:
        pass # Silent if pet is not running

def main():
    hook_type = sys.argv[1].lower() if len(sys.argv) > 1 else "pre_invocation"

    # Read context payload from stdin if available
    payload = {}
    try:
        if not sys.stdin.isatty():
            content = sys.stdin.read().strip()
            if content:
                payload = json.loads(content)
    except Exception:
        payload = {}

    if hook_type == "pre_invocation":
        # User just sent a message, agent starting!
        notify_pet("working", "收到主人指令！正在编写代码与思考中~ 🌸", mood="working", timeout=300.0)
        print(json.dumps({"injectSteps": []}))
        return

    elif hook_type == "pre_tool_use":
        tool_name = payload.get("toolCall", {}).get("name", "tool")
        notify_pet("working", f"正在执行工具: {tool_name} ⚡", mood="working", timeout=120.0)
        print(json.dumps({"decision": "allow"}))
        return

    elif hook_type == "post_tool_use":
        err = payload.get("error", "")
        if err:
            notify_pet("error", "工具执行遇到异常！⚠️", mood="error", timeout=15.0)
        print(json.dumps({}))
        return

    elif hook_type == "stop":
        # Turn finished! Celebrate and notify user
        notify_pet("done", "任务完成啦！主人请查看~ (✌️ ✌️) 🌸", mood="success", timeout=12.0)
        print(json.dumps({"decision": "approve"}))
        return

    # Default fallback
    print(json.dumps({}))

if __name__ == "__main__":
    main()
