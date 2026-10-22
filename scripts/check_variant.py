"""Require exclusive KPM selection and confirm KPM linked after compilation."""
from pathlib import Path
import os,subprocess,sys
r=Path(sys.argv[1]);suki=os.environ.get('ONYX_VARIANT','kernelsu')=='sukisu'
config=(r/'out/.config').read_text().splitlines()
assert ('CONFIG_KPM=y' in config)==suki,'KPM must be enabled exclusively for SukiSU'
if '--built' in sys.argv:
 symbols=subprocess.check_output(['llvm-nm-21','--defined-only',str(r/'out/vmlinux')],text=True)
 assert (' do_kpm\n' in symbols)==suki,'KPM implementation does not match variant'
print('Variant configuration/linkage verified; SukiSU also requires image backend validation')
