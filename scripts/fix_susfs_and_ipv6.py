#!/usr/bin/env python3
from pathlib import Path
root=Path('/root/onyx-kernel-dev')
path=root/'kernel/net/ipv6/addrconf.c'
text=path.read_text().replace('\t\t\t\tfib6_add_gc_list(f6i);\n','')
path.write_text(text)
path=root/'kernelsu/kernel/feature/selinux_hide.c'
text=path.read_text()
old='''    if (security_dump_masked_av_fn)
        security_dump_masked_av_fn(policydb, scontext, tcontext, tclass, masked, "bounds");'''
new='''    security_dump_masked_av_fn(policydb, scontext, tcontext, tclass, masked, "bounds");'''
assert old in text
text=text.replace(old,new,1)
old='''    if (context_struct_compute_av_fn) {
        context_struct_compute_av_fn(policydb, scontext, tcontext, tclass, avd, NULL);
    } else {
        context_struct_compute_av(policydb, scontext, tcontext, tclass, avd, NULL);
    }'''
new='''    context_struct_compute_av_fn(policydb, scontext, tcontext, tclass, avd, NULL);'''
assert old in text
path.write_text(text.replace(old,new,1))
