#!/usr/bin/env python3
"""GridLib status generator — writes status.json every 15 seconds. No server, no deps."""

import json
import os
import subprocess
import time
from pathlib import Path

OUTPUT = Path(__file__).parent / "status.json"
ZIM_DIR = Path(os.environ.get("ZIM_DIR", "/srv/kiwix/content"))
INTERVAL = int(os.environ.get("GRIDLIB_INTERVAL", 15))


def _read(path: str) -> str | None:
    try:
        return Path(path).read_text().strip()
    except Exception:
        return None


def _run(*cmd: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(list(cmd), capture_output=True, text=True, timeout=3)
    except Exception:
        return None


def cpu_percent() -> float:
    try:
        def read_stat():
            parts = Path("/proc/stat").read_text().splitlines()[0].split()
            vals = [int(x) for x in parts[1:]]
            return vals[3], sum(vals)

        i1, t1 = read_stat()
        time.sleep(0.3)
        i2, t2 = read_stat()
        dt = t2 - t1
        return round((1 - (i2 - i1) / dt) * 100, 1) if dt > 0 else 0.0
    except Exception:
        return 0.0


def memory() -> dict:
    try:
        info: dict[str, int] = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            info[k.strip()] = int(v.strip().split()[0])
        total = info.get("MemTotal", 0)
        avail = info.get("MemAvailable", 0)
        used = total - avail
        pct = round(used / total * 100, 1) if total else 0.0
        return {"total_mb": total // 1024, "used_mb": used // 1024, "percent": pct}
    except Exception:
        return {"total_mb": 0, "used_mb": 0, "percent": 0.0}


def temperature() -> float | None:
    raw = _read("/sys/class/thermal/thermal_zone0/temp")
    if raw and raw.isdigit():
        return round(int(raw) / 1000, 1)
    return None


def disk() -> dict:
    try:
        r = _run("df", "-B1", "/")
        if r and r.returncode == 0:
            parts = r.stdout.strip().splitlines()[1].split()
            total, used = int(parts[1]), int(parts[2])
            pct = round(used / total * 100, 1) if total else 0.0
            return {
                "total_gb": round(total / 1_000_000_000, 1),
                "used_gb": round(used / 1_000_000_000, 1),
                "percent": pct,
            }
    except Exception:
        pass
    return {"total_gb": 0.0, "used_gb": 0.0, "percent": 0.0}


def service_active(name: str) -> bool:
    r = _run("systemctl", "is-active", name)
    return r is not None and r.stdout.strip() == "active"


def zim_files() -> list[str]:
    try:
        return sorted(f.name for f in ZIM_DIR.glob("*.zim"))
    except Exception:
        return []


def get_status() -> dict:
    return {
        "cpu_percent": cpu_percent(),
        "memory": memory(),
        "temperature_c": temperature(),
        "disk": disk(),
        "services": {
            "kiwix": {"active": service_active("kiwix-serve"), "port": 8080},
        },
        "zims": zim_files(),
    }


if __name__ == "__main__":
    print(f"GridLib status generator running (interval: {INTERVAL}s) → {OUTPUT}")
    while True:
        try:
            status = get_status()
            OUTPUT.write_text(json.dumps(status))
        except Exception as e:
            print(f"Error generating status: {e}")
        time.sleep(INTERVAL)
