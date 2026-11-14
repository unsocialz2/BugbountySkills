"""Validate canonical routing plus actual harmless examples extracted from guides.

Syntax and local-fixture behavior do not establish target exploitability. No test
transmits a payload to an external server, executes an unknown serialized blob,
changes a package registry or tests a real browser unless optional suite can run.
"""
import ast
import base64
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'.opencode/skills/web-mode'
GUIDES=WEB/'SKILL_FILES/VULNERABILITIES/WEB'
SPEC=importlib.util.spec_from_file_location('web_knowledge',WEB/'scripts/validate_knowledge.py')
knowledge=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(knowledge)


def blocks(name,language):
    text=(GUIDES/(name+'.md')).read_text()
    return re.findall(r'^```'+re.escape(language)+r'\n(.*?)^```\s*$',text,re.M|re.S)


def execute_python(name):
    code=blocks(name,'python')
    if len(code)!=1:raise AssertionError(f'{name}: expected one self-contained fixture')
    env={'__name__':'__main__'}
    with contextlib.redirect_stdout(io.StringIO()) as output:
        exec(compile(code[0],name+'.md','exec'),env)
    return env,output.getvalue()


class KnowledgeTests(unittest.TestCase):
    def test_canonical_catalogue_and_links(self):
        report=knowledge.validate()
        self.assertTrue(report['ok'],'\n'.join(report['errors']))

    def test_json_and_python_examples_parse_as_printed(self):
        for path in GUIDES.glob('*.md'):
            for language,code in re.findall(r'^```([^\n]*)\n(.*?)^```\s*$',path.read_text(),re.M|re.S):
                with self.subTest(guide=path.name,language=language):
                    if language=='json':json.loads(code)
                    if language=='python':ast.parse(code)

    @unittest.skipUnless(shutil.which('node'),'Node required for JavaScript grammar checks')
    def test_javascript_examples_parse_and_do_not_need_decoder_magic(self):
        snippets=[]
        for path in GUIDES.glob('*.md'):
            snippets.extend({'file':path.name,'code':code} for code in blocks(path.stem,'javascript'))
        runner='''const fs=require('node:fs'),vm=require('node:vm');
const examples=JSON.parse(fs.readFileSync(0,'utf8'));let failures=[];
for(const x of examples){try{new vm.Script(x.code,{filename:x.file})}catch(e){failures.push({file:x.file,error:String(e)})}}
console.log(JSON.stringify({checked:examples.length,failures}));if(failures.length)process.exitCode=1;'''
        result=subprocess.run(['node','-e',runner],input=json.dumps(snippets),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        result=json.loads(result.stdout);self.assertGreater(result['checked'],0)
        # These old alleged bypasses must not become valid JS just by passing a WAF.
        negative=r'''const vm=require('node:vm'),assert=require('node:assert/strict');
for(const code of [String.raw`alert\u00281)`,'%61lert(1)'])assert.throws(()=>new vm.Script(code),SyntaxError);'''
        result=subprocess.run(['node','-e',negative],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_http_framing_constructor_has_actual_crlf_and_correct_octet_count(self):
        env,_=execute_python('http_request_smuggling')
        request=env['request'];header,body=request.split(b'\r\n\r\n',1)
        self.assertEqual(body,env['body'])
        self.assertEqual(int(re.search(br'Content-Length: (\d+)',header)[1]),len(body))
        self.assertTrue(body.startswith(b'0\r\n\r\nGET /audit-canary/'))
        self.assertEqual(body[5:],env['canary'])
        self.assertNotIn(b'\\r\\n',request)

    @unittest.skipUnless(shutil.which('node'),'Node required for WHATWG URL semantics')
    def test_documented_url_host_controls_execute(self):
        snippet=blocks('url_parser_differentials','javascript')[0]
        runner="const assert=require('node:assert/strict');console.assert=(v,...msg)=>assert.ok(v,JSON.stringify(msg));\n"+snippet
        result=subprocess.run(['node','-e',runner],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        env,output=execute_python('url_parser_differentials')
        self.assertEqual(output.strip(),'audit.example.invalid')
        self.assertEqual(env['parts'].hostname,'audit.example.invalid')

    def test_internal_query_construction_preserves_data_when_encoded(self):
        env,_=execute_python('server_side_parameter_pollution')
        from urllib.parse import urlsplit,parse_qs
        self.assertIn('auditMarker',parse_qs(urlsplit(env['unsafe']).query))
        self.assertEqual(parse_qs(urlsplit(env['safe']).query),{'name':[env['value']]})
        env,_=execute_python('http_parameter_pollution')
        self.assertEqual(env['values'],['AUDIT_A','AUDIT_B'])

    def test_inert_pickle_hook_is_load_semantics_not_system_execution(self):
        env,_=execute_python('deserialization_all_langs')
        self.assertIsInstance(env['blob'],bytes)
        self.assertNotIn(b'posix',env['blob'])
        self.assertNotIn(b'system',env['blob'])

    def test_documented_office_repack_preserves_archive_root(self):
        before=os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            try:
                os.chdir(d)
                root=Path('owned_document_parts');(root/'word').mkdir(parents=True)
                (root/'[Content_Types].xml').write_text('<Types/>')
                (root/'word/document.xml').write_text('<document>AUDIT_MARKER</document>')
                execute_python('xxe_all_types')
                with zipfile.ZipFile('owned_audit.docx') as archive:
                    self.assertEqual(set(archive.namelist()),{'[Content_Types].xml','word/document.xml'})
                    self.assertIn(b'AUDIT_MARKER',archive.read('word/document.xml'))
            finally:os.chdir(before)

    def test_webhook_signature_covers_exact_payload_bytes(self):
        env,_=execute_python('async_jobs_webhooks')
        self.assertTrue(env['valid'](env['body'],env['signature']))
        self.assertFalse(env['valid'](env['body']+b' ',env['signature']))
        self.assertFalse(env['valid'](env['body'], '0'*64))

    def test_webauthn_client_data_fixture_is_decode_only(self):
        env,_=execute_python('webauthn_passkeys')
        parsed=json.loads(env['decoded'])
        self.assertEqual(parsed['type'],'webauthn.get')
        self.assertEqual(parsed['origin'],'https://rp.example.invalid')
        self.assertEqual(parsed['challenge'],'AUDIT_CHALLENGE')
        # This confirms serialization only; no authenticator signature is implied.
        self.assertNotIn('signature',parsed)

    def test_jwt_fixture_generates_structured_synthetic_hmac_token(self):
        env,out=execute_python('jwt_attacks')
        parts=out.strip().split('.')
        self.assertEqual(len(parts),3)
        decode=lambda x:json.loads(base64.urlsafe_b64decode(x+'='*(-len(x)%4)))
        self.assertEqual(decode(parts[0]),{'alg':'HS256','typ':'JWT'})
        self.assertEqual(decode(parts[1])['aud'],'audit-service')
        self.assertEqual(out.strip().encode(),env['message']+b'.'+env['signature'])

    def test_jwt_fixture_with_independent_library_and_wrong_audience_control(self):
        try:import jwt
        except ImportError:self.skipTest('PyJWT optional independent verifier unavailable')
        env,out=execute_python('jwt_attacks');token=out.strip()
        claims=jwt.decode(token,env['key'],algorithms=['HS256'],audience='audit-service',issuer='https://issuer.example.invalid')
        self.assertEqual(claims['sub'],'owned-A')
        with self.assertRaises(jwt.InvalidAudienceError):
            jwt.decode(token,env['key'],algorithms=['HS256'],audience='different-service')
        with self.assertRaises(jwt.InvalidSignatureError):
            jwt.decode(token,b'wrong_synthetic_key_32_bytes_only!',algorithms=['HS256'],audience='audit-service')


if __name__=='__main__':unittest.main()
