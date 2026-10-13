#!/usr/bin/env python3
from pathlib import Path
root=Path('/root/onyx-kernel-dev/kernel')
path=root/'fs/proc/task_mmu.c'
text=path.read_text()
anchor='static int show_smap(struct seq_file *m, void *v)\n{\n\tstruct vm_area_struct *vma = v;\n\tstruct mem_size_stats mss;\n'
assert anchor in text
text=text.replace(anchor,anchor+'''
#ifdef CONFIG_KSU_SUSFS_SUS_MAP
\tif (vma->vm_file && SUSFS_IS_INODE_SUS_MAP(file_inode(vma->vm_file)))
\t\treturn 0;
#endif
''',1)
path.write_text(text)
path=root/'net/ipv4/tcp_input.c'
text=path.read_text()
assert text.count('tcp_process_tlp_ack(sk, ack, flag);')==1
path.write_text(text.replace('tcp_process_tlp_ack(sk, ack, flag);','tcp_process_tlp_ack(sk, ack, flag, &rs);'))
# The other BBR reject changes only a comment; retain current upstream wording.
for name in ('fs/proc/task_mmu.c.rej','net/ipv4/tcp_input.c.rej'):
    source=root/name
    dest=Path('/root/onyx-kernel-dev/port-evidence')/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    source.rename(dest)
