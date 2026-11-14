#!/usr/bin/env python3
"""Optional isolated browser regressions; never connects to a real target.

Exit 0: all checks executed and passed. Exit 1: executed check failed.
Exit 2: browser/runtime unavailable (blocked, not a passing security check).
"""
import argparse
import json
from pathlib import Path
import shutil
import sys


def run(executable=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {'status':'blocked','reason':'Playwright is not installed','checks':[]},2
    checks=[]
    with sync_playwright() as p:
        chosen=executable
        if chosen is None and not Path(p.chromium.executable_path).exists():
            chosen=shutil.which('chromium') or shutil.which('google-chrome')
        try:
            browser=p.chromium.launch(executable_path=chosen,headless=True,args=['--no-sandbox'])
        except Exception as exc:
            # Runtime unavailable is not browser-policy validation. No full launch
            # command, environment or unrelated process output needs publishing.
            reason='Chromium launch failed: '+type(exc).__name__
            if 'socket() failed' in str(exc) or 'Operation not permitted' in str(exc):
                reason+=' (environment disallows required process socket)'
            elif 'Executable doesn' in str(exc):reason+=' (browser executable unavailable)'
            return {'status':'blocked','reason':reason,'checks':[]},2
        try:
            for name,policy,script,expected in [
                ('eval-does-not-authorize-inline',"script-src 'self' 'unsafe-eval'",'<script>window.__AUDIT_MARKER__=1</script>',False),
                ('nonce-disables-unsafe-inline',"script-src 'nonce-audit123' 'unsafe-inline'",'<script>window.__AUDIT_MARKER__=1</script>',False),
                ('matching-nonce-positive-control',"script-src 'nonce-audit123'",'<script nonce="audit123">window.__AUDIT_MARKER__=1</script>',True),
                ('inline-only-positive-control',"script-src 'unsafe-inline'",'<script>window.__AUDIT_MARKER__=1</script>',True)]:
                context=browser.new_context();context.route('**/*',lambda route:route.abort())
                context.route('http://audit.invalid/**',lambda route,pol=policy,body=script:route.fulfill(
                    status=200,content_type='text/html',headers={'Content-Security-Policy':pol},body=body))
                page=context.new_page();page.goto('http://audit.invalid/policy')
                observed=page.evaluate('window.__AUDIT_MARKER__ === 1')
                assert observed is expected,(name,observed,expected)
                checks.append({'name':name,'passed':True,'observed':observed})
                context.close()
            context=browser.new_context();context.route('**/*',lambda route:route.abort())
            context.route('http://audit.invalid/**',lambda route:route.fulfill(status=200,content_type='text/html',body='<body></body>'))
            page=context.new_page();page.goto('http://audit.invalid/frames')
            for name,sandbox,expected_origin,expected_access in [
                ('srcdoc-unsandboxed',None,'http://audit.invalid',True),
                ('srcdoc-opaque-origin','allow-scripts','null',False)]:
                observed=page.evaluate(r'''async sandbox => {
                    const f=document.createElement('iframe');
                    if(sandbox!==null)f.setAttribute('sandbox',sandbox);
                    const response=new Promise((resolve,reject)=>{
                        const timeout=setTimeout(()=>reject(new Error('frame proof timed out')),3000);
                        const listener=e=>{if(e.source===f.contentWindow){clearTimeout(timeout);window.removeEventListener('message',listener);resolve({origin:e.origin,access:e.data.access});}};
                        window.addEventListener('message',listener);
                    });
                    f.srcdoc='<script>let access;try{void parent.document.body;access=true}catch(e){access=false}parent.postMessage({access},"*")</script>';
                    document.body.append(f);return await response;
                }''',sandbox)
                assert observed=={'origin':expected_origin,'access':expected_access},(name,observed)
                checks.append({'name':name,'passed':True,'observed':observed})
            context.close()
            return {'status':'passed','browser_version':browser.version,'checks':checks,
                    'limits':'Synthetic CSP and iframe regressions only; no live-target, gadget, victim-delivery or all-browser certification.'},0
        except Exception as exc:
            return {'status':'failed','browser_version':browser.version,'checks':checks,
                    'reason':type(exc).__name__+': '+str(exc)},1
        finally:browser.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable',help='Explicit permitted Chromium executable')
    parser.add_argument('--output',type=Path,help='Optional new JSON evidence file')
    args=parser.parse_args();result,status=run(args.executable)
    if args.output:
        with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2));raise SystemExit(status)


if __name__=='__main__':main()
