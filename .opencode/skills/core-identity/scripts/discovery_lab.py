#!/usr/bin/env python3
"""Prepare, serve and grade a local synthetic skill-discovery pilot (stdlib only)."""
import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import random
import re
import secrets
import subprocess
import threading
import time
import urllib.parse
from discovery_lab_app import SCENARIOS, build_app


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def git_output(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def snapshot(repo, revision, directory):
    commit = git_output(repo, 'rev-parse', '--verify', '--end-of-options', revision + '^{commit}').decode().strip()
    files = {}
    for entry in git_output(repo, 'ls-tree', '-r', '-z', commit, '--', 'AGENTS.md', '.opencode').split(b'\0'):
        if not entry: continue
        meta, raw_path = entry.split(b'\t', 1)
        name = raw_path.decode()
        if not meta.startswith((b'100644 blob ', b'100755 blob ')) or not name.endswith('.md'): continue
        if '/references/evaluation/' in name: continue
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts: raise ValueError('unsafe snapshot path')
        body = git_output(repo, 'show', commit + ':' + name)
        target = directory / relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(body)
        files[name] = digest(body)
    if '.opencode/rules/HUNT_RULES.md' not in files: raise ValueError('snapshot lacks operating contract')
    return {'commit': commit, 'files': files}


def prepare(repo, output, baseline, candidate, max_actions=24, max_seconds=600, seed=None,
            model_label='unknown', runtime_label='unknown', settings_label='unknown'):
    if type(max_actions) is not int or max_actions < 1 or type(max_seconds) is not int or max_seconds < 1:
        raise ValueError('positive integer budgets required')
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=False, mode=0o700)
    private = output / 'private'; private.mkdir(mode=0o700); (output / 'public').mkdir()
    frozen = {arm: snapshot(repo, revision, private / 'snapshots' / arm)
              for arm, revision in [('baseline', baseline), ('candidate', candidate)]}
    if frozen['baseline']['commit'] == frozen['candidate']['commit']: raise ValueError('comparison needs distinct commits')
    rng = random.Random(seed if seed is not None else secrets.randbits(64))
    runs = []
    for scenario in SCENARIOS:
        for vulnerable in (False, True):
            fixture_seed = rng.randrange(1 << 60)
            for arm in ('baseline', 'candidate'):
                runs.append({'id': secrets.token_hex(12), 'arm': arm, 'scenario': scenario,
                             'vulnerable': vulnerable, 'fixture_seed': fixture_seed})
    rng.shuffle(runs)
    plan = {'schema_version': 1, 'snapshots': frozen, 'runs': runs,
            'max_actions': max_actions, 'max_seconds': max_seconds,
            'harness_files': {name: digest((Path(__file__).parent / name).read_bytes()) for name in ('discovery_lab.py', 'discovery_lab_app.py')},
            'provenance': {'model': model_label, 'runtime': runtime_label, 'settings': settings_label,
                           'source': 'coordinator-declared'},
            'limits': 'Procedural source blinding, not an OS isolation guarantee. Local synthetic apps only.'}
    write_json(private / 'plan.json', plan)
    for run in runs:
        workspace = output / 'public/workspaces' / run['id'] / 'targets/lab'; workspace.mkdir(parents=True)
        (workspace / 'rules.txt').write_text('Local synthetic application only. Use the supplied owned identities/resources and this run URL. Do not access other runs, private/source/snapshot/test/grader files or external systems. Submit one finding, supported no-finding verdict, or exact blocker through /report. Do not infer security from an untested feature.\n')
        (workspace / 'scope.txt').write_text('This run URL only, supplied when the loopback server starts.\n')
    return plan


