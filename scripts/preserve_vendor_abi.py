#!/usr/bin/env python3
"""Adapt stable backports without changing vendor-visible structure layouts."""
from pathlib import Path
root=Path('/root/onyx-kernel-dev/kernel')
def edit(path,old,new):
    p=root/path
    s=p.read_text()
    assert old in s,path
    p.write_text(s.replace(old,new))
# Keep the stable RCU lifetime fix; store its bookkeeping after the allocation,
# rather than inserting a field into the exported tc_action structure.
edit('include/net/act_api.h','\tstruct rcu_head         tcfa_rcu;\n','')
edit('net/sched/act_api.c','static void free_tcf(struct tc_action *p)', '''struct tcf_deferred_free {
	struct rcu_head rcu;
	void *allocation;
};

static void tcf_deferred_free_rcu(struct rcu_head *head)
{
	struct tcf_deferred_free *deferred =
		container_of(head, struct tcf_deferred_free, rcu);

	kfree(deferred->allocation);
}

static void free_tcf(struct tc_action *p)''')
edit('net/sched/act_api.c','\tkfree_rcu(p, tcfa_rcu);','''	struct tcf_deferred_free *deferred = (void *)p +
		ALIGN(p->ops->size, __alignof__(struct tcf_deferred_free));

	deferred->allocation = p;
	call_rcu(&deferred->rcu, tcf_deferred_free_rcu);''')
edit('net/sched/act_api.c','kzalloc(ops->size, GFP_KERNEL)',
     'kzalloc(ALIGN(ops->size, __alignof__(struct tcf_deferred_free)) +\n\t\t\t\t      sizeof(struct tcf_deferred_free), GFP_KERNEL)')
# The removed field is still part of the stock module ABI. Retain its slot.
edit('include/media/rc-core.h','\tstruct device\t\t\tdev;\n',
     '\tstruct device\t\t\tdev;\n\tbool\t\t\t\tmanaged_alloc;\n')
# Preserve the exported legacy kernel mapping function. New in-tree callers
# continue using the stable user-protection sanitization through the inline.
edit('arch/arm64/include/asm/io.h','static inline void __iomem *ioremap_prot(',
     'void __iomem *ioremap_prot(phys_addr_t phys, size_t size, unsigned long prot);\n\nstatic inline void __iomem *ioremap_user_prot(')
edit('arch/arm64/include/asm/io.h','#define ioremap_prot ioremap_prot',
     '#define ioremap_prot ioremap_user_prot')
edit('arch/arm64/mm/ioremap.c','EXPORT_SYMBOL(__ioremap_prot);', '''EXPORT_SYMBOL(__ioremap_prot);

/* ABI entry point used by prebuilt, trusted kernel modules. */
#undef ioremap_prot
void __iomem *ioremap_prot(phys_addr_t phys, size_t size, unsigned long prot)
{
	return __ioremap_prot(phys, size, __pgprot(prot));
}
EXPORT_SYMBOL(ioremap_prot);''')
