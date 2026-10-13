#!/usr/bin/env python3
import hashlib,json,sys,zipfile
from pathlib import Path
p=Path(sys.argv[1])
for slot in ('a','b'):
 dest=p.with_name(p.stem+f'-Slot-{slot.upper()}'+p.suffix)
 with zipfile.ZipFile(p) as src,zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
  for info in src.infolist():
   data=src.read(info.filename)
   if info.filename=='anykernel.sh':data=data.replace(b'onyx_slot_override=\n',f'onyx_slot_override=_{slot}\n'.encode())
   if info.filename=='build-manifest.json':
    m=json.loads(data);m['installer_slot_override']='_'+slot;data=(json.dumps(m,indent=2)+'\n').encode()
   out.writestr(info,data)
 with zipfile.ZipFile(dest) as z:assert z.testzip() is None
 dest.with_name(dest.name+'.sha256').write_text(hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name+'\n')
 print(dest)
