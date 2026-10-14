#!/usr/bin/env python3
import os
import sys
import requests

WH = os.environ["DISCORD_WH"]


def discord(text: str, file: str | None = None) -> None:
    if file:
        with open(file, "rb") as fh:
            requests.post(WH, data={"content": text[:1900]}, files={"file": fh}, timeout=20)
    else:
        requests.post(WH, json={"content": text[:1900]}, timeout=20)


if __name__ == "__main__":
    message = sys.stdin.read()
    attachment = sys.argv[1] if len(sys.argv) > 1 else None
    discord(message, attachment)
