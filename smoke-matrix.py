import os,subprocess,pathlib,json,time
r=pathlib.Path('/tmp/mocha1893');c=r/'candidate'
env=dict(os.environ,CI='1',HOME=str(r/'home'),npm_config_cache=str(r/'npm-cache'),NODE_OPTIONS='--trace-warnings')
results=[]
for version in ['20.19.0','20','22.12.0','22','24','26']:
 prefix=r/'nodes'/version
 if version!='26':
  install=['npm','install','--prefix',str(prefix),'node@'+version,'--no-audit','--no-fund']
  with open('/evidence/smoke-node-'+version+'-install.log','w') as f:
   p=subprocess.run(install,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT)
  assert p.returncode==0,'runtime install '+version
 active=dict(env,PATH=(str(prefix/'node_modules/.bin')+':' if version!='26' else '')+os.environ['PATH'])
 actual=subprocess.run(['node','--version'],env=active,text=True,capture_output=True,check=True).stdout.strip()
 cmd=['npm','run','test-smoke'];start=time.monotonic()
 with open('/evidence/candidate-smoke-'+version+'.log','w') as f:
  f.write('node='+actual+'\ncommand='+json.dumps(cmd)+'\n');f.flush();p=subprocess.run(cmd,cwd=c,env=active,stdout=f,stderr=subprocess.STDOUT)
 row=dict(requestedNode=version,node=actual,command=cmd,code=p.returncode,seconds=round(time.monotonic()-start,2));results.append(row);pathlib.Path('/evidence/candidate-smoke-matrix-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(row),flush=True)
