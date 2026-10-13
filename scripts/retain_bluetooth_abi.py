#!/usr/bin/env python3
from pathlib import Path
path=Path('/root/onyx-kernel-dev/kernel/net/bluetooth/hci_sysfs.c')
text=path.read_text()
# This Android branch does not allocate hci_dev::srcu (or expose it in its ABI).
# There is consequently no srcu instance to release on the unused-device path.
assert '\t\tcleanup_srcu_struct(&hdev->srcu);\n' in text
path.write_text(text.replace('\t\tcleanup_srcu_struct(&hdev->srcu);\n','',1))
