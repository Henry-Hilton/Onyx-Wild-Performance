from pathlib import Path
import tempfile,subprocess,sys,os
p=Path(sys.argv[1])
with tempfile.TemporaryDirectory(prefix='onyx-preinit-') as td:
 t=Path(td);b=t/'runner';meta=t/'metadata';meta.mkdir()
 args=['clang-21','-std=gnu11','-Os','-static','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-I'+str(p/'preinit/runner/nolibc'),'-I'+str(p/'include'),'-DINIT_PATH="/bin/echo"',f'-DKSU_DIR_DEFAULT="{meta}"',f'-DKSU_DIR_VOLD="{t}/absent-vold"',f'-DKSU_DIR_WATCHDOG="{t}/absent-watchdog"',f'-DKMSG_PATH="{t}/kmsg"',str(p/'preinit/runner/runner.c'),'-o',str(b)]
 args.insert(1,f'-DOWNER_UID={os.getuid()}')
 subprocess.run(args,check=True)
 def run():
  result=subprocess.run([str(b),'selinux_setup'],capture_output=True,text=True,timeout=8)
  assert result.returncode==0 and result.stdout.strip()=='selinux_setup',result
 run() # No modules: real init replacement still receives original arguments.
 mod=meta/'preinit/test';mod.mkdir(parents=True);target=t/'result';target.write_text('')
 (mod/'preinit.conf').write_text(f'write {target} port-ok\n')
 run();assert target.read_text().strip()=='port-ok'
 target.write_text('');(mod/'preinit.conf').chmod(0o666)
 run();assert target.read_text()=='' # Reject unsafe configuration ownership/mode.
 (mod/'preinit.conf').chmod(0o600);(meta/'.preinit_bootcount').write_text('3\n')
 run();assert target.read_text()=='' # Boot-loop protection still resumes init.
 print('Runner tests passed: passthrough, action execution, unsafe config, bootcount limit.')
