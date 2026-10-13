#!/usr/bin/env python3
from pathlib import Path
import re,sys,subprocess,yaml,json
kernel,out=map(Path,sys.argv[1:])
workspace=Path(__file__).resolve().parents[1]
features={}
for action in ('susfs-config','networking-config','cifs','misc','droidspaces','btf'):
    text=(workspace/'wildkernels/.github/actions'/action/'action.yml').read_text()
    for key,value in re.findall(r'^\s+(CONFIG_\w+)=(y|n|m|"[^"\n]*"|\d+)\s*$',text,re.M):
        features[key]=value
features.update({
 'CONFIG_KSU':'y','CONFIG_NOMOUNT':'y','CONFIG_BBG':'y','CONFIG_NTSYNC':'y',
 'CONFIG_TCP_CONG_BBR3':'y','CONFIG_FUSE_BPF':'y','CONFIG_DEBUG_INFO_BTF':'y',
 'CONFIG_SYSVIPC':'y','CONFIG_POSIX_MQUEUE':'y','CONFIG_USER_NS':'y','CONFIG_PID_NS':'y','CONFIG_IPC_NS':'y',
 'CONFIG_DEVTMPFS':'y','CONFIG_DEVTMPFS_MOUNT':'y',
 'CONFIG_LOCALVERSION':'"-onyx-wild-performance"','CONFIG_LOCALVERSION_AUTO':'n',
 'CONFIG_LTO_NONE':'n','CONFIG_LTO_CLANG':'y','CONFIG_LTO_CLANG_THIN':'y','CONFIG_LTO_CLANG_FULL':'n',
 'CONFIG_MODULE_SIG_PROTECT':'n','CONFIG_MODULE_SIG_FORCE':'n',
 'CONFIG_RCU_LAZY_DEFAULT_OFF':'y',
 'CONFIG_UBSAN':'n','CONFIG_UBSAN_TRAP':'n','CONFIG_DEBUG_MEMORY_INIT':'n',
 'CONFIG_CMA_DEBUGFS':'y','CONFIG_PRINTK_CALLER':'n',
 'CONFIG_DEBUG_INFO_COMPRESSED_NONE':'y','CONFIG_DEBUG_INFO_COMPRESSED_ZSTD':'n',
 'CONFIG_DEBUG_INFO_COMPRESSED_ZLIB':'n',
})
# Keep stock 250 Hz, CFI, KASAN exports, KUnit and vendor-visible debug interfaces.
# Those are ABI dependencies; a higher timer rate alone does not prove better performance.
features['CONFIG_CMDLINE']='"console=ttynull stack_depot_disable=on cgroup_disable=pressure kasan.stacktrace=off kvm-arm.mode=protected bootconfig ioremap_guard kasan=off"'
features['CONFIG_LSM']='"landlock,lockdown,yama,loadpin,safesetid,selinux,smack,tomoyo,apparmor,bpf,baseband_guard"'
(out/'requested-features.json').write_text(json.dumps(features,indent=2)+'\n')
fragment=out/'onyx-features.config'
fragment.write_text('\n'.join(f'{k}={v}' if v!='n' else f'# {k} is not set' for k,v in features.items())+'\n')
for key,value in features.items():
    args=[str(kernel/'scripts/config'),'--file',str(out/'.config')]
    if value in ('y','n','m'):
        args += [{'y':'--enable','n':'--disable','m':'--module'}[value],key]
    elif value.startswith('"'):
        args += ['--set-str',key,value[1:-1]]
    else:
        args += ['--set-val',key,value]
    subprocess.run(args,check=True)
