"""Require shared configuration parity and six packages before publishing."""
from pathlib import Path
import gzip,hashlib,json,sys,zipfile
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
 assert m['kpm_backend']['backend_patched']==(variant=='sukisu')
 label='SukiSU-KPM' if variant=='sukisu' else 'KernelSU'
 packages=list(d.glob('*-'+label+'-SUSFS-AnyKernel3-EXPERIMENTAL*.zip'));assert len(packages)==3
 for p in packages:
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   embedded=json.loads(z.read('build-manifest.json'));embedded.pop('installer_slot_override',None)
   assert embedded==m,'ZIP/report metadata mismatch: '+p.name
   assert z.read('kernel.config')==(d/(variant+'-kernel.config')).read_bytes()
   image=z.read('Image.gz');raw=gzip.decompress(image)
   assert hashlib.sha256(image).hexdigest()==m['kernel_image_sha256']==m['kpm_backend']['packaged_image_sha256']
   assert (b'KP1158\0\0' in raw)==(variant=='sukisu')
 assert hashlib.sha256((d/m['source_archive']).read_bytes()).hexdigest()==m['source_archive_sha256']
assert len(list(d.glob('*AnyKernel3-EXPERIMENTAL*.zip')))==6
print('Both variants have identical shared configuration and six slot ZIPs')
