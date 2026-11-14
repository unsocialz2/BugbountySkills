#!/usr/bin/env python3
"""Fail-closed, offline URL/method/budget checks for the bundled HTTP collectors.

This deliberately conservative policy is not a scope inference engine, DNS/IP
isolation, browser gate, or a sandbox for unrelated commands. Redirects remain
unfollowed by the collectors. Build policies from the designated program rules.
"""
import argparse
import hashlib
import ipaddress
import json
import math
from pathlib import Path
import re
import urllib.parse


class ScopeDenied(ValueError):
    """Policy absent, ambiguous, invalid or not permitting the requested action."""


def _host(value, wildcard=False):
    if not isinstance(value, str) or not value or value != value.strip():
        raise ScopeDenied('invalid policy host')
    star = wildcard and value.startswith('*.')
    raw = value[2:] if star else value
    if any(x in raw for x in ('*', '%', '/', '\\', '@', '#', '?')) or raw.endswith('.'):
        raise ScopeDenied('ambiguous host')
    try:
        normalized = str(ipaddress.ip_address(raw))
        if star:
            raise ScopeDenied('wildcard IP is unsupported')
    except ValueError:
        if ':' in raw or re.fullmatch(r'(?:0[xX][0-9a-fA-F]+|[0-9]+)(?:\.(?:0[xX][0-9a-fA-F]+|[0-9]+))*', raw):
            raise ScopeDenied('noncanonical address')
        try:
            normalized = raw.encode('idna').decode('ascii').lower()
        except UnicodeError as exc:
            raise ScopeDenied('invalid IDNA host') from exc
        if re.fullmatch(r'[0-9.]+', normalized):
            raise ScopeDenied('IDNA numeric address is unsupported')
        labels = normalized.split('.')
        if (len(normalized) > 253 or len(labels) < 2 or
                any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', x) for x in labels)):
            raise ScopeDenied('invalid DNS host')
    return ('*.' if star else '') + normalized


def _path(raw):
    # Over-approximate common decoders for denial matching. Do not try to predict
    # an arbitrary server's parser; ambiguous path-scoped actions are rejected.
    if not isinstance(raw, str) or not raw.startswith('/'):
        raise ScopeDenied('absolute path required')
    value = raw
    ambiguous = False
    for _ in range(5):
        if re.search(r'%(?![0-9a-fA-F]{2})', value):
            raise ScopeDenied('malformed percent encoding')
        try:
            decoded = urllib.parse.unquote(value, errors='strict')
        except UnicodeError as exc:
            raise ScopeDenied('invalid path encoding') from exc
        if decoded == value:
            break
        if re.search(r'%(?:2f|5c|2e|3b|3f|23|25)', value, re.I):
            ambiguous = True
        value = decoded
    else:
        raise ScopeDenied('excessive decoding depth')
    if any(ord(c) < 32 or ord(c) == 127 for c in value) or any(c in value for c in ('?', '#')):
        raise ScopeDenied('path contains decoded controls or separators')
    if '\\' in value or ';' in value or '//' in value:
        ambiguous = True
    value = value.replace('\\', '/')
    segments = []
    for part in value.split('/'):
        if part in ('', '.'):
            if part == '.': ambiguous = True
            continue
        if part == '..':
            ambiguous = True
            if segments: segments.pop()
        else:
            segments.append(part)
    normalized = '/' + '/'.join(segments)
    if normalized != '/' and value.endswith('/'):
        normalized += '/'
    return normalized, ambiguous


def normalize_url(url):
    if not isinstance(url, str) or not url or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url):
        raise ScopeDenied('invalid URL characters')
    if '\\' in url or '#' in url:
        raise ScopeDenied('backslash or fragment in URL')
    try:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username is not None or parsed.password is not None:
            raise ScopeDenied('HTTP(S) URL without userinfo required')
        if '%' in parsed.netloc:
            raise ScopeDenied('encoded authority')
        host = _host(parsed.hostname)
        port = parsed.port if parsed.port is not None else (443 if parsed.scheme == 'https' else 80)
        # An empty explicit port is parser-dependent; do not silently default it.
        if parsed.netloc.endswith(':'):
            raise ScopeDenied('empty port')
        if not 1 <= port <= 65535:
            raise ScopeDenied('invalid port')
        path, ambiguous = _path(parsed.path or '/')
    except (ValueError, UnicodeError) as exc:
        if isinstance(exc, ScopeDenied): raise
        raise ScopeDenied('invalid URL authority') from exc
    return parsed.scheme, host, port, path, ambiguous


