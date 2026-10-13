#!/usr/bin/env python3
from pathlib import Path
import gzip,hashlib,json,tarfile,zipfile
import sys
w=Path(sys.argv[1]);dist=w/'dist';m=json.loads((dist/'build-manifest.json').read_text())
zip_path=next(dist.glob('*AnyKernel3-EXPERIMENTAL.zip'))
assert m['module_validation']['missing_export_count']==0
assert m['module_validation']['crc_mismatch_count']==0
assert m['layout_validation']['structure_count']==15
assert not m['layout_validation']['mismatches']
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 image=z.read('Image.gz')
 assert hashlib.sha256(image).hexdigest()==m['kernel_image_sha256']
 assert image==(dist/'Image.gz').read_bytes()
 assert gzip.decompress(image)[56:60]==b'ARM\x64'
 assert json.loads(z.read('build-manifest.json'))==m
 installer=z.read('anykernel.sh').decode()
 assert 'device.name1=onyx' in installer and 'do.devicecheck=1' in installer
 assert 'do.modules=0' in installer and 'block=$ONYX_BOOT_BLOCK' in installer
 assert 'onyx-boot.sh' in z.namelist()
 assert not {'dtb','dtbo.img','vendor_boot.img'}&set(z.namelist())
 assert z.getinfo('META-INF/com/google/android/update-binary').external_attr>>16 & 0o111
 assert z.getinfo('tools/ak3-core.sh').external_attr>>16 & 0o111
source=dist/m['source_archive']
assert hashlib.sha256(source.read_bytes()).hexdigest()==m['source_archive_sha256']
with tarfile.open(source) as t:
 for path in ('kernel/Makefile','kernel/drivers/kernelsu/Kbuild','kernel/fs/nomount/Makefile','kernel/security/baseband-guard/Makefile',
              'kernel/fs/susfs.c','kernel/net/ipv4/tcp_bbr3.c','kernel/drivers/misc/ntsync.c','source-notices/kernelsu-LICENSE'):
  assert t.getmember(path).isfile(),path
 header=t.extractfile('kernel/include/net/genetlink.h').read().decode()
 assert header.count('cap_sys_admin:1;')==1
summary={'zip':zip_path.name,'zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),
         'module_files_checked':m['module_validation']['count'],'layout_structures_checked':15,
         'image_header':'ARM64 valid','zip_integrity':'passed','source_integrity':'passed',
         'hardware_boot_testing':'pending for HyperOS and AOSP'}
(dist/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