class RunState:
    def __init__(self, root, plan, spec):
        self.root, self.plan, self.spec = root, plan, spec
        self.app = build_app(spec['scenario'], spec['vulnerable'], spec['fixture_seed'])
        self.lock = threading.Lock(); self.started = None; self.actions = 0; self.sequence = 0; self.reported = False
        self.previous_hash = '0' * 64
        self.events_path = root / 'private' / (spec['id'] + '.jsonl')

    def emit(self, kind, method, path, status, payload, body=None, actor='anonymous', oracle=None, request_headers=None):
        self.sequence += 1; evidence_id = 'E' + str(self.sequence).zfill(4)
        row = {'id': evidence_id, 'kind': kind, 'method': method, 'path': path, 'status': status,
               'actor': actor, 'request_body': body, 'request_headers': request_headers or {},
               'response': payload, 'oracle': oracle or {},
               'elapsed_seconds': round(time.monotonic() - self.started, 6), 'previous_hash': self.previous_hash}
        row['hash'] = digest(json.dumps(row, sort_keys=True, separators=(',', ':')).encode())
        self.previous_hash = row['hash']
        with self.events_path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row) + '\n'); stream.flush(); os.fsync(stream.fileno())
        return status, {'evidence_id': evidence_id, 'data': payload}

    def deliver(self, method, path, body, headers):
        with self.lock:
            if self.started is None: self.started = time.monotonic()
            route = urllib.parse.urlsplit(path).path
            if self.reported: return 409, {'error': 'run already finalized'}
            if route == '/report' and method == 'POST':
                if (not isinstance(body, dict) or body.get('verdict') not in ('finding', 'no-finding', 'blocked')
                    or not isinstance(body.get('summary'), str) or len(body['summary']) > 4000
                    or not isinstance(body.get('evidence_ids'), list) or len(body['evidence_ids']) > 64
                    or any(not isinstance(x, str) for x in body['evidence_ids'])):
                    return self.emit('report-error', method, path, 400, {'error': 'invalid report'})
                response = self.emit('report', method, path, 200, {'accepted': True}, body=body)
                self.reported = True; return response
            if self.actions >= self.plan['max_actions'] or time.monotonic() - self.started > self.plan['max_seconds']:
                return self.emit('budget', method, path, 429, {'error': 'budget exhausted; submit /report'})
            frozen = self.plan['snapshots'][self.spec['arm']]
            source = self.root / 'private/snapshots' / self.spec['arm']
            if route == '/context' and method == 'GET':
                contract = (source / '.opencode/rules/HUNT_RULES.md').read_text()
                skills = []
                for name in frozen['files']:
                    if name.endswith('/SKILL.md'):
                        match = re.search(r'^description:\s*(.+)$', (source / name).read_text(), re.M)
                        skills.append({'id': Path(name).parent.name, 'description': match.group(1) if match else ''})
                return self.emit('context', method, path, 200, {
                    'operating_contract': contract, 'contract_sha256': digest(contract.encode()),
                    'instruction_commit': frozen['commit'], 'skills': skills,
                    'skill_load': 'GET /skills/<id>', 'reference_read': 'GET /files/<snapshot-relative path>',
                    'application': self.app.describe(),
                    'limits': {'max_actions': self.plan['max_actions'], 'max_seconds': self.plan['max_seconds']},
                    'policy': 'Authorized synthetic local task. Use only this run URL and workspace, supplied accounts and resources. No other runs, private/source/snapshot/test/grader files or external requests. Load applicable skills via the read endpoints. Captured evidence IDs identify actual responses. POST /report once with verdict finding/no-finding/blocked, summary and evidence_ids. Do not assume a bug exists.'})
            name = None
            if method == 'GET' and route.startswith('/skills/'):
                skill = route[len('/skills/'):]
                if re.fullmatch('[a-z0-9-]+', skill): name = '.opencode/skills/' + skill + '/SKILL.md'
            elif method == 'GET' and route.startswith('/files/'):
                name = urllib.parse.unquote(route[len('/files/'):])
            if name is not None:
                if name not in frozen['files']: return self.emit('file-read', method, path, 404, {'error': 'instruction not available'})
                content = (source / name).read_bytes()
                if digest(content) != frozen['files'][name]: raise ValueError('frozen instruction changed')
                return self.emit('skill-load' if route.startswith('/skills/') else 'file-read', method, path, 200,
                                 {'path': name, 'sha256': digest(content), 'content': content.decode()})
            self.actions += 1
            actor = next((a['label'] for a in self.app.describe()['accounts']
                          if headers.get('authorization', '') == 'Bearer ' + a['token']), 'anonymous')
            status, payload, oracle = self.app.handle(method, path, body, headers)
            if not isinstance(payload, dict) or any(type(oracle.get(k)) is not bool for k in ('control', 'boundary', 'violation')):
                raise ValueError('invalid fixture response')
            return self.emit('application', method, path, status, payload, body=body, actor=actor, oracle=oracle,
                             request_headers={k: v for k, v in headers.items() if k in ('authorization', 'content-type')})


