#!/usr/bin/env python3
"""Collect an explicitly pre-approved URL list into a new run directory.
No redirects, retries, crawling, URL expansion, or secret verification.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def checked_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password or p.fragment:
        raise ValueError('expected HTTP(S) URL without userinfo or fragment')
    if any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError('URL contains whitespace/control characters')
    _ = p.port
    return url


def validate_body(body, kind, content_type):
    if not body.strip():
        raise ValueError('empty body')
    if kind == 'sourcemap':
        obj = json.loads(body)
        if not isinstance(obj, dict) or type(obj.get('version')) is not int or obj['version'] != 3:
            raise ValueError('not a version 3 sourcemap')
        def valid_map(m):
            if not isinstance(m, dict) or type(m.get('version')) is not int or m['version'] != 3:
                return False
            if 'sections' in m:
                sections = m['sections']
                if not isinstance(sections, list) or not sections:
                    return False
                for section in sections:
                    if not isinstance(section, dict): return False
                    offset = section.get('offset', {})
                    if not isinstance(offset, dict): return False
                    if any(type(offset.get(k)) is not int or offset[k] < 0 for k in ('line', 'column')): return False
                    if not valid_map(section.get('map')): return False
                return True
            return (isinstance(m.get('sources'), list) and all(isinstance(s, str) for s in m['sources'])
                    and isinstance(m.get('names'), list) and all(isinstance(s, str) for s in m['names'])
                    and isinstance(m.get('mappings'), str))
        if not valid_map(obj):
            raise ValueError('unsupported or malformed sourcemap structure')
    else:
        prefix = body.lstrip()[:512].lower()
        mime = content_type.split(';', 1)[0].strip().lower()
        if mime in ('text/html', 'application/xhtml+xml', 'application/json') or prefix.startswith((b'<!doctype html', b'<html', b'{"error"')):
            raise ValueError('HTML/JSON error response instead of JavaScript')
    # JS is a candidate artifact, not syntactically verified or a security finding.


def fetch(opener, url, max_bytes):
    request = urllib.request.Request(url, headers={'User-Agent': 'BugbountySkills-asset-collector/1', 'Accept-Encoding': 'identity'})
    with opener.open(request, timeout=20) as response:
        if response.status != 200:
            raise ValueError('unexpected HTTP status')
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError('response exceeds byte limit')
        return body, response.headers.get('Content-Type', '')


def collect(urls, output, kind, interval, max_bytes, fetcher=None):
    if not math.isfinite(interval) or interval < 0 or max_bytes <= 0:
        raise ValueError('invalid interval or byte limit')
    urls = list(dict.fromkeys(checked_url(u.strip()) for u in urls if u.strip()))
    if not urls:
        raise ValueError('no URLs; refusing an empty successful run')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    opener = urllib.request.build_opener(NoRedirect())
    fetcher = fetcher or (lambda url: fetch(opener, url, max_bytes))
    failures = 0
    with (output / 'manifest.jsonl').open('x', encoding='utf-8') as manifest:
        for index, url in enumerate(urls):
            if index:
                time.sleep(interval)
            record = {'url': url, 'kind': kind, 'time_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
            temporary = None
            try:
                body, content_type = fetcher(url)
                if len(body) > max_bytes: raise ValueError('response exceeds byte limit')
                validate_body(body, kind, content_type)
                name = hashlib.sha256(url.encode()).hexdigest() + ('.map' if kind == 'sourcemap' else '.js')
                with tempfile.NamedTemporaryFile(dir=output, delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(body)
                temporary.replace(output / name)
                record.update(status='saved', file=name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), content_type=content_type)
            except (OSError, ValueError, urllib.error.URLError) as error:
                failures += 1
                # Avoid logging exception strings that may contain credentials/URLs.
                record.update(status='failed', error=type(error).__name__)
                if isinstance(error, urllib.error.HTTPError):
                    record['http_status'] = error.code
                    error.close()
            finally:
                if temporary is not None: temporary.unlink(missing_ok=True)
            manifest.write(json.dumps(record) + '\n')
            manifest.flush()
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--urls', required=True, type=Path, help='exact URLs already checked against scope and exclusions')
    parser.add_argument('--output', required=True, type=Path, help='new target-local run directory; never overwrites an old run')
    parser.add_argument('--kind', required=True, choices=('javascript', 'sourcemap'))
    parser.add_argument('--interval', required=True, type=float, help='minimum seconds between requests, selected from target policy')
    parser.add_argument('--max-bytes', type=int, default=10_000_000)
    args = parser.parse_args()
    try:
        failures = collect(args.urls.read_text().splitlines(), args.output, args.kind, args.interval, args.max_bytes)
    except (OSError, ValueError) as error:
        parser.exit(2, f'Collection setup failed: {type(error).__name__}\n')
    print(f'Collection complete; failed URLs: {failures}. Inspect manifest before downstream work.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
