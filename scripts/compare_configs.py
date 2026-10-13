#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/root/onyx-kernel-dev')
def config(path):
    result = {}
    for line in path.read_text().splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            result[key] = value
        elif re.fullmatch(r'# CONFIG_\w+ is not set', line):
            result[line.split()[1]] = 'n'
    return result

base = config(ROOT/'config-xiaomi/.config')
for tree, filename in [('gki-clo', 'capybara_defconfig'), ('konoha', 'konoha_defconfig')]:
    other = config(ROOT/('config-'+tree)/'.config')
    print('\n===', tree, 'differences from Xiaomi GKI ===')
    for key in sorted(base.keys() | other.keys()):
        if base.get(key) != other.get(key):
            if key in base or other.get(key) not in ('n', '<default>'):
                print(key, base.get(key, '<default>'), '->', other.get(key, '<default>'))
