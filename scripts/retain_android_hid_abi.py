#!/usr/bin/env python3
from pathlib import Path
import subprocess
kernel=Path('/root/onyx-kernel-dev/kernel')
# Android already backported the buffer-size check behind a new __hid symbol
# and retained the old exported wrapper. The mainline 6.6.143 name changes
# would break existing Android modules, so retain this equivalent ABI backport.
for name in ('drivers/hid/hid-core.c','drivers/hid/hid-gfrm.c',
             'drivers/hid/hid-logitech-hidpp.c','drivers/hid/hid-multitouch.c',
             'drivers/hid/hid-primax.c','drivers/hid/hid-vivaldi-common.c',
             'drivers/hid/wacom_sys.c','drivers/staging/greybus/hid.c','include/linux/hid.h'):
    original=subprocess.check_output(['git','show',f'HEAD:{name}'],cwd=kernel)
    (kernel/name).write_bytes(original)
