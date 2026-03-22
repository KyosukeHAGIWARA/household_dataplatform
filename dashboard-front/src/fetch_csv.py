from __future__ import annotations

import os
from pathlib import Path

import httpx

BASE_DIR = Path(__file__).resolve().parents[1]

WORKER_URL = os.getenv(
    "WORKER_ENDPOINT",
    "http://127.0.0.1:8787",  # wrangler dev default
)
RAW_DIR = BASE_DIR / "data/raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_files() -> None:
    res = httpx.get(f"{WORKER_URL}/files", timeout=30.0)
    res.raise_for_status()
    keys = res.json()

    if not keys:
        print("No files found.")
        return

    for item in keys:
        key = item["name"]
        filepath = RAW_DIR / f"{key}.csv"

        if filepath.exists():
            print(f"Skip (already exists): {key}")
            continue

        csv_res = httpx.get(f"{WORKER_URL}/fetch/{key}", timeout=60.0)
        csv_res.raise_for_status()
        filepath.write_text(csv_res.text, encoding="utf-8")
        print(f"Saved: {filepath}")


if __name__ == "__main__":
    fetch_files()
