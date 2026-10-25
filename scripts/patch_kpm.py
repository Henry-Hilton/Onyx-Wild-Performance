"""Install and inspect the real KPM image backend; CONFIG_KPM alone is insufficient."""
from pathlib import Path
import gzip,hashlib,json,os,re,secrets,subprocess,sys
r,w=map(Path,sys.argv[1:]);out=r/'out';lock=json.loads((w/'sources.lock.json').read_text())
variant=os.environ.get('ONYX_VARIANT',lock.get('root_variant','kernelsu'))
enabled='CONFIG_KPM=y' in (out/'.config').read_text().splitlines()
assert enabled==(variant=='sukisu'),'KPM is exclusive to SukiSU'
raw=out/'arch/arm64/boot/Image';compressed=raw.with_name('Image.gz')
def sha(data):return hashlib.sha256(data).hexdigest()
original=raw.read_bytes();assert original[56:60]==b'ARM\x64'
report={'enabled':enabled,'compiled_image_sha256':sha(original),'backend_patched':False}
if enabled:
 tools=r/'kpm_tools';payload=r/'kpm_payload/kpm/kpimg';pin=lock['kpm_tools']
 for repo,expected in ((tools,pin['source']['commit']),(r/'kpm_payload',pin['payload_source']['commit'])):
  if (repo/'.git').exists():
   assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==expected
 payload_bytes=payload.read_bytes();assert sha(payload_bytes)==pin['payload_sha256']
 for symbol in (b'sukisu_kpm_supercall_install',b'__arm64_sys_truncate'):
  assert symbol in payload_bytes,'Payload lacks SukiSU KPM bridge'
 # The bridge replaced the legacy stub hooks. Require the pinned kernel and
 # backend sources to agree on every public framing tag and ABI version.
 headers=[(r/'kernel/drivers/kernelsu/extension/kpm/bridge.h').read_text(),
          (tools/'kernel/patch/sukisu/supercall.h').read_text()]
 framing={}
 for name in ('SUKISU_KPM_SUPERCALL_MAGIC','SUKISU_KPM_SUPERCALL_MAGIC2',
              'SUKISU_KPM_SUPERCALL_MAGIC3','SUKISU_KPM_ABI_VERSION'):
  values=[re.search(r'^#define\s+'+name+r'\s+(0x[0-9a-fA-F]+|[0-9]+)',h,re.M) for h in headers]
  assert all(values),'Missing KPM bridge definition: '+name
  parsed=[int(v[1],0) for v in values]
  assert parsed[0]==parsed[1],'KPM bridge mismatch: '+name
  framing[name]=parsed[0]
 subprocess.run(['make','-C',str(tools/'tools'),'-j2'],check=True,stdout=subprocess.DEVNULL)
 tool=tools/'tools/kptools';patched=raw.with_name('Image.kpm')
 unpatched=subprocess.run([str(tool),'-l','-i',str(raw)],text=True,capture_output=True,check=True).stdout
 assert 'patched=false' in unpatched,'Expected a freshly compiled, unpatched image'
 # Pass a random verifier key via stdin, never via process arguments or logs.
 result=subprocess.run([str(tool),'-p','-i',str(raw),'-k',str(payload),'--root-skey-fd','0','-o',str(patched)],input=secrets.token_hex(24)+'\n',text=True,capture_output=True)
 (out/'kpm-patch.log').write_text(result.stdout+result.stderr)
 assert result.returncode==0,'KPM backend patch failed; inspect kpm-patch.log'
 inspected=subprocess.run([str(tool),'-l','-i',str(patched)],text=True,capture_output=True,check=True).stdout
 assert 'patched=true' in inspected and 'arch=arm64' in inspected,'Backend inspection failed'
 data=patched.read_bytes();offset=data.find(b'KP1158\0\0');assert offset>=len(original)
 assert data[offset+8:offset+12]==payload_bytes[8:12],'Wrong KPM backend version'
 assert len(data)>=offset+len(payload_bytes) and data[56:60]==b'ARM\x64'
 branch=int.from_bytes(data[4:8],'little');assert branch&0xfc000000==0x14000000
 imm=branch&0x3ffffff;imm=imm-(1<<26) if imm&(1<<25) else imm
 target=4+(imm<<2)
 assert 0<=target<len(data) and data[4:8]!=original[4:8],'KPM entry hook missing'
 compressed.write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
 report.update(backend_patched=True,bridge_framing=framing,metadata_offset=offset,entry_target=target,payload_sha256=sha(payload_bytes),tool_source_commit=pin['source']['commit'],payload_source_commit=pin['payload_source']['commit'],patched_image_sha256=sha(data),negative_control='unpatched image: patched=false',inspection='patched=true; arch=arm64')
else:
 assert b'KP1158\0\0' not in gzip.decompress(compressed.read_bytes()),'Unexpected backend in KernelSU'
report['packaged_image_sha256']=sha(compressed.read_bytes())
(out/'kpm-backend-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('KPM backend patched and inspected' if enabled else 'KernelSU image unchanged; KPM disabled')
