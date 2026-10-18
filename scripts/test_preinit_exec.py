"""Exercise the actual exec wrapper with mocked kernel exec/ownership boundaries."""
from pathlib import Path
import subprocess,sys,tempfile
source=Path(sys.argv[1]).read_text()
start=source.index('static int do_execveat_common(int fd, struct filename *filename,')
wrapper=source[start:source.index('int kernel_execve(',start)]
prefix=r'''
#include <assert.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>
#define CONFIG_KSU_SUSFS 1
#define AT_FDCWD -100
#define AT_EMPTY_PATH 0x1000
#define __user
#define unlikely(x) (x)
#define IS_ERR_OR_NULL(x) (!(x))
#define pr_warn(...) ((void)0)
struct filename { const char *name; } original={"/system/bin/init"}, runner={"runner"};
struct user_arg_ptr { const char **args; };
struct task { int pid; } task={1};
#define current (&task)
static int calls,prepared,closed,released,fail_runner,fatal,disable_runner;
static const char *get_user_arg_ptr(struct user_arg_ptr a,int i) { return a.args[i]; }
static int fatal_signal_pending(struct task *t) { return fatal; }
static void close_fd(int fd) { assert(fd==42);closed++; }
static void putname(struct filename *f) { assert(f==&original);released++; }
struct filename *ksu_handle_preinit(struct filename *f,const char *arg,int *fd) {
 prepared++;assert(f==&original);assert(!strcmp(arg,"selinux_setup"));
 if(disable_runner)return NULL;*fd=42;return &runner;
}
static int onyx_do_execveat_common(int fd,struct filename *f,struct user_arg_ptr a,
                                  struct user_arg_ptr e,int flags) {
 calls++;
 if(f==&runner){assert(fd==AT_FDCWD && flags==0);return fail_runner?-8:0;}
 assert(f==&original);return 0;
}
'''
tests=r'''
static void reset(void) { calls=prepared=closed=released=fail_runner=fatal=disable_runner=0;task.pid=1; }
int main(void) {
 const char *args[]={"/system/bin/init","selinux_setup",NULL};
 struct user_arg_ptr a={args};
 reset();assert(!do_execveat_common(AT_FDCWD,&original,a,a,0));assert(prepared==1&&calls==1&&released==1&&!closed);
 reset();assert(!do_execveat_common(123,&original,a,a,0));assert(prepared==1&&calls==1);
 reset();assert(!do_execveat_common(123,&original,a,a,0x100));assert(prepared==1&&calls==1);
 reset();assert(!do_execveat_common(123,&original,a,a,AT_EMPTY_PATH));assert(!prepared&&calls==1);
 reset();task.pid=2;assert(!do_execveat_common(AT_FDCWD,&original,a,a,0));assert(!prepared&&calls==1);
 reset();fail_runner=1;assert(!do_execveat_common(AT_FDCWD,&original,a,a,0));assert(calls==2&&closed==1&&!released);
 reset();fail_runner=fatal=1;assert(do_execveat_common(AT_FDCWD,&original,a,a,0)==-8);assert(calls==1&&closed==1&&released==1);
 reset();disable_runner=1;assert(!do_execveat_common(AT_FDCWD,&original,a,a,0));assert(calls==1&&!closed&&!released);
 return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='onyx-exec-test-') as tmp:
 p=Path(tmp);(p/'test.c').write_text(prefix+wrapper+tests)
 subprocess.run(['clang-21','-Wall','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Exec wrapper tests passed: execveat flags/fd, PID filtering, fallback and cleanup.')
