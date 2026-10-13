#!/usr/bin/env python3
"""Release packaging shared by CI and a locally reproduced build."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile,zipfile
r,w=map(Path,sys.argv[1:]);out=r/'out';dist=w/'dist'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
image=out/'arch/arm64/boot/Image.gz'
with gzip.open(image,'rb') as f:assert f.read(64)[56:60]==b'ARM\x64'
a=json.loads((dist/'crdroid-module-audit.json').read_text());b=json.loads((dist/'structure-layout-audit.json').read_text())
assert a['module_count']>0 and not a['missing_kernel_exports'] and not a['crc_mismatches']
assert len(b['structures'])==15 and not b['mismatches']
lock=json.loads((w/'sources.lock.json').read_text())
notices=r/'source-notices';notices.mkdir(exist_ok=True)
shutil.copytree(w/'licenses',notices/'licenses',dirs_exist_ok=True)
shutil.copy2(w/'README.md',notices/'README.md')
shutil.copy2(w/'scripts/build_exported_source.sh',notices/'build_exported_source.sh')
source=dist/'Onyx-Wild-Performance-source.tar.gz'
with tarfile.open(source,'w:gz',dereference=True) as archive:
 for tree in (r/'kernel',notices):
  for folder,dirs,files in os.walk(tree,followlinks=True):
   dirs[:]=sorted(d for d in dirs if d not in ('.git','.github'))
   for file in sorted(files):
    path=Path(folder)/file
    if path.exists() and file!='.git':archive.add(path,arcname=path.relative_to(r),recursive=False)
manifest={'name':'Onyx Wild Performance','status':'experimental; hardware boot testing pending',
 'module_crc_mismatch_policy':'warn and accept, matching gki-clo',
 'kernel_release':(out/'include/config/kernel.release').read_text().strip(),
 'built_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'compiler':subprocess.check_output(['clang-21','--version'],text=True).splitlines()[0],
 'target':'Redmi Turbo 4 Pro / Poco F7 (onyx), android15-6.6 GKI, 4 KiB pages',
 'compile_flags':'-O3 -mtune=cortex-x4; ThinLTO; stock 250 Hz; CFI and KASAN interfaces retained',
 'sources':lock,'repository_commit':os.environ.get('GITHUB_SHA','local'),
 'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
 'kernel_image_sha256':sha(image),'source_archive':source.name,'source_archive_sha256':sha(source),
 'module_validation':{'count':a['module_count'],'missing_export_count':0,'crc_mismatch_count':0},
 'layout_validation':{'structure_count':15,'mismatches':[]},
 'configuration_differences':json.loads((out/'feature-validation.json').read_text())['missing'],
 'device_testing':{'HyperOS':'not tested','AOSP':'not tested'}}
(dist/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copy2(out/'.config',dist/'kernel.config');shutil.copy2(out/'Module.symvers',dist/'Module.symvers')
stage=r/'package-stage';shutil.copytree(r/'anykernel',stage,ignore=shutil.ignore_patterns('.git','.github'),dirs_exist_ok=True)
for name in ('Image','Image.gz','Image.lz4','dtb','dtbo.img'):
 path=stage/name
 if path.is_file():path.unlink()
shutil.copy2(w/'anykernel/anykernel.sh',stage/'anykernel.sh');shutil.copy2(image,stage/'Image.gz')
shutil.copy2(w/'anykernel/onyx-boot.sh',stage/'onyx-boot.sh')
for name in ('build-manifest.json','kernel.config','structure-layout-audit.json'):shutil.copy2(dist/name,stage/name)
(stage/'profiles').mkdir(exist_ok=True);shutil.copy2(w/'profiles/max-performance.sh',stage/'profiles/max-performance.sh')
version=manifest['kernel_release'].split('-',1)[0]
package=dist/f'Onyx-Wild-Performance-{version}-KernelSU-SUSFS-AnyKernel3-EXPERIMENTAL.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for path in sorted(stage.rglob('*')):
  if path.is_file():
   info=zipfile.ZipInfo(path.relative_to(stage).as_posix());info.create_system=3
   info.external_attr=(0o100755 if path.name.endswith('.sh') or 'tools' in path.parts or path.name=='update-binary' else 0o100644)<<16
   archive.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(package) as archive:
 assert archive.testzip() is None
 assert sha(image)==hashlib.sha256(archive.read('Image.gz')).hexdigest()
 assert 'META-INF/com/google/android/update-binary' in archive.namelist()
summary={'module_files_checked':a['module_count'],'layout_structures_checked':15,'zip_integrity':'passed',
 'source_integrity':'passed','hardware_boot_testing':'pending for HyperOS and AOSP','zip_sha256':sha(package)}
(dist/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for path in (package,source):(dist/(path.name+'.sha256')).write_text(f'{sha(path)}  {path.name}\n')
print(package)
subprocess.run([sys.executable,str(w/'scripts/make_slot_variants.py'),str(package)],check=True)
