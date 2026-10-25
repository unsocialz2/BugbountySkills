import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collector', ROOT / '.opencode/skills/recon-mode/scripts/collect_assets.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'run'

    def collect(self, urls, fetcher, kind='javascript', max_bytes=10000):
        return c.collect(urls, self.out, kind, 0, max_bytes, fetcher)

    def test_distinct_urls_preserve_content_and_dedupe(self):
        urls = ['https://example.invalid/a.js', 'https://example.invalid/b.js']
        self.assertEqual(self.collect(urls + urls[:1], lambda u: (u.encode(), 'text/javascript')), 0)
        records = [json.loads(s) for s in (self.out/'manifest.jsonl').read_text().splitlines()]
        self.assertEqual(len(records), 2)
        self.assertNotEqual(records[0]['file'], records[1]['file'])
        for rec in records:
            self.assertEqual((self.out/rec['file']).read_bytes(), rec['url'].encode())
        with self.assertRaises(FileExistsError):
            self.collect(urls, lambda u: (b'replaced', 'text/javascript'))
        self.assertEqual((self.out/records[0]['file']).read_bytes(), urls[0].encode())

    def test_partial_failure_is_visible_and_does_not_erase_success(self):
        def fetch(u):
            if u.endswith('bad'): raise urllib.error.HTTPError(u, 404, 'missing', {}, None)
            return b'const good = 1;', 'application/javascript'
        self.assertEqual(self.collect(['https://example.invalid/good','https://example.invalid/bad'], fetch), 1)
        rows = [json.loads(x) for x in (self.out/'manifest.jsonl').read_text().splitlines()]
        self.assertEqual([r['status'] for r in rows], ['saved','failed'])
        self.assertEqual(rows[1]['http_status'], 404)
        self.assertEqual(len(list(self.out.glob('*.js'))), 1)

    def test_sourcemap_rejects_nonempty_html_and_bad_structure(self):
        for body in (b'<html>404</html>', b'{}', b'{"version":3}', b'{"version":true,"sources":[],"names":[],"mappings":""}'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                c.validate_body(body,'sourcemap','text/plain')
        basic = {'version':3,'sources':['a.js'],'names':[],'mappings':'AAAA'}
        for obj in (basic, {'version':3,'sections':[{'offset':{'line':0,'column':0},'map':basic}]}):
            c.validate_body(json.dumps(obj).encode(),'sourcemap','application/json')

    def test_common_error_pages_and_empty_js_rejected(self):
        for body,mime in [(b'', 'text/javascript'),(b'<html>login</html>','text/plain'),(b'error','text/html')]:
            with self.subTest(body=body), self.assertRaises(ValueError): c.validate_body(body,'javascript',mime)

    def test_no_redirect_and_invalid_urls(self):
        self.assertIsNone(c.NoRedirect().redirect_request(None,None,302,'',{},'https://other.invalid'))
        for url in ['file:///tmp/a', 'https://a.invalid/a#x', 'https://user:secret@a.invalid/a', 'https://a.invalid/a\nb', 'https://a.invalid:bad/a']:
            with self.subTest(url=url), self.assertRaises(ValueError): c.checked_url(url)

    def test_empty_input_and_invalid_limits_create_no_run(self):
        with self.assertRaises(ValueError): self.collect([],lambda u: None)
        for interval in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError): c.collect(['https://a.invalid'],self.out,'javascript',interval,10)
        self.assertFalse(self.out.exists())

    def test_oversized_response_not_saved(self):
        self.assertEqual(self.collect(['https://a.invalid/a'],lambda u:(b'x'*11,'text/javascript'),max_bytes=10),1)
        self.assertEqual(list(self.out.glob('*.js')),[])

    def test_spacing_and_no_redirect_follow_at_fetch_layer(self):
        with patch.object(c.time,'sleep') as sleep:
            self.collect(['https://a.invalid/a','https://a.invalid/b'],lambda u:(b'let x=1','text/javascript'))
            sleep.assert_called_once_with(0)
        class Response(io.BytesIO):
            status=200
            headers={'Content-Type':'text/javascript'}
        class Opener:
            def open(self, request, timeout):
                self.request=request
                return Response(b'abc')
        opener=Opener()
        self.assertEqual(c.fetch(opener,'https://a.invalid/a',10),(b'abc','text/javascript'))
        with self.assertRaises(ValueError): c.fetch(opener,'https://a.invalid/a',2)

if __name__ == '__main__': unittest.main()
