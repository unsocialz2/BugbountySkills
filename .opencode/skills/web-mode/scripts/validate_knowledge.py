#!/usr/bin/env python3
"""Offline web knowledge integrity checks; not a hunting-performance benchmark."""
import argparse
import json
from pathlib import Path
import re
import urllib.parse

ROOT = Path(__file__).resolve().parents[4]
WEB = ROOT / '.opencode/skills/web-mode'


def external_references(text):
    urls = re.findall(r'\[[^\]]+\]\((https?://[^\s)]+)\)', text)
    return sorted(set(u for u in urls if urllib.parse.urlsplit(u).hostname and
                      not urllib.parse.urlsplit(u).hostname.endswith('.invalid')))


def validate(root=ROOT):
    web = root / '.opencode/skills/web-mode'
    catalogue = json.loads((web / 'references/web-catalog.json').read_text())
    errors = []
    if catalogue.get('schema_version') != 1:
        errors.append('unsupported catalogue schema')
    entries = catalogue['methodologies']
    ids = [e['id'] for e in entries]
    if len(ids) != len(set(ids)):
        errors.append('duplicate methodology ID')
    known = set(ids) | set(catalogue['compatibility'])
    actual = {p.stem for p in (web / 'SKILL_FILES/VULNERABILITIES/WEB').glob('*.md')}
    if actual != known:
        errors.append(f'catalogue/file mismatch: {sorted(actual ^ known)}')
    router = (web / 'SKILL.md').read_text()
    if len(router.splitlines()) >= 500:
        errors.append('router is no longer concise')
    source_count = set()
    for e in entries:
        path = web / e['path']
        if not path.is_file():
            errors.append(f'missing methodology: {e["path"]}')
            continue
        text = path.read_text()
        if e['path'] not in router:
            errors.append(f'unrouted methodology: {e["id"]}')
        urls = external_references(text)
        source_count.update(urls)
        domains = {urllib.parse.urlsplit(u).hostname for u in urls}
        if len(urls) < 3 or len(domains) < 2:
            errors.append(f'insufficient primary-source diversity: {e["id"]}')
        if e['id'] != 'dependency_confusion' and not any(
                d == 'portswigger.net' or (d == 'github.com' and '/portswigger/' in u.lower())
                for u in urls for d in [urllib.parse.urlsplit(u).hostname]):
            errors.append(f'missing PortSwigger source: {e["id"]}')
        if urls != e.get('reference_urls'):
            errors.append(f'stale source index: {e["id"]}')
        for term in ('control', 'evidence', 'payload', 'reopen'):
            if term not in text.lower():
                errors.append(f'missing {term} discussion: {e["id"]}')
        if re.search(r'(?im)^## (?:SEVERITY & CVSS|IDENTITY IN THIS SKILL)', text):
            errors.append(f'legacy persona/scoring section: {e["id"]}')
        # Review executable blocks, not warnings explaining why old recipes fail.
        blocks = re.findall(r'^```[^\n]*\n(.*?)^```\s*$', text, re.M | re.S)
        for block in blocks:
            if re.search(r'(?i)\b(?:flushall|drop\s+table|xp_cmdshell)\b|/dev/tcp/|INTO\s+OUTFILE|/var/spool/cron', block):
                errors.append(f'destructive/persistent recipe: {e["id"]}')
    paths = list((web).rglob('*.md'))
    paths += list((root/'.opencode/skills/payloads').rglob('*.md'))
    paths += list((root/'.opencode/skills/api-mode').rglob('*.md'))
    for path in paths:
        # AI payload content is intentionally outside this web revision.
        if path.name in ('14-prompt-injection-llm.md', 'prompt_injection_payloads.md'):
            continue
        text = path.read_text()
        if len(re.findall(r'^```', text, re.M)) % 2:
            errors.append(f'unbalanced fences: {path.relative_to(root)}')
        for dest in re.findall(r'\[[^\]]+\]\(([^\s)]+)\)', text):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', dest) or dest.startswith('#'):
                continue
            local = urllib.parse.unquote(dest.split('#', 1)[0])
            if local and not (path.parent/local).exists():
                errors.append(f'broken local link: {path.relative_to(root)} -> {dest}')
    return {'ok': not errors, 'canonical_methodologies': len(entries),
            'compatibility_entries': len(catalogue['compatibility']),
            'distinct_reference_urls': len(source_count), 'errors': errors,
            'limits': 'Structure/links/regression constraints only; source truth, all payload execution and discovery performance are not certified.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f'Web knowledge integrity: {"PASS" if result["ok"] else "FAIL"}; '
              f'{result["canonical_methodologies"]} canonical guides; '
              f'{result["distinct_reference_urls"]} distinct reference URLs')
        for error in result['errors']:
            print(error)
        print(result['limits'])
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
