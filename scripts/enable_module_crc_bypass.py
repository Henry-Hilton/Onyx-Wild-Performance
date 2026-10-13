#!/usr/bin/env python3
"""Apply gki-clo's symbol CRC mismatch acceptance to the working kernel."""
from pathlib import Path
p=Path('/root/onyx-kernel-dev/kernel/kernel/module/version.c')
s=p.read_text()
old='bad_version:\n\tpr_warn("%s: disagrees about version of symbol %s\\n", info->name, symname);\n\treturn 0;'
new='''bad_version:
	/* Match gki-clo: permit prebuilt modules with differing symbol CRCs. */
	pr_warn("%s: disagrees about version of symbol %s; forcing load (CRC bypass)\\n",
		info->name, symname);
	return 1;'''
assert old in s
p.write_text(s.replace(old,new))
