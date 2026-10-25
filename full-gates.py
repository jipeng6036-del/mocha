import os,subprocess,pathlib,json,time,hashlib
r=pathlib.Path('/tmp/mocha1893');c=r/'candidate'
env=dict(os.environ,CI='1',HOME=str(r/'home'),npm_config_cache=str(r/'npm-cache'),PLAYWRIGHT_BROWSERS_PATH=str(r/'browsers'),NODE_OPTIONS='--trace-warnings',PATH='/tmp/node1893/node_modules/.bin:'+os.environ['PATH'])
results=[]
versions={name:subprocess.run([name,'--version'],env=env,text=True,capture_output=True).stdout.strip() for name in ['node','npm']}
for name,cmd in [('candidate-full-format',['npm','run','format:check']),('candidate-full-lint',['npm','run','lint']),('candidate-full-node',['npm','run','test-node']),('candidate-full-browser',['npm','run','test-browser']),('candidate-full-tsc',['npm','run','tsc']),('candidate-full-smoke',['npm','run','test-smoke'])]:
 start=time.monotonic()
 with open('/evidence/'+name+'.log','w') as f:
  f.write('cwd='+str(c)+'\nuid='+str(os.getuid())+'\nversions='+json.dumps(versions)+'\ncommand='+json.dumps(cmd)+'\n');f.flush();p=subprocess.run(cmd,cwd=c,env=env,stdout=f,stderr=subprocess.STDOUT)
 row=dict(name=name,command=cmd,code=p.returncode,seconds=round(time.monotonic()-start,2));results.append(row);pathlib.Path('/evidence/candidate-full-results.json').write_text(json.dumps(dict(versions=versions,uid=os.getuid(),results=results),indent=2));print(json.dumps(row),flush=True)
