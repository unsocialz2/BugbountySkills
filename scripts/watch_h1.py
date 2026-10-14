#!/usr/bin/env python3
import json
import os
import time

import requests

SEEN_FILE = "seen.txt"
URL = "https://hackerone.com/programs/search?query=&sort_type=published_at&page=1"


def load_seen() -> set[str]:
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, encoding="utf-8") as fh:
        return set(fh.read().split())


def notify(text: str) -> None:
    webhook = os.environ["DISCORD_WH"]
    requests.post(webhook, json={"content": text[:1900]}, timeout=20)


def main() -> None:
    seen = load_seen()
    while True:
        response = requests.get(URL, headers={"Accept": "application/json"}, timeout=30)
        response.raise_for_status()
        data = response.json()
        for program in data.get("programs", []):
            handle = program.get("handle")
            if not handle or handle in seen:
                continue
            name = program.get("name", handle)
            notify(f"NEW: {name} https://hackerone.com/{handle}")
            seen.add(handle)
            with open(SEEN_FILE, "a", encoding="utf-8") as fh:
                fh.write(handle + "\n")
        time.sleep(3600)


if __name__ == "__main__":
    main()
