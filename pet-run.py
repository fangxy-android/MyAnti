#!/usr/bin/env python3
"""Wrapper tool to run any command and automatically sync pet state.

Usage:
  python pet-run.py <command and args...>

Examples:
  python pet-run.py npm test
  python pet-run.py git push
  python pet-run.py pytest
  python pet-run.py cargo build
"""

import sys
import subprocess
import urllib.request
import json

API_URL = "http://127.0.0.1:8765"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def notify_pet(state: str, text: str, mood: str = "info", timeout: float = 5.0):
    try:
        req = urllib.request.Request(
            f"{API_URL}/api/state",
            data=json.dumps({"state": state, "text": text, "mood": mood, "timeout": timeout}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=1.0)
    except Exception:
        pass # Silent if pet is not running

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1:]
    cmd_str = " ".join(cmd)
    display_name = cmd_str[:30] + ("..." if len(cmd_str) > 30 else "")

    # 1. Notify pet that work started
    notify_pet("working", f"正在执行: {display_name}", mood="info", timeout=300.0)

    # 2. Run child process and stream output live
    try:
        res = subprocess.run(cmd, shell=True)
        code = res.returncode
    except KeyboardInterrupt:
        notify_pet("idle", "任务被用户中断")
        sys.exit(130)
    except Exception as e:
        notify_pet("error", f"命令启动异常: {e}", mood="error", timeout=5.0)
        sys.exit(1)

    # 3. Notify pet result
    if code == 0:
        notify_pet("done", f"执行成功: {display_name} 🎉", mood="success", timeout=5.0)
    else:
        notify_pet("error", f"执行失败 (退出码 {code}) ⚠️", mood="error", timeout=6.0)

    sys.exit(code)

if __name__ == "__main__":
    main()
