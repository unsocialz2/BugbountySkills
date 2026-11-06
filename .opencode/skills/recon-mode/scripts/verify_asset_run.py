#!/usr/bin/env python3
"""Verify a collector run locally without network requests or file changes."""
import argparse
import hashlib
import json
from pathlib import Path


def file_digest(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_run(directory):
    root = Path(directory)
    problems = []
    result = {'status': 'unverified', 'eligible_as_baseline': False, 'problems': problems}
    summary_path, manifest_path = root / 'run.json', root / 'manifest.jsonl'
    if summary_path.is_symlink() or manifest_path.is_symlink():
        problems.append('metadata-symlink')
        return result
    try:
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        if not isinstance(summary, dict) or type(summary.get('schema_version')) is not int or summary['schema_version'] != 1:
            raise ValueError()
        if summary.get('completed') is not True:
            problems.append('no-completion-record')
            return result
        kind = summary.get('kind')
        if kind not in ('javascript', 'sourcemap'):
            raise ValueError()
        counts = [summary.get(k) for k in ('requested', 'saved', 'failed')]
        if any(type(n) is not int or n < 0 for n in counts) or counts[0] == 0:
            raise ValueError()
        requested, saved, failed = counts
        expected_status = 'complete' if failed == 0 else ('failed' if saved == 0 else 'partial')
        if saved + failed != requested or summary.get('status') != expected_status:
            problems.append('summary-count-or-status-mismatch')
        raw_manifest = manifest_path.read_bytes()
        if hashlib.sha256(raw_manifest).hexdigest() != summary.get('manifest_sha256'):
            problems.append('manifest-hash-mismatch')
        rows = [json.loads(line) for line in raw_manifest.decode('utf-8').splitlines()]
        if not rows or any(not isinstance(row, dict) for row in rows):
            raise ValueError()
        urls = [row.get('url') for row in rows]
        if any(not isinstance(url, str) or not url for url in urls):
            raise ValueError()
        if len(set(urls)) != len(urls):
            problems.append('duplicate-url')
        digest = hashlib.sha256(json.dumps(urls, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
        if digest != summary.get('input_sha256'):
            problems.append('input-hash-mismatch')
        if len(rows) != requested or sum(row.get('status') == 'saved' for row in rows) != saved or sum(row.get('status') == 'failed' for row in rows) != failed:
            problems.append('manifest-count-mismatch')
        for row in rows:
            if row.get('kind') != kind:
                problems.append('artifact-kind-mismatch')
            if row.get('status') == 'failed':
                continue
            if row.get('status') != 'saved':
                problems.append('unknown-record-status')
                continue
            expected_name = hashlib.sha256(row['url'].encode()).hexdigest() + ('.js' if kind == 'javascript' else '.map')
            if row.get('file') != expected_name:
                problems.append('unexpected-artifact-path')
                continue
            artifact = root / expected_name
            if artifact.is_symlink():
                problems.append('artifact-symlink')
                continue
            if not artifact.is_file():
                problems.append('missing-artifact')
                continue
            if type(row.get('bytes')) is not int or artifact.stat().st_size != row['bytes']:
                problems.append('artifact-size-mismatch')
            if file_digest(artifact) != row.get('sha256'):
                problems.append('artifact-hash-mismatch')
        result.update(requested=requested, saved=saved, failed=failed)
        if not problems:
            result.update(status=expected_status, eligible_as_baseline=expected_status == 'complete')
    except FileNotFoundError:
        problems.append('missing-run-metadata')
    except (OSError, ValueError, UnicodeError, RecursionError):
        problems.append('unreadable-or-invalid-run')
    result['problems'] = sorted(set(problems))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='existing collector run directory')
    args = parser.parse_args()
    result = verify_run(args.directory)
    print(json.dumps(result, indent=2))
    return 0 if result['eligible_as_baseline'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
