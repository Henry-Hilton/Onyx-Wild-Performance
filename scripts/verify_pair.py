"""Require shared configuration parity and six packages before publishing."""
from pathlib import Path
import json,sys
d=Path(sys.argv[1])
def config(variant):
 result={}
 for line in (d/(variant+'-kernel.config')).read_text().splitlines():
  if line.startswith('CONFIG_'):
   key,value=line.split('=',1);result[key]=value
  elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
   result[line[2:-11]]='n'
 for key in ('CONFIG_KPM','CONFIG_KSU_MANUAL_SU'):result.pop(key,None)
 return result
a=config('kernelsu');b=config('sukisu')
diff={k:(a.get(k,'n'),b.get(k,'n')) for k in a.keys()|b.keys() if a.get(k,'n')!=b.get(k,'n')}
assert not diff, 'Shared configuration drift: '+str(diff)
for variant in ('kernelsu','sukisu'):
 m=json.loads((d/(variant+'-build-manifest.json')).read_text())
 assert m['root_variant']==variant and m['kpm_enabled']==(variant=='sukisu')
assert len(list(d.glob('*AnyKernel3-EXPERIMENTAL*.zip')))==6
print('Both variants have identical shared configuration and six slot ZIPs')
