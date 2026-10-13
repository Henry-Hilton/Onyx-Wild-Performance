#!/usr/bin/env python3
from pathlib import Path
import re,json
root=Path('/root/onyx-kernel-dev')
report=[]
(root/'remaining-conflicts.txt').write_text('')
pattern=re.compile(r'^<<<<<<< OEM\n(.*?)^=======\n(.*?)^>>>>>>> v6\.6\.143\n',re.M|re.S)
for item in json.loads((root/'stable-port-report.json').read_text()):
    if item['status']!='conflict':
        continue
    path=root/'kernel'/item['path']
    text=path.read_text()
    reference=root/'konoha'/item['path']
    ref=reference.read_text() if reference.is_file() else ''
    index=0
    def choose(match):
        global index
        index+=1
        ours,theirs=match.groups()
        in_ours=bool(ours.strip()) and ours in ref
        in_theirs=bool(theirs.strip()) and theirs in ref
        choice=None
        if in_ours and not in_theirs:
            choice=ours
        elif in_theirs and not in_ours:
            choice=theirs
        if choice is not None:
            report.append({'path':item['path'],'index':index,'resolution':'exact reference match','side':'OEM' if choice==ours else 'stable'})
            return choice
        return match.group(0)
    resolved=pattern.sub(choose,text)
    path.write_text(resolved)
    if '<<<<<<< OEM' in resolved:
        with (root/'remaining-conflicts.txt').open('a') as out:
            for i,m in enumerate(pattern.finditer(resolved),1):
                line=resolved[:m.start()].count('\n')+1
                out.write(f'=== {item["path"]}:{line} ===\n{m.group(0)}\n')
(root/'conflict-resolutions.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exact reference resolutions:',len(report))
print('Remaining conflict blocks:',(root/'remaining-conflicts.txt').read_text().count('=== ') if (root/'remaining-conflicts.txt').exists() else 0)
