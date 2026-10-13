#!/usr/bin/env python3
from pathlib import Path
root=Path('/root/onyx-kernel-dev/kernel')
path=root/'net/ipv6/addrconf.c'
text=path.read_text()
old='''\t\t\t\tfib6_set_expires(f6i, expires);
\t\t\tfib6_info_release(f6i);'''
new='''\t\t\t\tfib6_set_expires(f6i, expires);
\t\t\t\tfib6_add_gc_list(f6i);

\t\t\t\tspin_unlock_bh(&table->tb6_lock);
\t\t\t}
\t\t\tfib6_info_release(f6i);'''
assert old in text
path.write_text(text.replace(old,new,1))
