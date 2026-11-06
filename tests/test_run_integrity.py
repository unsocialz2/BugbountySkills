import contextlib
import hashlib
import http.client
import http.server
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / '.opencode/skills/recon-mode/scripts'

def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

c, v = load('collect_assets'), load('verify_asset_run')

class RunIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / 'run'
        self.urls = ['https://example.invalid/a.js', 'https://example.invalid/b.js']

    def run_collection(self, fetcher=None):
        return c.collect(self.urls, self.out, 'javascript', 0, 10000,
                         fetcher=fetcher or (lambda url: (b'const x = 1;', 'text/javascript')))

    def summary(self):
        return json.loads((self.out / 'run.json').read_text())

    def test_complete_run_and_cli_are_read_only(self):
        self.assertEqual(self.run_collection(), 0)
        before = {p.name: p.read_bytes() for p in self.out.iterdir()}
        self.assertTrue(v.verify_run(self.out)['eligible_as_baseline'])
        result = subprocess.run([sys.executable, str(SCRIPTS / 'verify_asset_run.py'), str(self.out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.out.iterdir()})

    def test_changed_and_missing_artifacts_rejected(self):
        self.run_collection()
        artifact = next(self.out.glob('*.js'))
        original = artifact.read_bytes()
        artifact.write_bytes(b'x' * len(original))
        self.assertIn('artifact-hash-mismatch', v.verify_run(self.out)['problems'])
        artifact.unlink()
        self.assertIn('missing-artifact', v.verify_run(self.out)['problems'])
        self.assertFalse(v.verify_run(self.out)['eligible_as_baseline'])

    def test_truncated_and_changed_manifest_rejected(self):
        self.run_collection()
        manifest = self.out / 'manifest.jsonl'
        manifest.write_bytes(manifest.read_bytes().splitlines()[0] + b'\n')
        result = v.verify_run(self.out)
        self.assertIn('manifest-hash-mismatch', result['problems'])
        self.assertIn('manifest-count-mismatch', result['problems'])

    def test_interruption_never_becomes_complete(self):
        def fetch(url):
            if url.endswith('b.js'): raise KeyboardInterrupt()
            return b'let a = 1;', 'text/javascript'
        with self.assertRaises(KeyboardInterrupt): self.run_collection(fetch)
        self.assertFalse(self.summary()['completed'])
        self.assertIn('no-completion-record', v.verify_run(self.out)['problems'])
        self.assertEqual(len(list(self.out.glob('*.js'))), 1)

    def test_http_transport_failure_preserves_partial_run(self):
        def fetch(url):
            if url.endswith('b.js'): raise http.client.IncompleteRead(b'partial')
            return b'let a = 1;', 'text/javascript'
        self.assertEqual(self.run_collection(fetch), 1)
        result = v.verify_run(self.out)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['problems'], [])
        self.assertFalse(result['eligible_as_baseline'])

    def test_all_failed_is_distinct_from_empty_success(self):
        self.assertEqual(self.run_collection(lambda u: (b'<html>login</html>', 'text/html')), 2)
        result = v.verify_run(self.out)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['saved'], 0)
        self.assertFalse(result['eligible_as_baseline'])

    def test_legacy_and_bad_summary_are_unverified(self):
        self.out.mkdir()
        (self.out / 'manifest.jsonl').write_text('')
        self.assertFalse(v.verify_run(self.out)['eligible_as_baseline'])
        for bad in ['[]', '{', '{"schema_version":true,"completed":true}']:
            (self.out / 'run.json').write_text(bad)
            self.assertFalse(v.verify_run(self.out)['eligible_as_baseline'])

    def test_unexpected_artifact_path_is_not_followed(self):
        self.run_collection()
        manifest = self.out / 'manifest.jsonl'
        rows = [json.loads(line) for line in manifest.read_text().splitlines()]
        rows[0]['file'] = '../outside.js'
        manifest.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        summary = self.summary()
        summary['manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        (self.out / 'run.json').write_text(json.dumps(summary))
        self.assertIn('unexpected-artifact-path', v.verify_run(self.out)['problems'])

    def test_duplicate_rows_and_count_mismatch_rejected(self):
        self.run_collection()
        manifest = self.out / 'manifest.jsonl'
        row = manifest.read_text().splitlines()[0]
        manifest.write_text(row + '\n' + row + '\n')
        summary = self.summary()
        summary['manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        summary['saved'] = 1
        (self.out / 'run.json').write_text(json.dumps(summary))
        result = v.verify_run(self.out)
        self.assertIn('duplicate-url', result['problems'])
        self.assertIn('summary-count-or-status-mismatch', result['problems'])
        self.assertFalse(result['eligible_as_baseline'])

    def test_symlink_artifact_is_rejected(self):
        self.run_collection()
        artifact = next(self.out.glob('*.js'))
        outside = self.root / 'outside'
        outside.write_bytes(artifact.read_bytes())
        artifact.unlink()
        artifact.symlink_to(outside)
        self.assertIn('artifact-symlink', v.verify_run(self.out)['problems'])

    def test_invalid_headers_and_kind_do_not_start_collection(self):
        for headers in [{'X-Handle':'a\r\nX: b'}, {'Authorization':'secret'}, {'Cookie':'secret'}, {'Host':'evil'}, {'Accept-Encoding':'gzip'}, {'X-A':1}, {'x-a':'a','X-A':'b'}, []]:
            with self.subTest(headers=headers), self.assertRaises((ValueError, UnicodeError)):
                c.collect(self.urls, self.out, 'javascript', 0, 100, headers=headers,
                          fetcher=lambda u: (_ for _ in ()).throw(AssertionError('invalid input reached transport')))
        with self.assertRaises(ValueError): c.collect(self.urls, self.out, 'unknown', 0, 100)
        self.assertFalse(self.out.exists())
        with self.assertRaises(ValueError): c.checked_url('https://@example.invalid/a')

    def test_header_values_are_not_stored(self):
        c.collect(self.urls, self.out, 'javascript', 0, 100,
                  fetcher=lambda u:(b'let x=1;', 'text/javascript'), headers={'X-HackerOne-Handle':'private-marker-32'})
        for p in self.out.iterdir(): self.assertNotIn(b'private-marker-32',p.read_bytes())


@contextlib.contextmanager
def local_server():
    seen=[]
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append((self.path, self.headers.get('X-HackerOne-Handle')))
            if self.path=='/redirect':
                self.send_response(302)
                self.send_header('Location','/must-not-be-followed')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-Type','text/javascript')
                if self.path=='/encoded': self.send_header('Content-Encoding','gzip')
                self.end_headers()
                self.wfile.write(b'let x = 1;')
        def log_message(self,*args): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try: yield 'http://127.0.0.1:' + str(server.server_port),seen
    finally: server.shutdown();server.server_close();thread.join()


class TransportIntegrationTests(unittest.TestCase):
    def test_cli_headers_and_redirect_rejection(self):
        with tempfile.TemporaryDirectory() as temp, local_server() as (base,seen):
            root=Path(temp)
            (root/'urls.txt').write_text(base+'/a.js\n'+base+'/redirect\n')
            (root/'headers.json').write_text(json.dumps({'X-HackerOne-Handle':'fixture-handle'}))
            result=subprocess.run([sys.executable,str(SCRIPTS/'collect_assets.py'),'--urls',str(root/'urls.txt'),
                '--output',str(root/'run'),'--kind','javascript','--interval','0',
                '--headers-file',str(root/'headers.json')],capture_output=True,text=True)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertEqual(seen,[('/a.js','fixture-handle'),('/redirect','fixture-handle')])
            self.assertNotIn('fixture-handle',result.stdout+result.stderr)
            self.assertEqual(v.verify_run(root/'run')['status'],'partial')

    def test_unexpected_compression_is_not_saved_as_javascript(self):
        with tempfile.TemporaryDirectory() as temp, local_server() as (base,seen):
            out=Path(temp)/'run'
            self.assertEqual(c.collect([base+'/encoded'],out,'javascript',0,100),1)
            self.assertEqual(list(out.glob('*.js')),[])
            self.assertEqual(v.verify_run(out)['status'],'failed')

if __name__=='__main__': unittest.main()
