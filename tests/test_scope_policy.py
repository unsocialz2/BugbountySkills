"""Scope/budget regression tests; all transports are mocked or loopback fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT/'.opencode/skills/recon-mode/scripts'
sys.path.insert(0, str(SCRIPTS))
try:
    from scope_policy import ScopeDenied, ScopePolicy, normalize_url
    import collect_assets as collector
    import probe_urls as probe
finally:
    sys.path.pop(0)


def raw_policy():
    return {'version':1,'policy_id':'owned-fixture','source':'synthetic designated policy',
            'allow':[{'host':'app.example.invalid'}, {'host':'*.labs.example.invalid'}],
            'deny':[{'host':'app.example.invalid','path_prefix':'/excluded'}],
            'min_interval':0.1,'max_requests':3,'max_bytes':1000}


class PolicyTests(unittest.TestCase):
    def setUp(self): self.policy=ScopePolicy(raw_policy())

    def test_hosts_subdomain_boundary_and_deny_precedence(self):
        for url in ('https://app.example.invalid/', 'https://a.labs.example.invalid/x',
                    'https://a.b.labs.example.invalid/x','https://APP.EXAMPLE.INVALID/?name=x'):
            with self.subTest(url=url):self.assertEqual(self.policy.permits(url),url)
        for url in ('https://labs.example.invalid/', 'https://app.example.invalid.evil.invalid/',
                    'https://notapp.example.invalid/', 'https://app.example.invalid/excluded',
                    'https://app.example.invalid/excluded/x','https://app.example.invalid/%65xcluded/x'):
            with self.subTest(url=url),self.assertRaises(ScopeDenied):self.policy.permits(url)
        self.policy.permits('https://app.example.invalid/excluded-other')

    def test_authority_scheme_port_and_method(self):
        denied=('http://app.example.invalid/','https://app.example.invalid:444/',
                'https://user@app.example.invalid/','https://app.example.invalid@evil.invalid/',
                'https://%61pp.example.invalid/','https://app.example.invalid./',
                'https://app.example.invalid:/','https://app.example.invalid:0/',
                'https://app.example.invalid/#fragment','https://app.example.invalid/\\evil',
                'https://app.example.invalid/\n')
        for url in denied:
            with self.subTest(url=url),self.assertRaises(ScopeDenied):self.policy.permits(url)
        for method in ('POST','HEAD','get'):
            with self.subTest(method=method),self.assertRaises(ScopeDenied):
                self.policy.permits('https://app.example.invalid/',method)
        self.policy.permits('https://app.example.invalid:443/')

    def test_ambiguous_paths_cannot_bypass_exclusions(self):
        for path in ('/a/../excluded','/%252e%252e/excluded','/a/..;/excluded',
                     '//excluded','/%2fexcluded','/a%5cexcluded','/%23excluded',
                     '/%3fexcluded','/%00','/%0d%0a','/%ZZ','/%FF','/%25252525252532'):
            with self.subTest(path=path),self.assertRaises(ScopeDenied):
                self.policy.permits('https://app.example.invalid'+path)

    def test_exact_prefix_and_host_wide_scope_are_distinct(self):
        raw=raw_policy();raw['allow']=[{'host':'app.example.invalid','path_prefix':'/api'}];raw['deny']=[]
        p=ScopePolicy(raw)
        p.permits('https://app.example.invalid/api')
        p.permits('https://app.example.invalid/api/items?q=other')
        for path in ('/apix','/api2','/api/../other','/api%2fitems'):
            with self.subTest(path=path),self.assertRaises(ScopeDenied):p.permits('https://app.example.invalid'+path)
        raw['allow']=[{'host':'app.example.invalid','path':'/api/item'}];p=ScopePolicy(raw)
        p.permits('https://app.example.invalid/api/item')
        with self.assertRaises(ScopeDenied):p.permits('https://app.example.invalid/api/item/extra')
        with self.assertRaises(ScopeDenied):p.permits('https://app.example.invalid/api/item/')
        raw['allow']=[{'host':'app.example.invalid'}];p=ScopePolicy(raw)
        p.permits('https://app.example.invalid/api%2fitem')  # No path exclusions to guess.

    def test_canonical_ip_ipv6_and_idna(self):
        raw=raw_policy();raw['allow']=[{'host':'127.0.0.1','schemes':['http'],'ports':[8123]},
                                      {'host':'::1','schemes':['http'],'ports':[8123]},
                                      {'host':'bücher.example.invalid'}];raw['deny']=[]
        p=ScopePolicy(raw)
        p.permits('http://127.0.0.1:8123/')
        p.permits('http://[::1]:8123/')
        p.permits('https://xn--bcher-kva.example.invalid/')
        for host in ('127.1','2130706433','0177.0.0.1','0x7f000001','0x7f.0.0.1','１２７.０.０.１'):
            with self.subTest(host=host),self.assertRaises(ScopeDenied):p.permits('http://'+host+':8123/')

    def test_policy_schema_is_explicit_and_rejects_ambiguous_rules(self):
        for change in ({'version':True},{'allow':[]},{'source':''},{'min_interval':float('nan')},
                       {'min_interval':True},{'max_requests':0},{'max_bytes':True},{'extra':'unknown'},
                       {'allow':[{'host':'*example.invalid'}]},
                       {'allow':[{'host':'app.example.invalid','path':'/a','path_prefix':'/b'}]},
                       {'allow':[{'host':'app.example.invalid','path_prefix':'/a/../b'}]},
                       {'allow':[{'host':'app.example.invalid','ports':[True]}]}):
            raw=raw_policy();raw.update(change)
            with self.subTest(change=change),self.assertRaises(ScopeDenied):ScopePolicy(raw)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"version":1,"version":2}')
            with self.assertRaises(ScopeDenied):ScopePolicy.load(p)

    def test_budget_and_digest(self):
        urls=['https://app.example.invalid/a']
        self.policy.preflight(urls,0.1,1000)
        self.assertEqual(self.policy.sha256,ScopePolicy(copy.deepcopy(self.policy.raw)).sha256)
        for args in ((urls,0.01,1000),(urls,0.1,1001),(urls*4,0.1,1000),
                     ([],0.1,10),(urls,float('nan'),10),(urls,True,10),
                     (urls,0.1,False),('https://app.example.invalid/',0.1,10)):
            with self.subTest(args=args),self.assertRaises(ScopeDenied):self.policy.preflight(*args)

    def test_complete_batch_checked_before_transport_or_output(self):
        urls=['https://app.example.invalid/a.js','https://other.example.invalid/b.js']
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run'
            fetch=Mock()
            with self.assertRaises(ScopeDenied):collector.collect(urls,out,'javascript',0.1,1000,fetcher=fetch,policy=self.policy)
            fetch.assert_not_called();self.assertFalse(out.exists())
            with patch.object(probe.urllib.request,'build_opener') as build:
                with self.assertRaises(ScopeDenied):probe.probe(urls,out,0.1,1000,policy=self.policy)
                build.assert_not_called();self.assertFalse(out.exists())

    def test_policy_metadata_does_not_become_an_execution_claim(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run'
            collector.collect(['https://app.example.invalid/a.js'],out,'javascript',0.1,1000,
                              fetcher=lambda *a:(b'const audit=1;','application/javascript'),policy=self.policy)
            meta=json.loads((out/'run.json').read_text())
            self.assertEqual(meta['scope_policy_sha256'],self.policy.sha256)
            self.assertEqual(meta['scope_mode'],'enforced-policy')
            self.assertNotIn('secure',meta)

    def test_identification_headers_cannot_override_method_or_route(self):
        for header in ('X-HTTP-Method-Override','X-Method-Override','X-HTTP-Method',
                       'X-Original-URL','X-Rewrite-URL','Forwarded','X-Forwarded-Host'):
            with self.subTest(header=header), self.assertRaises(ValueError):
                collector.checked_headers({header:'DELETE'})
        self.assertEqual(collector.checked_headers({'X-Research':'AUDIT'}),{'x-research':'AUDIT'})

    def test_cli_fails_closed_without_policy_before_requests(self):
        for script,extra in (('collect_assets.py',['--kind','javascript']),('probe_urls.py',[])):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);(root/'urls').write_text('https://app.example.invalid/a.js\n')
                result=subprocess.run([sys.executable,str(SCRIPTS/script),'--urls',str(root/'urls'),
                    '--output',str(root/'run'),'--interval','1',*extra],capture_output=True,text=True)
                self.assertEqual(result.returncode,2,result.stdout+result.stderr)
                self.assertIn('--scope-policy',result.stderr)
                self.assertFalse((root/'run').exists())


if __name__=='__main__':unittest.main()
