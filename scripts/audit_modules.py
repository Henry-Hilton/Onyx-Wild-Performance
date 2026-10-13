#!/usr/bin/env python3
"""Compare supplied Android modules with the built kernel's symbol CRCs."""
import argparse
import json
from pathlib import Path
from collections import defaultdict
from elftools.elf.elffile import ELFFile

parser=argparse.ArgumentParser()
parser.add_argument('--modules', type=Path, default=Path('/root/onyx-recovery-inputs/rom-images'))
parser.add_argument('--symvers',type=Path)
parser.add_argument('--baseline',type=Path)
parser.add_argument('--write-baseline',type=Path)
parser.add_argument('--output',type=Path,default=Path('/root/onyx-kernel-dev/module-audit.json'))
args=parser.parse_args()
exports={}
requirements=[]
module_symbols=set()
for path in ([] if args.baseline else sorted(args.modules.rglob('*.ko'))):
    with path.open('rb') as handle:
        elf=ELFFile(handle)
        names=elf.get_section_by_name('__versions')
        imports={}
        if names:
            data=names.data()
            for offset in range(0,len(data),64):
                record=data[offset:offset+64]
                symbol=record[8:].split(b'\0',1)[0].decode()
                imports[symbol]=int.from_bytes(record[:8],'little')
        symtab=elf.get_section_by_name('.symtab')
        if symtab:
            for symbol in symtab.iter_symbols():
                if symbol.name.startswith('__ksymtab_'):
                    module_symbols.add(symbol.name.removeprefix('__ksymtab_'))
        modinfo=elf.get_section_by_name('.modinfo')
        info={}
        if modinfo:
            for entry in modinfo.data().split(b'\0'):
                if b'=' in entry:
                    key,value=entry.decode(errors='replace').split('=',1)
                    info[key]=value
        requirements.append({'path':str(path),'name':path.name,'vermagic':info.get('vermagic'),'imports':imports})
if args.baseline:
    baseline=json.loads(args.baseline.read_text())
    requirements=baseline['modules']
    module_symbols=set(baseline['module_symbols'])
if args.write_baseline:
    for module in requirements:
        module['path']=str(Path(module['path']).relative_to(args.modules))
    args.write_baseline.write_text(json.dumps({'module_symbols':sorted(module_symbols),'modules':requirements},separators=(',',':'))+'\n')
if not requirements:
    raise SystemExit('No module requirements supplied; refusing an empty ABI audit')
if args.symvers:
    for line in args.symvers.read_text().splitlines():
        cols=line.split()
        if len(cols)>=3:
            exports[cols[1]]=int(cols[0],16)
missing=defaultdict(list)
mismatch=defaultdict(list)
if exports:
    for module in requirements:
        for symbol,crc in module['imports'].items():
            if symbol not in exports:
                if symbol not in module_symbols:
                    missing[symbol].append(module['name'])
            elif exports[symbol]!=crc:
                mismatch[symbol].append({'module':module['name'],'expected':f'{crc:08x}','built':f'{exports[symbol]:08x}'})
result={'module_count':len(requirements),'vermagic':sorted(set(m['vermagic'] for m in requirements if m['vermagic'])),
        'missing_kernel_exports':dict(missing),'crc_mismatches':dict(mismatch),'modules':requirements}
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'module_count':result['module_count'],'vermagic':result['vermagic'],
                  'missing_kernel_exports':sorted(missing),'crc_mismatches':sorted(mismatch)},indent=2))
if exports and (missing or mismatch):
    raise SystemExit('Module ABI validation failed')