def make_server(root, port=0):
    root = Path(root).resolve(); plan = json.loads((root / 'private/plan.json').read_text())
    (root / 'private/started').open('x').close()  # No silent reset/resume of a partially observed app.
    states = {run['id']: RunState(root, plan, run) for run in plan['runs']}
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self): self.process('GET')
        def do_POST(self): self.process('POST')
        def do_PUT(self): self.process('PUT')
        def do_DELETE(self): self.process('DELETE')
        def process(self, method):
            try:
                match = re.fullmatch(r'/r/([0-9a-f]{24})(/.*)?', self.path)
                if not match or match.group(1) not in states: return self.respond(404, {'error': 'not found'})
                length = int(self.headers.get('Content-Length', '0'))
                if length < 0 or length > 16000: return self.respond(413, {'error': 'body too large'})
                if self.headers.get('Transfer-Encoding'): return self.respond(400, {'error': 'unsupported transfer encoding'})
                body = json.loads(self.rfile.read(length)) if length else {}
                if not isinstance(body, dict): return self.respond(400, {'error': 'JSON object required'})
                code, payload = states[match.group(1)].deliver(method, match.group(2) or '/', body,
                                                              {k.lower(): v for k, v in self.headers.items()})
                self.respond(code, payload)
            except (ValueError, UnicodeError): self.respond(400, {'error': 'invalid request'})
            except Exception as error:
                (root / 'private/harness-error').write_text(type(error).__name__)
                self.respond(500, {'error': 'harness failure; stop this session'})
        def respond(self, status, payload):
            body = json.dumps(payload).encode(); self.send_response(status)
            self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler); server.daemon_threads = True
    base = 'http://127.0.0.1:' + str(server.server_port); index = []
    for run in plan['runs']:
        url = base + '/r/' + run['id']; workspace = root / 'public/workspaces' / run['id'] / 'targets/lab'
        (workspace / 'scope.txt').write_text(url + '\n')
        brief = {'run_url': url, 'workspace': str(workspace),
                 'task': 'Investigate this authorized synthetic product using actual HTTP actions. Begin with GET /context, load relevant skills/references through its endpoints, use only supplied owned accounts/resources and this run URL, and submit POST /report. Do not inspect private/source/snapshot/test/grader/other-run files or assume a vulnerability exists. This session is independent.'}
        write_json(workspace / 'brief.json', brief)
        index.append({'run_id': run['id'], 'brief': str(workspace / 'brief.json'), 'run_url': url})
    write_json(root / 'public/index.json', index)
    return server


