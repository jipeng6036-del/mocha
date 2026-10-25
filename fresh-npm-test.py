import os,subprocess,pathlib,json,time,hashlib
r=pathlib.Path('/tmp/mocha1893');base=dict(os.environ,CI='1',HOME=str(r/'home'),npm_config_cache=str(r/'npm-cache'),PLAYWRIGHT_BROWSERS_PATH=str(r/'browsers'),NODE_OPTIONS='--trace-warnings');rows=[]
for name,tree,path,cmd in [('baseline-docs-knip-repeat','baseline','/tmp/node1893/node_modules/.bin',['npm','run','lint:knip-docs']),('candidate-fresh-docs-ci-before-npmtest','candidate/docs',str(r/'nodes/22/node_modules/.bin'),['npm','ci','--ignore-scripts']),('candidate-fresh-npm-test','candidate',str(r/'nodes/22/node_modules/.bin'),['npm','test'])]:
 env=dict(base,PATH=path+':'+os.environ['PATH']);start=time.monotonic();actual=subprocess.run(['node','--version'],env=env,text=True,capture_output=True,check=True).stdout.strip()
 with open('/evidence/'+name+'.log','w') as f:
  f.write('cwd='+str(r/tree)+'\nnode='+actual+'\ncommand='+json.dumps(cmd)+'\n');f.flush();p=subprocess.run(cmd,cwd=r/tree,env=env,stdout=f,stderr=subprocess.STDOUT)
 row=dict(name=name,tree=tree,node=actual,command=cmd,code=p.returncode,seconds=round(time.monotonic()-start,2));rows.append(row);pathlib.Path('/evidence/fresh-npm-test-results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
 if name=='candidate-fresh-docs-ci-before-npmtest' and p.returncode:break
