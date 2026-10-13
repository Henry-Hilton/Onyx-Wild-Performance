#!/usr/bin/env python3
"""Port reviewed upstream features onto the official onyx source."""
from pathlib import Path
import subprocess
import shutil
import json

ROOT = Path('/root/onyx-kernel-dev')
KERNEL = ROOT/'kernel'
REPORT = ROOT/'port-report.json'
results = []
def run(args, cwd=KERNEL, check=True, **kwargs):
    return subprocess.run(args, cwd=cwd, check=check, text=True, **kwargs)
def patch(path, cwd=KERNEL):
    path = Path(path)
    check=run(['git','apply','--check',str(path)],cwd=cwd,check=False,capture_output=True)
    if check.returncode == 0:
        run(['git','apply',str(path)],cwd=cwd)
        status='applied'
    else:
        reverse=run(['git','apply','--reverse','--check',str(path)],cwd=cwd,check=False,capture_output=True)
        status='already-present' if reverse.returncode == 0 else 'needs-port'
    results.append({'patch':str(path.relative_to(ROOT)), 'status':status, 'detail':check.stderr.strip() if status=='needs-port' else ''})
    REPORT.write_text(json.dumps(results,indent=2)+'\n')
    print(status, path.name, flush=True)
def append(path, text):
    p=KERNEL/path
    content=p.read_text()
    if text.strip() not in content:
        p.write_text(content+'\n'+text+'\n')

if not KERNEL.exists():
    run(['git','clone','--shared',str(ROOT/'crdroid'),str(KERNEL)],cwd=ROOT)
    run(['git','checkout','-b','codex/onyx-wild-performance'])
for path, missing in [('drivers/misc/Kconfig','drivers/misc/hwid/Kconfig'),('drivers/power/supply/Kconfig','drivers/power/supply/mca/Kconfig')]:
    p=KERNEL/path
    p.write_text('\n'.join(line for line in p.read_text().splitlines() if missing not in line)+'\n')

patch(ROOT/'susfs/kernel_patches/KernelSU/10_enable_susfs_for_ksu.patch',cwd=ROOT/'kernelsu')
dest=KERNEL/'drivers/kernelsu'
if not dest.exists():
    dest.symlink_to(ROOT/'kernelsu/kernel',target_is_directory=True)
append('drivers/Makefile','obj-$(CONFIG_KSU) += kernelsu/')
append('drivers/Kconfig','source "drivers/kernelsu/Kconfig"')
for subdir in ('fs','include/linux'):
    for file in (ROOT/'susfs/kernel_patches'/subdir).iterdir():
        if file.is_file():
            shutil.copy2(file,KERNEL/subdir/file.name)
patch(ROOT/'susfs/kernel_patches/50_add_susfs_in_gki-android15-6.6.patch')

# Integrate source at recorded commits without executing network setup scripts.
for target, source, makefile, kconfig, symbol in [
    ('fs/nomount','nomount/kernel/src','fs/Makefile','fs/Kconfig','NOMOUNT'),
    ('security/baseband-guard','bbg','security/Makefile','security/Kconfig','BBG')]:
    dest=KERNEL/target
    if not dest.exists():
        dest.symlink_to(ROOT/source,target_is_directory=True)
    append(makefile,f'obj-$(CONFIG_{symbol}) += {dest.name}/')
    append(kconfig,f'source "{target}/Kconfig"')

patch(ROOT/'droidspaces/Documentation/resources/kernel-patches/GKI/below-kernel-6.12/001.GKI-below-6.12-fix_sysvipc_kabi_6_7_8.patch')
patch(ROOT/'patches/common/ntsync/ntsync_compat_android15-6.6.patch')
patch(ROOT/'patches/common/ntsync/ntsync_base.patch')
patch(ROOT/'patches/common/bbrv3/0001-net-tcp-backport-BBRv3-to-android15-6.6.patch')
patch(ROOT/'patches/common/unicode_bypass_fix_6.1+.patch')
for name in (
    'optimized_mem_operations','file_struct_8bytes_align','reduce_cache_pressure',
    'mem_opt_prefetch','optimise_memcmp','minimise_wakeup_time','int_sqrt',
    'reduce_gc_thread_sleep_time','add_timeout_wakelocks_globally',
    'f2fs_reduce_congestion','reduce_freeze_timeout','clear_page_16bytes_align',
    'avoid_extra_s2idle_wake_attempts','disable_cache_hot_buddy',
    'f2fs_enlarge_min_fsync_blocks','increase_ext4_default_commit_age',
    'increase_sk_mem_packets','reduce_pci_pme_wakeups',
    'silence_irq_cpu_logspam','silence_system_logspam'):
    patch(ROOT/f'patches/common/{name}.patch')