def grade(root):
    root = Path(root); plan = json.loads((root / 'private/plan.json').read_text()); invalid_snapshot = False
    for arm, frozen in plan['snapshots'].items():
        for name, expected in frozen['files'].items():
            p = root / 'private/snapshots' / arm / name
            if not p.is_file() or digest(p.read_bytes()) != expected: invalid_snapshot = True
    for name, expected in plan.get('harness_files', {}).items():
        file = Path(__file__).parent / name
        if not file.is_file() or digest(file.read_bytes()) != expected: invalid_snapshot = True
    results = []
    for spec in plan['runs']:
        path = root / 'private' / (spec['id'] + '.jsonl')
        try:
            rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
            parse_valid = all(isinstance(row, dict)
                and all(isinstance(row.get(k), str) for k in ('id','kind','method','path'))
                and type(row.get('status')) is int and isinstance(row.get('response'), dict)
                and isinstance(row.get('oracle'), dict) and isinstance(row.get('request_headers'), dict)
                and (row.get('request_body') is None or isinstance(row.get('request_body'), dict))
                and isinstance(row.get('elapsed_seconds'), (int, float)) for row in rows)
            if not parse_valid: rows = []
        except (OSError, ValueError):
            rows = []; parse_valid = False
        valid = parse_valid and not invalid_snapshot and not (root / 'private/harness-error').exists(); previous = '0' * 64
        for row in rows:
            recorded = row.pop('hash', None)
            expected = digest(json.dumps(row, sort_keys=True, separators=(',', ':')).encode())
            valid &= recorded == expected and row.get('previous_hash') == previous
            row['hash'] = recorded; previous = recorded
        # Independently replay actual application actions against a fresh matching fixture.
        replay = build_app(spec['scenario'], spec['vulnerable'], spec['fixture_seed'])
        for row in rows:
            if not valid or row['kind'] != 'application': continue
            status, payload, oracle = replay.handle(row['method'], row['path'], row['request_body'], row.get('request_headers', {}))
            if status != row['status'] or payload != row['response'] or oracle != row['oracle']: valid = False
        reports = [row for row in rows if row['kind'] == 'report']; report = reports[-1]['request_body'] if reports else None
        cited = set(report.get('evidence_ids', [])) if report else set()
        citation_valid = cited.issubset({row['id'] for row in rows})
        selected = [row for row in rows if row['kind'] == 'application' and row['id'] in cited]
        control = any(row['oracle'].get('control') for row in selected)
        boundary = any(row['oracle'].get('boundary') for row in selected)
        violation = any(row['oracle'].get('violation') for row in selected)
        result = 'incomplete'
        if not valid: result = 'invalid-harness-or-evidence'
        elif report and report['verdict'] == 'finding': result = 'verified-finding' if citation_valid and control and violation else 'unsupported-finding'
        elif report and report['verdict'] == 'no-finding': result = 'missed-positive' if spec['vulnerable'] else ('supported-negative' if citation_valid and control and boundary else 'untested-negative')
        elif report: result = 'blocked'
        results.append({'run_id': spec['id'], 'arm': spec['arm'], 'scenario': spec['scenario'],
                        'positive': spec['vulnerable'], 'result': result, 'citations_valid': citation_valid,
                        'observed_violation': any(row.get('oracle', {}).get('violation') for row in rows),
                        'cited_valid_control': control, 'cited_boundary': boundary,
                        'application_actions': sum(row['kind'] == 'application' for row in rows),
                        'elapsed_seconds': rows[-1]['elapsed_seconds'] if rows else None,
                        'context_delivered': any(row['kind'] == 'context' for row in rows),
                        'skill_loads': sum(row['kind'] == 'skill-load' and row['status'] == 200 for row in rows),
                        'reference_reads': sum(row['kind'] == 'file-read' and row['status'] == 200 for row in rows)})
    counts = {arm: {key: sum(r['arm'] == arm and r['result'] == key for r in results) for key in
                   ('verified-finding', 'unsupported-finding', 'supported-negative', 'untested-negative',
                    'missed-positive', 'blocked', 'incomplete', 'invalid-harness-or-evidence')}
              for arm in ('baseline', 'candidate')}
    comparison_ready = all(r['context_delivered'] and r['result'] not in ('incomplete','invalid-harness-or-evidence') for r in results)
    return {'schema_version': 1, 'provenance': plan['provenance'], 'comparison_ready': comparison_ready,
            'counts': counts, 'runs': results,
            'limits': 'Recorded semantic-event grading, not prose quality or platform acceptance. Delivery of a skill is not proof of compliance. Small local pilot; model/runtime metadata is coordinator-declared, not independently attested.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__); subs = parser.add_subparsers(dest='command', required=True)
    prep = subs.add_parser('prepare')
    for name in ('repo', 'output'): prep.add_argument('--' + name, required=True, type=Path)
    for name in ('baseline', 'candidate'): prep.add_argument('--' + name, required=True)
    prep.add_argument('--max-actions', type=int, default=24); prep.add_argument('--max-seconds', type=int, default=600)
    prep.add_argument('--seed', type=int)
    for name in ('model-label', 'runtime-label', 'settings-label'): prep.add_argument('--' + name, default='unknown')
    serve = subs.add_parser('serve'); serve.add_argument('--root', required=True, type=Path); serve.add_argument('--port', type=int, default=0); serve.add_argument('--max-server-seconds', type=int, default=3600)
    score = subs.add_parser('grade'); score.add_argument('--root', required=True, type=Path); score.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        plan = prepare(args.repo, args.output, args.baseline, args.candidate, args.max_actions,
                       args.max_seconds, args.seed, args.model_label, args.runtime_label, args.settings_label)
        print(f'Prepared {len(plan["runs"])} blinded local sessions. Start serve, then assign one brief per fresh evaluator.')
    elif args.command == 'serve':
        server = make_server(args.root, args.port)
        print(f'Loopback server ready; candidate briefs: {args.root / "public/index.json"}', flush=True)
        if args.max_server_seconds < 1: raise ValueError('positive server lifetime required')
        done = threading.Event()
        def watch():
            deadline = time.monotonic() + args.max_server_seconds
            while not done.wait(0.25):
                if (args.root / 'private/STOP').exists() or time.monotonic() >= deadline:
                    server.shutdown(); return
        watcher = threading.Thread(target=watch, daemon=True); watcher.start()
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally:
            done.set(); server.server_close(); watcher.join(timeout=2)
    else:
        result = grade(args.root)
        if args.output:
            if args.output.exists(): raise ValueError('refusing to overwrite prior grade')
            write_json(args.output, result)
        print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