def _rule(raw):
    allowed = {'host', 'schemes', 'ports', 'methods', 'path', 'path_prefix'}
    if not isinstance(raw, dict) or set(raw) - allowed or 'host' not in raw:
        raise ScopeDenied('invalid rule fields')
    result = dict(raw)
    result['host'] = _host(raw['host'], wildcard=True)
    schemes = raw.get('schemes', ['https'])
    if not isinstance(schemes, list) or not schemes or any(s not in ('http', 'https') for s in schemes):
        raise ScopeDenied('invalid schemes')
    result['schemes'] = schemes
    ports = raw.get('ports', [443])
    if not isinstance(ports, list) or not ports or any(type(p) is not int or not 1 <= p <= 65535 for p in ports):
        raise ScopeDenied('invalid ports')
    result['ports'] = ports
    methods = raw.get('methods', ['GET'])
    if not isinstance(methods, list) or not methods or any(not isinstance(m, str) or not re.fullmatch('[A-Z]+', m) for m in methods):
        raise ScopeDenied('invalid methods')
    result['methods'] = methods
    if 'path' in raw and 'path_prefix' in raw:
        raise ScopeDenied('choose path or path_prefix')
    for key in ('path', 'path_prefix'):
        if key in raw:
            path, ambiguous = _path(raw[key])
            if ambiguous or '?' in raw[key] or '#' in raw[key] or '%' in raw[key]:
                raise ScopeDenied('policy paths must be canonical literals')
            result[key] = path
    return result


def _matches(rule, parts, method, allow=False):
    scheme, host, port, path, ambiguous = parts
    expected = rule['host']
    if expected.startswith('*.'):
        host_ok = host.endswith('.' + expected[2:]) and host != expected[2:]
    else:
        host_ok = host == expected
    if not host_ok or scheme not in rule['schemes'] or port not in rule['ports'] or method not in rule['methods']:
        return False
    # Refuse ambiguous path-scoped allows; denies still inspect folded paths.
    if allow and ambiguous and ('path' in rule or 'path_prefix' in rule):
        return False
    if 'path' in rule:
        return path == rule['path']
    if 'path_prefix' in rule:
        prefix = rule['path_prefix'].rstrip('/')
        return path == prefix or path.startswith(prefix + '/')
    return True


class ScopePolicy:
    def __init__(self, raw):
        fields = {'version', 'policy_id', 'source', 'allow', 'deny', 'min_interval', 'max_requests', 'max_bytes'}
        if not isinstance(raw, dict) or set(raw) != fields or type(raw['version']) is not int or raw['version'] != 1:
            raise ScopeDenied('invalid policy schema/version')
        if any(not isinstance(raw[k], str) or not raw[k].strip() for k in ('policy_id', 'source')):
            raise ScopeDenied('policy provenance required')
        for key in ('allow', 'deny'):
            if not isinstance(raw[key], list) or (key == 'allow' and not raw[key]):
                raise ScopeDenied('explicit allow rules required')
        self.allow = [_rule(r) for r in raw['allow']]
        self.deny = [_rule(r) for r in raw['deny']]
        if (isinstance(raw['min_interval'], bool) or not isinstance(raw['min_interval'], (int, float)) or
                not math.isfinite(raw['min_interval']) or raw['min_interval'] < 0):
            raise ScopeDenied('invalid minimum interval')
        if any(type(raw[k]) is not int or raw[k] <= 0 for k in ('max_requests', 'max_bytes')):
            raise ScopeDenied('invalid request/byte budget')
        self.raw = raw
        self.sha256 = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

    @classmethod
    def load(cls, path):
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result: raise ScopeDenied('duplicate JSON policy key')
                result[key] = value
            return result
        return cls(json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique))

    def permits(self, url, method='GET'):
        if not isinstance(method, str) or method != method.upper():
            raise ScopeDenied('canonical method required')
        parts = normalize_url(url)
        if parts[4]:
            for rule in self.allow + self.deny:
                if ('path' in rule or 'path_prefix' in rule) and _matches(
                        {k: v for k, v in rule.items() if k not in ('path', 'path_prefix')}, parts, method):
                    raise ScopeDenied('ambiguous path under path-restricted scope')
        if any(_matches(r, parts, method) for r in self.deny):
            raise ScopeDenied('explicit scope exclusion')
        if not any(_matches(r, parts, method, allow=True) for r in self.allow):
            raise ScopeDenied('outside explicit scope')
        return url

    def preflight(self, urls, interval, max_bytes, method='GET'):
        if (isinstance(interval, bool) or not isinstance(interval, (int, float)) or not math.isfinite(interval) or
                interval < self.raw['min_interval'] or type(max_bytes) is not int or max_bytes <= 0 or max_bytes > self.raw['max_bytes']):
            raise ScopeDenied('request rate/byte budget exceeds policy')
        if not isinstance(urls, (list, tuple)) or not urls or len(urls) > self.raw['max_requests']:
            raise ScopeDenied('request count exceeds policy')
        for url in urls:
            self.permits(url, method)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', required=True, type=Path)
    parser.add_argument('--urls', required=True, type=Path)
    parser.add_argument('--interval', required=True, type=float)
    parser.add_argument('--max-bytes', type=int, default=1000000)
    parser.add_argument('--method', default='GET')
    args = parser.parse_args()
    try:
        policy = ScopePolicy.load(args.policy)
        urls = list(dict.fromkeys(u.strip() for u in args.urls.read_text(encoding='utf-8-sig').splitlines() if u.strip()))
        policy.preflight(urls, args.interval, args.max_bytes, args.method)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Scope preflight refused: {type(exc).__name__}\n')
    print(json.dumps({'permitted_urls': len(urls), 'policy_sha256': policy.sha256, 'network_calls': 0}))


if __name__ == '__main__':
    main()
