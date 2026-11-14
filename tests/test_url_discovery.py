import contextlib
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch, Mock
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / '.opencode/skills/recon-mode/scripts'
sys.path.insert(0, str(SCRIPTS))
try:
    import probe_urls as probe
finally:
    sys.path.pop(0)


@contextlib.contextmanager
def local_server():
    seen = []
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append((self.path, self.headers.get('X-Research')))
            if self.path == '/broken':
                self.send_response(200)
                self.send_header('Transfer-Encoding', 'chunked')
                self.end_headers()
                self.wfile.write(b'Q\r\nnot-a-chunk\r\n')
                self.close_connection = True
                return
            status = {'/ok': 200, '/restricted': 403, '/redirect': 302}.get(self.path, 404)
            body = {'/ok': b'{"openapi":"3.0.0"}', '/restricted': b'{"reason":"private-route"}'}.get(self.path, b'not-found')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            if status == 302: self.send_header('Location', '/must-not-follow')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with patch.dict(os.environ, {'NO_PROXY': '127.0.0.1,localhost'}):
            yield f'http://127.0.0.1:{server.server_port}', seen
    finally:
        server.shutdown(); server.server_close(); thread.join()


class UrlProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'run'

    def test_denials_and_not_found_preserved_without_redirects(self):
        with local_server() as (base, seen):
            urls = [base + path for path in ('/ok', '/restricted', '/missing', '/redirect')]
            self.assertEqual(probe.probe(urls, self.output, 0, 1000, {'X-Research': 'fixture-user'}), 0)
            self.assertEqual(seen, [(p, 'fixture-user') for p in ('/ok', '/restricted', '/missing', '/redirect')])
        rows = [json.loads(x) for x in (self.output / 'responses.jsonl').read_text().splitlines()]
        self.assertEqual([x['http_status'] for x in rows], [200, 403, 404, 302])
        self.assertEqual(len({x['file'] for x in rows}), 4)
        for row in rows:
            self.assertEqual(row['sha256'], hashlib.sha256((self.output / row['file']).read_bytes()).hexdigest())
            self.assertFalse(row['truncated'])
        summary = json.loads((self.output / 'run.json').read_text())
        self.assertTrue(summary['completed'])
        self.assertEqual(summary['responses'], 4)
        self.assertEqual(summary['errors'], 0)
        self.assertEqual(summary['manifest_sha256'], hashlib.sha256((self.output / 'responses.jsonl').read_bytes()).hexdigest())
        self.assertNotIn('fixture-user', (self.output / 'run.json').read_text())
        self.assertNotIn('fixture-user', (self.output / 'responses.jsonl').read_text())
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaises(FileExistsError): probe.probe(urls, self.output, 0, 1000)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})

    def test_truncation_is_explicit(self):
        with local_server() as (base, _): probe.probe([base + '/ok'], self.output, 0, 3)
        row = json.loads((self.output / 'responses.jsonl').read_text())
        self.assertTrue(row['truncated'])
        self.assertEqual(row['bytes'], 3)
        self.assertEqual((self.output / row['file']).read_bytes(), b'{"o')

    def test_malformed_transfer_is_partial_not_a_negative_result(self):
        with local_server() as (base, _):
            self.assertEqual(probe.probe([base + '/ok', base + '/broken'], self.output, 0, 100), 1)
        rows = [json.loads(x) for x in (self.output / 'responses.jsonl').read_text().splitlines()]
        self.assertEqual(rows[0]['outcome'], 'response')
        self.assertEqual(rows[1]['outcome'], 'transport-or-storage-error')
        self.assertEqual(json.loads((self.output / 'run.json').read_text())['status'], 'partial')

    def test_transport_errors_do_not_log_private_exception_messages(self):
        opener = Mock()
        opener.open.side_effect = urllib.error.URLError('private-value-998')
        with patch.object(probe.urllib.request, 'build_opener', return_value=opener):
            self.assertEqual(probe.probe(['https://example.invalid/a'], self.output, 0, 100), 1)
        self.assertEqual(json.loads((self.output / 'run.json').read_text())['status'], 'failed')
        self.assertNotIn('private-value-998', (self.output / 'responses.jsonl').read_text())

    def test_interruption_leaves_run_incomplete(self):
        opener = Mock()
        opener.open.side_effect = KeyboardInterrupt()
        with patch.object(probe.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaises(KeyboardInterrupt): probe.probe(['https://example.invalid/a'], self.output, 0, 100)
        self.assertFalse(json.loads((self.output / 'run.json').read_text())['completed'])

    def test_invalid_inputs_make_no_requests_or_output(self):
        invalid = [([], 0, 10, None), (['file:///tmp/x'], 0, 10, None),
                   (['https://example.invalid/a'], -1, 10, None),
                   (['https://example.invalid/a'], 0, 0, None),
                   (['https://example.invalid/a'], 0, 10, {'Cookie': 'secret'}),
                   (['https://example.invalid/a'], 0, 10, {'X-Research': 'bad\r\nheader'})]
        with patch.object(probe.urllib.request, 'build_opener') as build:
            for urls, interval, limit, headers in invalid:
                with self.subTest(urls=urls, headers=headers), self.assertRaises(ValueError):
                    probe.probe(urls, self.output, interval, limit, headers)
            build.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_cli_bom_files_and_invalid_header_file(self):
        with local_server() as (base, seen):
            (self.root / 'urls.txt').write_text(base + '/restricted\n', encoding='utf-8-sig')
            (self.root / 'headers.json').write_text(json.dumps({'X-Research': 'fixture-cli'}), encoding='utf-8-sig')
            from urllib.parse import urlsplit
            local = urlsplit(base)
            (self.root/'scope-policy.json').write_text(json.dumps({
                'version':1,'policy_id':'synthetic-loopback','source':'local test fixture',
                'allow':[{'host':local.hostname,'schemes':['http'],'ports':[local.port]}],
                'deny':[],'min_interval':0,'max_requests':10,'max_bytes':10000000}))
            args = [sys.executable, str(SCRIPTS / 'probe_urls.py'), '--urls', str(self.root / 'urls.txt'),
                    '--scope-policy', str(self.root/'scope-policy.json'), '--output', str(self.output), '--interval', '0', '--headers-file', str(self.root / 'headers.json')]
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(seen, [('/restricted', 'fixture-cli')])
            self.assertNotIn('fixture-cli', result.stdout + result.stderr)
            (self.root / 'headers.json').write_text('[]')
            args[args.index('--output') + 1] = str(self.root / 'bad-run')
            bad = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertFalse((self.root / 'bad-run').exists())
            self.assertEqual(len(seen), 1)


@unittest.skipUnless(shutil.which('ffuf') and shutil.which('bash'), 'ffuf and bash required for documented command integration')
class DocumentedFfufTests(unittest.TestCase):
    def test_exact_documented_example_preserves_403_and_404(self):
        document = (ROOT / '.opencode/skills/recon-mode/SKILL_FILES/RECON/15_content_discovery_fuzzing.md').read_text()
        command = re.search(r'```bash\n(.*?)\n```', document, re.S).group(1)
        with tempfile.TemporaryDirectory() as temp, local_server() as (base, seen):
            root = Path(temp)
            wordlist = root / 'paths.txt'; wordlist.write_text('ok\nrestricted\nmissing\n')
            env = {**os.environ, 'BASE_URL': base, 'APPROVED_PATHS': str(wordlist),
                   'RUN': str(root / 'run'), 'REQUESTS_PER_SECOND': '10',
                   'IDENTIFICATION_HEADER': 'X-Research: fixture-ffuf',
                   'XDG_CONFIG_HOME': str(root / 'config'), 'NO_PROXY': '127.0.0.1,localhost'}
            result = subprocess.run(['bash', '-c', command], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads((root / 'run/results.json').read_text())
            self.assertEqual(sorted(x['status'] for x in output['results']), [200, 403, 404])
            self.assertEqual(sorted(seen), sorted((p, 'fixture-ffuf') for p in ('/ok', '/restricted', '/missing')))
            self.assertEqual((root / 'run/completion.txt').read_text().strip(), 'exit=0')
            saved = (root / 'run/results.json').read_bytes()
            rerun = subprocess.run(['bash', '-c', command], env=env, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(rerun.returncode, 0)
            self.assertEqual(saved, (root / 'run/results.json').read_bytes())


if __name__ == '__main__': unittest.main()
