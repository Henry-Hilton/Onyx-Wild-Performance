#!/usr/bin/env python3
from pathlib import Path
import re
root=Path('/root/onyx-kernel-dev/kernel')
pattern=re.compile(r'^<<<<<<< OEM\n(.*?)^=======\n(.*?)^>>>>>>> v6\.6\.143\n',re.M|re.S)
for name in ('drivers/scsi/scsi_lib.c','mm/memory.c','mm/mempolicy.c','mm/migrate.c'):
    path=root/name
    text=path.read_text()
    def resolve(match):
        ours,theirs=match.groups()
        if name=='drivers/scsi/scsi_lib.c':
            assert ours==theirs
            return ours
        # Retain Android's folio conversions and per-walk failure accounting,
        # while using the stable update's renamed hugetlb isolation helper.
        return ours.replace('isolate_hugetlb(', 'folio_isolate_hugetlb(')
    text=pattern.sub(resolve,text)
    path.write_text(text)
