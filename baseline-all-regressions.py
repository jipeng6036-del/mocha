import os,subprocess,pathlib,json,time,hashlib
r=pathlib.Path('/tmp/mocha1893');b=r/'baseline';c=r/'candidate';rel='test/browser/html-reporter.spec.js'
assert hashlib.sha256((b/'lib/reporters/html.js').read_bytes()).hexdigest()=='5da554bbb0983f761914aa8f8f7d8b82ce45d6a1e58bdb9c63ad5ebdc1d3785f'
(b/rel).write_bytes((c/rel).read_bytes())
env=dict(os.environ,CI='1',HOME=str(r/'home'),npm_config_cache=str(r/'npm-cache'),PLAYWRIGHT_BROWSERS_PATH=str(r/'browsers'),NODE_OPTIONS='--trace-warnings',PATH=str(r/'nodes/22/node_modules/.bin')+':'+os.environ['PATH']);cmd=['node','node_modules/@playwright/test/cli.js','test',rel,'--retries=0'];start=time.monotonic()
with open('/evidence/baseline-browser-regression-all-red.log','w') as f:
 f.write('cwd='+str(b)+'\ncommand='+json.dumps(cmd)+'\n');f.flush();p=subprocess.run(cmd,cwd=b,env=env,stdout=f,stderr=subprocess.STDOUT)
row=dict(command=cmd,code=p.returncode,seconds=round(time.monotonic()-start,2),baselineHtmlSha256=hashlib.sha256((b/'lib/reporters/html.js').read_bytes()).hexdigest(),testSha256=hashlib.sha256((b/rel).read_bytes()).hexdigest(),bundleSha256=hashlib.sha256((b/'mocha.js').read_bytes()).hexdigest());pathlib.Path('/evidence/baseline-browser-regression-all-red-result.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
