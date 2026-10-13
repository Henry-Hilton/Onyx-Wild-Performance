#!/usr/bin/env python3
from pathlib import Path
import re
for name in ('xiaomi', 'konoha', 'gki-clo'):
    root=Path('/root/onyx-kernel-dev')/name
    print('===', name, '===')
    for file in root.rglob('Kconfig*'):
        if not file.is_file():
            continue
        for match in re.finditer(r'^\s*source\s+"([^"$]+)"', file.read_text(errors='replace'), re.M):
            target=match.group(1)
            if not (root/target).is_file():
                print(file.relative_to(root), target)
