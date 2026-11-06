import contextlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'.opencode/skills/core-identity/scripts'
sys.path.insert(0,str(SCRIPTS))
try:
    import discovery_lab as lab
finally:
    sys.path.pop(0)

class Fixture:
    def __init__(self, scenario, vulnerable, seed): self.vulnerable=vulnerable; self.value=0
    def describe(self):
        return {'name':'Training tool','accounts':[{'label':'A','token':'lab-A'},{'label':'B','token':'lab-B'}]}
    def handle(self, method, path, body, headers):
        flags={'control':False,'boundary':False,'violation':False}
        if headers.get('authorization')!='Bearer lab-A': return 401,{'error':'auth'},flags
        if method=='GET' and path=='/api/own':
            flags['control']=True
            return 200,{'owned':'synthetic'},flags
        if method=='GET' and path=='/api/check':
            flags['boundary']=True; flags['violation']=self.vulnerable
            return (200,{'canary':'private'})+(flags,) if self.vulnerable else (403,{'error':'denied'},flags)
        return 404,{'error':'missing'},flags


def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.DEVNULL).decode().strip()

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.repo=self.root/'repo';self.repo.mkdir()
        git(self.repo,'init')
        contract=self.repo/'.opencode/rules/HUNT_RULES.md';contract.parent.mkdir(parents=True);contract.write_text('Old synthetic instructions\n')
        skill=self.repo/'.opencode/skills/sample/SKILL.md';skill.parent.mkdir(parents=True)
        skill.write_text('---\nname: sample\ndescription: Sample skill\n---\nRead related evidence.\n')
        key=self.repo/'.opencode/skills/sample/references/evaluation/rubric.md';key.parent.mkdir(parents=True);key.write_text('must stay hidden')
        git(self.repo,'add','.');git(self.repo,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','baseline')
        self.baseline=git(self.repo,'rev-parse','HEAD');contract.write_text('Revised synthetic instructions\n')
        git(self.repo,'add','.');git(self.repo,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','candidate')
        self.candidate=git(self.repo,'rev-parse','HEAD')
        self.output=self.root/'pilot'
        with patch.object(lab,'SCENARIOS',('one','two')):
            self.plan=lab.prepare(self.repo,self.output,self.baseline,self.candidate,max_actions=3,max_seconds=60,seed=123)
        self.app_patch=patch.object(lab,'build_app',lambda *args:Fixture(*args));self.app_patch.start();self.addCleanup(self.app_patch.stop)

    def state(self, positive=False):
        spec=next(x for x in self.plan['runs'] if x['vulnerable']==positive)
        return lab.RunState(self.output,self.plan,spec)

    def call(self,state,path,method='GET',body=None):
        return state.deliver(method,path,body or {},{'authorization':'Bearer lab-A'})

    def test_prepare_blinds_plan_and_preserves_snapshots(self):
        self.assertEqual(len(self.plan['runs']),8)
        self.assertNotEqual(self.plan['snapshots']['baseline']['commit'],self.plan['snapshots']['candidate']['commit'])
        for frozen in self.plan['snapshots'].values(): self.assertFalse(any('/references/evaluation/' in p for p in frozen['files']))
        for spec in self.plan['runs']:
            workspace=self.output/'public/workspaces'/spec['id']/'targets/lab'
            self.assertTrue((workspace/'rules.txt').is_file())
            self.assertNotIn('vulnerable',(workspace/'rules.txt').read_text())
        with self.assertRaises(FileExistsError): lab.prepare(self.repo,self.output,self.baseline,self.candidate)

    def test_recorded_context_skill_and_app_do_not_expose_oracle(self):
        state=self.state()
        status,response=self.call(state,'/context')
        self.assertEqual(status,200);self.assertIn('operating_contract',response['data'])
        _,loaded=self.call(state,'/skills/sample');self.assertIn('content',loaded['data'])
        _,response=self.call(state,'/api/check')
        self.assertNotIn('oracle',json.dumps(response))
        events=[json.loads(x) for x in state.events_path.read_text().splitlines()]
        self.assertEqual([x['kind'] for x in events],['context','skill-load','application'])
        self.assertTrue(events[-1]['oracle']['boundary'])
        self.assertEqual(events[-1]['previous_hash'],events[-2]['hash'])
        _,hidden=self.call(state,'/files/.opencode/skills/sample/references/evaluation/rubric.md')
        self.assertEqual(hidden['data']['error'],'instruction not available')

    def test_budget_requires_report_not_more_actions(self):
        state=self.state();self.plan['max_actions']=1
        self.call(state,'/api/own')
        status,_=self.call(state,'/api/check');self.assertEqual(status,429)
        status,_=self.call(state,'/report','POST',{'verdict':'blocked','summary':'budget','evidence_ids':[]})
        self.assertEqual(status,200)
        self.assertEqual(self.call(state,'/api/own')[0],409)

    def test_grade_uses_controls_boundaries_and_actual_violations(self):
        for spec in self.plan['runs']:
            state=lab.RunState(self.output,self.plan,spec)
            self.call(state,'/context')
            _,control=self.call(state,'/api/own');_,test=self.call(state,'/api/check')
            self.call(state,'/report','POST',{'verdict':'finding' if spec['vulnerable'] else 'no-finding',
                'summary':'observed synthetic behavior','evidence_ids':[control['evidence_id'],test['evidence_id']]})
        result=lab.grade(self.output)
        for arm in ('baseline','candidate'):
            self.assertEqual(result['counts'][arm]['verified-finding'],2)
            self.assertEqual(result['counts'][arm]['supported-negative'],2)
        self.assertTrue(all(x['context_delivered'] for x in result['runs']))

    def test_rejects_prose_only_findings_and_untested_negatives(self):
        for spec in self.plan['runs']:
            state=lab.RunState(self.output,self.plan,spec)
            verdict='finding' if spec['vulnerable'] else 'no-finding'
            self.call(state,'/report','POST',{'verdict':verdict,'summary':'unbacked assertion','evidence_ids':[]})
        result=lab.grade(self.output)
        self.assertEqual(result['counts']['candidate']['unsupported-finding'],2)
        self.assertEqual(result['counts']['candidate']['untested-negative'],2)

    def test_finding_needs_control_and_known_evidence_ids(self):
        state=self.state(True);_,test=self.call(state,'/api/check')
        self.call(state,'/report','POST',{'verdict':'finding','summary':'missing control','evidence_ids':[test['evidence_id']]})
        result=next(x for x in lab.grade(self.output)['runs'] if x['run_id']==state.spec['id'])
        self.assertEqual(result['result'],'unsupported-finding')
        another=next(s for s in self.plan['runs'] if s['id']!=state.spec['id'])
        state=lab.RunState(self.output,self.plan,another)
        self.call(state,'/report','POST',{'verdict':'finding','summary':'fake refs','evidence_ids':['E9999']})
        result=next(x for x in lab.grade(self.output)['runs'] if x['run_id']==state.spec['id'])
        self.assertEqual(result['result'],'unsupported-finding')
        self.assertFalse(result['citations_valid'])

    def test_grader_replay_rejects_consistently_rehashed_fabricated_effect(self):
        state=self.state(False);_,control=self.call(state,'/api/own');_,test=self.call(state,'/api/check')
        self.call(state,'/report','POST',{'verdict':'finding','summary':'fabricated','evidence_ids':[control['evidence_id'],test['evidence_id']]})
        rows=[json.loads(x) for x in state.events_path.read_text().splitlines()]
        rows[1]['oracle']['violation']=True
        previous='0'*64
        for row in rows:
            row.pop('hash');row['previous_hash']=previous
            row['hash']=lab.digest(json.dumps(row,sort_keys=True,separators=(',',':')).encode());previous=row['hash']
        state.events_path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        result=next(x for x in lab.grade(self.output)['runs'] if x['run_id']==state.spec['id'])
        self.assertEqual(result['result'],'invalid-harness-or-evidence')

    def test_http_loopback_protocol_and_restart_refusal(self):
        server=lab.make_server(self.output);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            self.assertEqual(server.server_address[0],'127.0.0.1')
            index=json.loads((self.output/'public/index.json').read_text())
            url=index[0]['run_url']
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(url+'/context') as response: context=json.load(response)
            self.assertNotIn('vulnerable',context['data'])
            self.assertNotIn('arm',context['data'])
            report=json.dumps({'verdict':'blocked','summary':'unit test','evidence_ids':[]}).encode()
            with opener.open(urllib.request.Request(url+'/report',data=report,headers={'Content-Type':'application/json'})) as response:
                self.assertTrue(json.load(response)['data']['accepted'])
            with self.assertRaises(FileExistsError): lab.make_server(self.output)
        finally: server.shutdown();server.server_close();thread.join()

if __name__=='__main__': unittest.main()
