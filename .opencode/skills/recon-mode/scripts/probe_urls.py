#!/usr/bin/env python3
"""Bounded GET observations for exact pre-approved URLs; no redirects or status filtering."""
import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

from collect_assets import NoRedirect, checked_headers, checked_url, input_digest, utc_now, write_json_atomic


def probe(urls, output, interval, max_bytes, headers=None, policy=None):
    import math
    if not math.isfinite(interval) or interval < 0 or type(max_bytes) is not int or max_bytes <= 0:
        raise ValueError('invalid interval or byte limit')
    request_headers = checked_headers({} if headers is None else headers)
    urls = list(dict.fromkeys(checked_url(u.strip()) for u in urls if u.strip()))
    if not urls:
        raise ValueError('empty approved URL list')
    if policy is not None:
        policy.preflight(urls, interval, max_bytes)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    summary = {'schema_version': 1, 'format': 'url-probe', 'started_utc': utc_now(),
               'completed': False, 'status': 'running', 'requested': len(urls),
               'input_sha256': input_digest(urls), 'interval_seconds': interval,
               'max_bytes': max_bytes, 'custom_headers': bool(request_headers)}
    summary['scope_policy_sha256'] = policy.sha256 if policy is not None else None
    summary['scope_mode'] = 'enforced-policy' if policy is not None else 'preapproved-library-input'
    write_json_atomic(output / 'run.json', summary)
    opener = urllib.request.build_opener(NoRedirect())
    failed = 0
    with (output / 'responses.jsonl').open('x', encoding='utf-8') as manifest:
        for index, url in enumerate(urls):
            if index:
                time.sleep(interval)
            record = {'url': url, 'time_utc': utc_now()}
            try:
                request = urllib.request.Request(url, headers={
                    'user-agent': 'BugbountySkills-url-probe/1',
                    **request_headers, 'accept-encoding': 'identity'})
                try:
                    response = opener.open(request, timeout=20)
                except urllib.error.HTTPError as error:
                    response = error  # A 3xx/4xx/5xx is an HTTP observation, not a transport failure.
                with response:
                    status = response.getcode()
                    content_type = response.headers.get('Content-Type', '')
                    content_encoding = response.headers.get('Content-Encoding', 'identity')
                    body = response.read(max_bytes + 1)
                truncated = len(body) > max_bytes
                body = body[:max_bytes]
                name = hashlib.sha256(url.encode()).hexdigest() + '.body'
                with (output / name).open('xb') as stream:
                    stream.write(body)
                    stream.flush()
                    os.fsync(stream.fileno())
                record.update(outcome='response', http_status=status, file=name, bytes=len(body),
                              sha256=hashlib.sha256(body).hexdigest(), content_type=content_type,
                              content_encoding=content_encoding, truncated=truncated)
            except (OSError, ValueError, urllib.error.URLError, http.client.HTTPException) as error:
                failed += 1
                record.update(outcome='transport-or-storage-error', error=type(error).__name__)
            manifest.write(json.dumps(record) + '\n')
            manifest.flush()
            os.fsync(manifest.fileno())
    summary.update(completed=True, ended_utc=utc_now(), responses=len(urls) - failed,
                   errors=failed,
                   status='complete' if not failed else ('failed' if failed == len(urls) else 'partial'),
                   manifest_sha256=hashlib.sha256((output / 'responses.jsonl').read_bytes()).hexdigest())
    write_json_atomic(output / 'run.json', summary)
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--urls', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path, help='new target-local run directory')
    parser.add_argument('--interval', required=True, type=float, help='seconds between requests, selected from program rules')
    parser.add_argument('--max-bytes', type=int, default=1_000_000)
    parser.add_argument('--headers-file', type=Path, help='JSON object of non-credential identification headers')
    parser.add_argument('--scope-policy', required=True, type=Path, help='explicit scope/rate policy JSON')
    args = parser.parse_args()
    try:
        from scope_policy import ScopePolicy
        policy = ScopePolicy.load(args.scope_policy)
        headers = json.loads(args.headers_file.read_text(encoding='utf-8-sig')) if args.headers_file else None
        errors = probe(args.urls.read_text(encoding='utf-8-sig').splitlines(), args.output,
                       args.interval, args.max_bytes, headers, policy=policy)
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(2, f'Probe failed: {type(error).__name__}\n')
    print(f'URL observations saved; transport/storage errors: {errors}. Inspect run.json and responses.jsonl.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
