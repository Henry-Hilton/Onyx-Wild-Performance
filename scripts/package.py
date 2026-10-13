#!/usr/bin/env python3
"""Package a real compiled ARM64 kernel with preserved-ROM AnyKernel3."""
from pathlib import Path
import sys,subprocess,shutil,json,gzip,hashlib,zipfile,datetime
root,workspace=map(Path,sys.argv[1:])
out=root/'out'
dist=workspace/'dist'
dist.mkdir(exist_ok=True)
image=out/'arch/arm64/boot/Image.gz'
with gzip.open(image,'rb') as handle:
    header=handle.read(64)
if len(header)!=64 or header[56:60]!=b'ARM\x64':
    raise SystemExit('Compiled image does not contain an ARM64 Linux Image header')
audit=json.loads((dist/'crdroid-module-audit.json').read_text())
layouts=json.loads((dist/'structure-layout-audit.json').read_text())
feature_report=json.loads((out/'feature-validation.json').read_text())
manifest={
 'name':'Onyx Wild Performance',
 'status':'experimental; not device boot-tested',
 'built_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'kernel_release':(out/'include/config/kernel.release').read_text().strip(),
 'target':'Redmi Turbo 4 Pro / Poco F7 (onyx), android15-6.6 GKI, 4 KiB pages',
 'compiler':subprocess.check_output([str(root/'toolchain/bin/clang'),'--version'],text=True).splitlines()[0],
 'compile_flags':'-O3 -mtune=cortex-x4; ThinLTO; stock 250 Hz; CFI and KASAN interfaces retained',
 'kernel_image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
 'components':{},
 'wildkernels_revision':subprocess.check_output(['git','-C',str(workspace/'wildkernels'),'rev-parse','HEAD'],text=True).strip(),
 'stable_update_revision':subprocess.check_output(['git','-C',str(root/'xiaomi'),'rev-parse','v6.6.143^{commit}'],text=True).strip(),
 'module_validation':{'count':audit['module_count'],'vermagic':audit['vermagic'],
                      'missing_export_count':len(audit['missing_kernel_exports']),
                      'crc_mismatch_count':len(audit['crc_mismatches'])},
 'configuration_differences':feature_report['missing'],
 'device_testing':{'HyperOS':'not tested','AOSP':'not tested'},
 'source_tree_modified':True,
 'module_crc_mismatch_policy':'warn and accept, matching gki-clo',
 'source_archive':'Onyx-Wild-Performance-source.tar.gz',
 'source_archive_sha256':hashlib.sha256((dist/'Onyx-Wild-Performance-source.tar.gz').read_bytes()).hexdigest(),
 'layout_validation':{'structure_count':len(layouts['structures']),'mismatches':layouts['mismatches']},
}
for name in ('kernel','crdroid','xiaomi','kernelsu','susfs','nomount','bbg','droidspaces','patches','anykernel'):
    manifest['components'][name]=subprocess.check_output(['git','-C',str(root/name),'rev-parse','HEAD'],text=True).strip()
(dist/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copy2(out/'.config',dist/'kernel.config')
shutil.copy2(out/'Module.symvers',dist/'Module.symvers')
shutil.copy2(image,dist/'Image.gz')
if audit['missing_kernel_exports'] or audit['crc_mismatches'] or layouts['mismatches']:
    raise SystemExit('Module ABI validation failed. Raw build saved; refusing a flashable ZIP until resolved.')
stage=root/'package-stage'
stage.mkdir(exist_ok=True)
for file in (root/'anykernel').iterdir():
    if file.name in ('.git','.github'):
        continue
    dest=stage/file.name
    if file.is_dir():
        shutil.copytree(file,dest,dirs_exist_ok=True)
    else:
        shutil.copy2(file,dest)
shutil.copy2(workspace/'anykernel/anykernel.sh',stage/'anykernel.sh')
shutil.copy2(workspace/'anykernel/onyx-boot.sh',stage/'onyx-boot.sh')
for name in ('Image','Image.gz','Image.lz4','dtb','dtbo.img'):
    path=stage/name
    if path.is_file():
        path.unlink()
shutil.copy2(image,stage/'Image.gz')
shutil.copy2(dist/'build-manifest.json',stage/'build-manifest.json')
shutil.copy2(dist/'kernel.config',stage/'kernel.config')
shutil.copy2(dist/'structure-layout-audit.json',stage/'structure-layout-audit.json')
(stage/'profiles').mkdir(exist_ok=True)
shutil.copy2(workspace/'profiles/max-performance.sh',stage/'profiles/max-performance.sh')
(stage/'NOTICE.txt').write_text('Experimental Onyx kernel. Device boot and performance testing are pending.\nSource and dependency revisions are recorded in build-manifest.json.\nCredits: Xiaomi/MiCode, crDroid, Linux, KernelSU, SUSFS, WildKernels, NoMount, Baseband Guard, DroidSpaces, osm0sis AnyKernel3.\n')
version=manifest['kernel_release'].split('-',1)[0]
zip_path=dist/f'Onyx-Wild-Performance-{version}-KernelSU-SUSFS-AnyKernel3-EXPERIMENTAL.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for path in sorted(stage.rglob('*')):
        if path.is_file() and '.git' not in path.parts:
            info=zipfile.ZipInfo(path.relative_to(stage).as_posix())
            info.create_system=3
            info.external_attr=((0o100755 if path.name.endswith('.sh') or 'tools' in path.parts or path.name=='update-binary' else 0o100644)<<16)
            archive.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(zip_path) as archive:
    assert archive.testzip() is None
    assert 'Image.gz' in archive.namelist()
    assert 'META-INF/com/google/android/update-binary' in archive.namelist()
digest=hashlib.sha256(zip_path.read_bytes()).hexdigest()
(dist/(zip_path.name+'.sha256')).write_text(f'{digest}  {zip_path.name}\n')
print(zip_path)
print('SHA256:',digest)
subprocess.run([sys.executable,str(workspace/'scripts/make_slot_variants.py'),str(zip_path)],check=True)
