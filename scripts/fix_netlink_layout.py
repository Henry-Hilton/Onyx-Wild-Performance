#!/usr/bin/env python3
from pathlib import Path
p=Path('/root/onyx-kernel-dev/kernel/include/net/genetlink.h')
s=p.read_text();start=s.index('struct genl_multicast_group {');end=s.index('};',start)
before=s[:end+2];after=s[end+2:].replace('\tu8\t\t\tcap_sys_admin:1;\n','')
p.write_text(before+after)
