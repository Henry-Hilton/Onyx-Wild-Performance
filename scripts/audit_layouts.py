#!/usr/bin/env python3
"""Compare selected vendor-facing BTF layouts with the supplied ROM kernel."""
import argparse,json,struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
def read_btf(path):
 with path.open('rb') as f:
  if f.read(4)==b'\x7fELF':
   f.seek(0);data=ELFFile(f).get_section_by_name('.BTF').data()
  else:
   f.seek(0);data=f.read()
 magic,version,flags,hdr,t_off,t_len,s_off,s_len=struct.unpack_from('<HBB5I',data)
 assert magic==0xeb9f and version==1
 strings=data[hdr+s_off:hdr+s_off+s_len]
 def name(offset):return strings[offset:strings.index(b'\0',offset)].decode()
 types=[{'kind':0,'size':0,'name':'void'}];pos=hdr+t_off;end=pos+t_len
 while pos<end:
  no,info,size=struct.unpack_from('<III',data,pos);pos+=12
  kind=(info>>24)&31;vlen=info&0xffff
  extra={1:4,3:12,4:vlen*12,5:vlen*12,6:vlen*8,13:vlen*8,14:4,15:vlen*12,17:4,19:vlen*12}.get(kind,0)
  item={'kind':kind,'name':name(no),'size':size,'members':[]}
  if kind in (4,5):
   for i in range(vlen):
    mn,mt,mo=struct.unpack_from('<III',data,pos+i*12)
    item['members'].append({'name':name(mn),'type':mt,'offset':mo&0xffffff if info>>31 else mo,
                            'bits':mo>>24 if info>>31 else 0})
  if kind==3:item['array']=struct.unpack_from('<III',data,pos)
  types.append(item);pos+=extra
 return types
def layouts(types,names):
 def size(i):
  t=types[i];k=t['kind']
  if k==2:return 8
  if k in (8,9,10,11,18):return size(t['size'])
  if k==3:return size(t['array'][0])*t['array'][2]
  return t['size'] if k in (1,4,5,6,16,19) else 0
 def fields(i,base=0):
  result={}
  for m in types[i]['members']:
   if not m['name'] and types[m['type']]['kind'] in (4,5):
    result.update(fields(m['type'],base+m['offset']))
   elif m['name']:
    result[m['name']]={'offset_bits':base+m['offset'],'size_bytes':size(m['type']),'bitfield_width':m['bits']}
  return result
 result={}
 for i,t in enumerate(types):
  if t['kind']==4 and t['name'] in names:
   result[t['name']]={'size_bytes':t['size'],'fields':fields(i)}
 return result
p=argparse.ArgumentParser();p.add_argument('stock',type=Path);p.add_argument('built',type=Path);p.add_argument('output',type=Path);p.add_argument('--write-baseline',type=Path);a=p.parse_args()
names={'task_struct','net_device','sk_buff','sock','tcp_sock','file','inode','page','cma','rc_dev','tc_action','serdev_device_driver','genl_multicast_group','genl_ops','genl_split_ops'}
old=json.loads(a.stock.read_text()) if a.stock.suffix=='.json' else layouts(read_btf(a.stock),names)
if a.write_baseline:a.write_baseline.write_text(json.dumps(old,indent=2)+'\n')
new=layouts(read_btf(a.built),names);errors=[];reports={}
for name in sorted(names):
 if name not in old or name not in new:
  reports[name]={'status':'not available in both BTF inputs'};errors.append(name);continue
 differences=[]
 if old[name]['size_bytes']!=new[name]['size_bytes']:differences.append('structure size')
 for field,layout in old[name]['fields'].items():
  if field.startswith('android_kabi_reserved') or field=='unused':continue
  if new[name]['fields'].get(field)!=layout:differences.append(field)
 reports[name]={'stock_size':old[name]['size_bytes'],'built_size':new[name]['size_bytes'],'differences':differences}
 if differences:errors.append(name)
result={'scope':'Selected structure sizes and member offsets; not a complete runtime ABI proof','structures':reports,'mismatches':errors}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if errors:raise SystemExit(1)
