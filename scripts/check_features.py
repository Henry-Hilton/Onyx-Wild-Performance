#!/usr/bin/env python3
from pathlib import Path
import sys,json
config=Path(sys.argv[1])
text=config.read_text()
required=json.loads((config.parent/'requested-features.json').read_text())
missing=[]
for key,value in required.items():
    expected=f'# {key} is not set' if value=='n' else f'{key}={value}'
    if expected not in text.splitlines():
        missing.append({'symbol':key,'requested':value})
(config.parent/'feature-validation.json').write_text(json.dumps({'missing':missing},indent=2)+'\n')
# Some upstream action symbols are absent in this series (e.g. NETFS_SUPPORT).
# Explicitly fail core feature gaps instead of silently producing a reduced kernel.
core={'CONFIG_KSU','CONFIG_KSU_SUSFS','CONFIG_NOMOUNT','CONFIG_BBG','CONFIG_NTSYNC',
      'CONFIG_TCP_CONG_BBR3','CONFIG_CIFS','CONFIG_DEBUG_INFO_BTF','CONFIG_FUSE_BPF',
      'CONFIG_SYSVIPC','CONFIG_IPC_NS','CONFIG_PID_NS','CONFIG_USER_NS','CONFIG_POSIX_MQUEUE',
      'CONFIG_TMPFS_XATTR','CONFIG_TMPFS_POSIX_ACL','CONFIG_WIREGUARD',
      'CONFIG_KSU_SUSFS_SUS_PATH','CONFIG_KSU_SUSFS_SUS_MOUNT','CONFIG_KSU_SUSFS_SUS_KSTAT',
      'CONFIG_KSU_SUSFS_SPOOF_UNAME','CONFIG_KSU_SUSFS_SUS_MAP','CONFIG_KSU_SUSFS_OPEN_REDIRECT'}
print('Config differences:',json.dumps(missing))
if any(item['symbol'] in core for item in missing):
    raise SystemExit('Required feature was lost during olddefconfig')
