#!/usr/bin/env python3
"""Three-way stable update retaining OEM changes, recording every conflict."""
from pathlib import Path
import subprocess
import tempfile
import json,sys

ROOT=Path('/root/onyx-kernel-dev')
kernel=ROOT/'kernel'
def git(*args, check=True):
    return subprocess.run(['git',*args],cwd=root_git,check=check,capture_output=True)
root_git=ROOT/'xiaomi'
old='v6.6.142' if '--current' in sys.argv else 'v6.6.56'
new='v6.6.143'
changes=git('diff','--name-status','--no-renames',old,new).stdout.decode().splitlines()
report=[]
for line in changes:
    status,name=line.split('\t',1)
    path=kernel/name
    if name.startswith('Documentation/devicetree/bindings/'):
        continue # OEM tree keeps these in a separately published checkout.
    if status=='D':
        if path.exists():
            base=git('show',f'{old}:{name}').stdout
            if path.read_bytes()==base:
                path.unlink()
            else:
                report.append({'path':name,'status':'modified-deletion'})
        continue
    incoming=git('show',f'{new}:{name}').stdout
    if status=='A':
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(incoming)
        elif path.read_bytes()!=incoming:
            report.append({'path':name,'status':'add-add'})
        continue
    if not path.exists():
        report.append({'path':name,'status':'OEM-removed'})
        continue
    base=git('show',f'{old}:{name}').stdout
    ours=path.read_bytes()
    if ours==base:
        path.write_bytes(incoming)
        continue
    with tempfile.TemporaryDirectory() as directory:
        files=[Path(directory)/n for n in ('ours','base','new')]
        for file,data in zip(files,(ours,base,incoming)):
            file.write_bytes(data)
        merged=subprocess.run(['git','merge-file','-p','-L','OEM','-L',old,'-L',new,*map(str,files)],capture_output=True)
        if merged.returncode<0 or merged.returncode>127:
            report.append({'path':name,'status':'binary-unmerged'})
        else:
            path.write_bytes(merged.stdout)
            if merged.returncode:
                report.append({'path':name,'status':'conflict','count':merged.returncode})
(ROOT/'stable-port-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
