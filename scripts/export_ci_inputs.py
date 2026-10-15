#!/usr/bin/env python3
"""Capture the tested tree as pinned upstream commits plus complete deltas."""
from pathlib import Path
import json,shutil,subprocess,sys
r=Path('/root/onyx-kernel-dev');w=Path(sys.argv[1])
for name in ('configs','patches','source-additions','abi','licenses'):(w/name).mkdir(exist_ok=True)
sources={}
for name in ('kernel','kernelsu','nomount','bbg','anykernel'):
 def git(*args):return subprocess.check_output(['git','-C',str(r/name),*args])
 sources[name]={'url':git('remote','get-url','origin').decode().strip(),'commit':git('rev-parse','HEAD').decode().strip()}
 if name=='kernel':sources[name]['url']='https://github.com/crdroidandroid/android_kernel_xiaomi_sm8735.git'
 if name!='anykernel':(w/'patches'/f'{name}.patch').write_bytes(git('diff','--binary'))
 if name=='kernel':
  for path in git('ls-files','--others','--exclude-standard','-z').decode().split('\0'):
   if not path:continue
   src=r/name/path
   if src.is_symlink():continue
   if src.is_file():
    dest=w/'source-additions'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
for name in ('kernelsu','susfs','nomount','bbg'):
 shutil.copy2(r/name/'LICENSE',w/'licenses'/f'{name}-LICENSE')
shutil.copy2(r/'out/.config',w/'configs/kernel.config')
shutil.copy2(r/'out/requested-features.json',w/'configs/requested-features.json')
manifest=json.loads((w/'dist/build-manifest.json').read_text())
(w/'sources.lock.json').write_text(json.dumps({'sources':sources,'provenance':manifest['components'],
 'wildkernels_revision':manifest['wildkernels_revision'],'stable_update_revision':manifest['stable_update_revision'],
 'kernel_su_git_version':int(subprocess.check_output(['git','-C',str(r/'kernelsu'),'rev-list','--count','HEAD'],text=True)),
 'abi_baseline':'crDroidAndroid-17.0-20261003-onyx-v13.0-BETA (6.6.142)'},indent=2)+'\n')
