"""Validate all three ZIPs, then namespace reports for a merged release."""
from pathlib import Path
import gzip,hashlib,json,os,sys,zipfile
d=Path(sys.argv[1]);variant=os.environ.get('ONYX_VARIANT','kernelsu')
m=json.loads((d/'build-manifest.json').read_text());assert m['root_variant']==variant
assert m['kpm_enabled']==(variant=='sukisu')
assert m['kpm_backend']['backend_patched']==(variant=='sukisu')
zips=list(d.glob('*AnyKernel3-EXPERIMENTAL*.zip'));assert len(zips)==3
for p in zips:
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  image=z.read('Image.gz');raw=gzip.decompress(image)
  assert raw[56:60]==b'ARM\x64' and b'forcing load (CRC bypass)' in raw
  assert b'(SUSFS manual hook)' in raw
  assert hashlib.sha256(image).hexdigest()==m['kernel_image_sha256']
  assert hashlib.sha256(image).hexdigest()==m['kpm_backend']['packaged_image_sha256']
  assert (b'KP1158\0\0' in raw)==(variant=='sukisu')
  slot='_a' if '-Slot-A.' in p.name else '_b' if '-Slot-B.' in p.name else ''
  assert ('onyx_slot_override='+slot+'\n').encode() in z.read('anykernel.sh')
  config=z.read('kernel.config').decode().splitlines()
  assert ('CONFIG_KPM=y' in config)==m['kpm_enabled']
 assert p.with_name(p.name+'.sha256').read_text().split()[0]==hashlib.sha256(p.read_bytes()).hexdigest()
archive=d/m['source_archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==m['source_archive_sha256']
for p in list(d.iterdir()):
 if p.is_file() and not p.name.startswith('Onyx-Wild-Performance-'):
  if p.name.startswith(variant+'-'):continue
  p.rename(p.with_name(variant+'-'+p.name))
print(variant+': verified 3 slot packages, source checksum and KPM exclusivity')
