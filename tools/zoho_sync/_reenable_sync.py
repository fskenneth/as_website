"""One-shot helper: restore SYNC_SCHEDULE intervals and restart the server.

Invoked by an OpenClaw cron at 2am on 2026-04-20 to re-enable m4 Zoho sync.
Safe to re-run — idempotent (no-op if intervals already match originals).

Usage:
    /Users/kennethjin/Desktop/development/as_website/.venv/bin/python \
        /Users/kennethjin/Desktop/development/as_website/tools/zoho_sync/_reenable_sync.py
"""
import re
import subprocess
import sys
import time
from pathlib import Path

CONFIG = Path(__file__).parent / "config.py"
ORIGINAL_INTERVALS = {
    "Staging_Report": 60,
    "All_Modules": 60,
    "Employee_Report": 1440,
    "Area_Report": 360,
    "All_Tasks": 60,
    "Location_Report": 1440,
    "All_Quotes": 360,
}


def restore_config() -> list[str]:
    text = CONFIG.read_text()
    changes: list[str] = []
    for report, interval in ORIGINAL_INTERVALS.items():
        # Match: "{report}": { ... "interval_minutes": 0,  # disabled: ...
        # Replace the 0 with original interval and drop the disabled comment.
        pattern = (
            rf'("{report}":\s*\{{\s*\n\s*)"interval_minutes":\s*0,[^\n]*'
        )
        new_text, n = re.subn(
            pattern,
            rf'\1"interval_minutes": {interval},',
            text,
        )
        if n == 1:
            changes.append(f"{report}: 0 -> {interval}")
            text = new_text
        elif n == 0:
            changes.append(f"{report}: already non-zero (skipped)")
        else:
            raise RuntimeError(f"{report}: pattern matched {n} times (expected 1)")
    CONFIG.write_text(text)
    return changes


def restart_server() -> str:
    # Kill anything on :5001
    subprocess.run(
        "lsof -ti :5001 | xargs -r kill -9",
        shell=True,
        check=False,
    )
    time.sleep(2)
    # Start fresh
    project = CONFIG.parent.parent.parent  # .../as_website
    venv_py = project / ".venv" / "bin" / "python"
    log = Path("/tmp/as_website.log")
    proc = subprocess.Popen(
        f"nohup {venv_py} main.py > {log} 2>&1 &",
        shell=True,
        cwd=str(project),
    )
    time.sleep(5)
    # Find the running PID
    out = subprocess.check_output(
        "ps aux | grep 'python main.py' | grep -v grep | awk '{print $2}'",
        shell=True,
        text=True,
    ).strip()
    return out or "<no pid found>"


def main() -> int:
    changes = restore_config()
    print("Config changes:")
    for c in changes:
        print(f"  {c}")

    pid = restart_server()
    print(f"Server PID(s): {pid}")

    # Show last log lines
    log = Path("/tmp/as_website.log")
    if log.exists():
        print("\nServer log tail:")
        for line in log.read_text().splitlines()[-15:]:
            print(f"  {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
