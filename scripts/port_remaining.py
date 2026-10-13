#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json
root=Path('/root/onyx-kernel-dev')
kernel=root/'kernel'
def edit(name,old,new):
    path=kernel/name
    text=path.read_text()
    if new in text:
        return
    assert old in text, (name,old)
    path.write_text(text.replace(old,new,1))

# DroidSpaces uses currently unused ABI slots 6,7,8 for System V IPC.
edit('include/linux/sched.h',
     '\tstruct sysv_sem\t\t\tsysvsem;\n\tstruct sysv_shm\t\t\tsysvshm;',
     '\t/* System V IPC fields reside in the ABI reserve below. */')
edit('include/linux/sched.h',
     '\tANDROID_KABI_RESERVE(6);\n\tANDROID_KABI_RESERVE(7);\n\tANDROID_KABI_RESERVE(8);',
     '#ifdef CONFIG_SYSVIPC\n\tANDROID_KABI_USE(6, struct sysv_sem sysvsem);\n\t_ANDROID_KABI_REPLACE(ANDROID_KABI_RESERVE(7); ANDROID_KABI_RESERVE(8), struct sysv_shm sysvshm);\n#else\n\tANDROID_KABI_RESERVE(6);\n\tANDROID_KABI_RESERVE(7);\n\tANDROID_KABI_RESERVE(8);\n#endif')
edit('arch/arm64/lib/clear_page.S','SYM_FUNC_START(__pi_clear_page)','\t.p2align 4\nSYM_FUNC_START(__pi_clear_page)')
edit('kernel/sched/features.h','SCHED_FEAT(CACHE_HOT_BUDDY, true)','SCHED_FEAT(CACHE_HOT_BUDDY, false)')
edit('include/net/sock.h','#define _SK_MEM_PACKETS\t\t256','#define _SK_MEM_PACKETS\t\t1024')
edit('fs/f2fs/f2fs.h','#define\tDEFAULT_IO_TIMEOUT\t(msecs_to_jiffies(20))','#define\tDEFAULT_IO_TIMEOUT\t(msecs_to_jiffies(6))')
for patch in ('susfs/kernel_patches/50_add_susfs_in_gki-android15-6.6.patch',
              'patches/common/bbrv3/0001-net-tcp-backport-BBRv3-to-android15-6.6.patch'):
    result=subprocess.run(['git','apply','--reject',str(root/patch)],cwd=kernel,capture_output=True,text=True)
    print(patch, result.returncode, result.stderr[-4000:])
print('Rejected hunks:')
for path in kernel.rglob('*.rej'):
    print(path.relative_to(kernel))
    print(path.read_text())
