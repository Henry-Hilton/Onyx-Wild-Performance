#!/usr/bin/env python3
"""Verify that the portable recipe recreates every tested modified source file."""
from pathlib import Path
import hashlib,subprocess,sys
old,new=map(Path,sys.argv[1:]);count=0
for component in ('kernel','kernelsu','nomount','bbg'):
 paths=subprocess.check_output(['git','-C',str(old/component),'diff','--name-only','-z']).decode().split('\0')
 paths+=subprocess.check_output(['git','-C',str(old/component),'ls-files','--others','--exclude-standard','-z']).decode().split('\0')
 for path in paths:
  if not path:continue
  a,b=old/component/path,new/component/path
  if a.is_symlink():assert b.exists();continue
  if a.is_file():
   assert b.is_file(),path
   assert hashlib.sha256(a.read_bytes()).digest()==hashlib.sha256(b.read_bytes()).digest(),path
   count+=1
print(f'Reconstructed {count} modified/added source files exactly')
