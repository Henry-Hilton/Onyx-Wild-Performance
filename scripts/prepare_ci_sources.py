#!/usr/bin/env python3
"""Fetch exact source commits and apply the reviewed, build-tested delta."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
w=Path(__file__).resolve().parents[1];root=Path(sys.argv[1]).resolve();root.mkdir(parents=True,exist_ok=True)
lock=json.loads((w/'sources.lock.json').read_text())
def run(*args):subprocess.run(args,check=True)
for name,source in lock['sources'].items():
 dest=root/name
 if dest.exists():raise SystemExit(f'Refusing to overwrite source directory: {dest}')
 run('git','init','-q',str(dest))
 run('git','-C',str(dest),'remote','add','origin',source['url'])
 run('git','-C',str(dest),'fetch','--depth=1','origin',source['commit'])
 run('git','-C',str(dest),'checkout','--detach','FETCH_HEAD')
 patch=w/'patches'/f'{name}.patch'
 if patch.exists() and patch.stat().st_size:
  run('git','-C',str(dest),'apply','--check',str(patch))
  run('git','-C',str(dest),'apply',str(patch))
shutil.copytree(w/'source-additions',root/'kernel',dirs_exist_ok=True)
for path,target in [('drivers/kernelsu','../../kernelsu/kernel'),('fs/nomount','../../nomount/kernel/src'),('security/baseband-guard','../../bbg')]:
 (root/'kernel'/path).symlink_to(target,target_is_directory=True)
print('Pinned sources prepared:',root)
