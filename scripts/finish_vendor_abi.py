#!/usr/bin/env python3
from pathlib import Path
r=Path('/root/onyx-kernel-dev/kernel')
def edit(path,old,new):
 p=r/path;s=p.read_text();assert old in s,path;p.write_text(s.replace(old,new))
# Keep the prebuilt multicast group layout and flag semantics. The new
# namespace capability checks remain; the old capability bit also works.
edit('include/net/genetlink.h','#define GENL_MCAST_CAP_NET_ADMIN\tBIT(0)',
     '#define GENL_MCAST_CAP_NET_ADMIN\tGENL_UNS_ADMIN_PERM')
edit('include/net/genetlink.h','char\t\t\tname[GENL_NAMSIZ];\n\tu8\t\t\tflags;\n',
     'char\t\t\tname[GENL_NAMSIZ];\n\tu8\t\t\tflags;\n\tu8\t\t\tcap_sys_admin:1;\n')
edit('net/netlink/genetlink.c','if ((grp->flags & GENL_MCAST_CAP_SYS_ADMIN) &&',
     'if ((grp->cap_sys_admin || (grp->flags & GENL_MCAST_CAP_SYS_ADMIN)) &&')
# Driver shutdown uses the existing device_driver callback slot. This avoids
# extending a structure allocated by prebuilt Bluetooth drivers.
edit('include/linux/serdev.h','\tvoid\t(*shutdown)(struct serdev_device *);\n','')
edit('drivers/tty/serdev/core.c','''	const struct serdev_device_driver *sdrv =
		to_serdev_device_driver(dev->driver);

	if (dev->driver && sdrv->shutdown)
		sdrv->shutdown(to_serdev_device(dev));''','''	if (dev->driver && dev->driver->shutdown)
		dev->driver->shutdown(dev);''')
edit('drivers/tty/serdev/core.c','''static void serdev_legacy_shutdown(struct serdev_device *serdev)
{
	struct device *dev = &serdev->dev;
	struct device_driver *driver = dev->driver;

	driver->shutdown(dev);
}

''','')
edit('drivers/tty/serdev/core.c','''	if (!sdrv->shutdown && sdrv->driver.shutdown)
		sdrv->shutdown = serdev_legacy_shutdown;

''','')
p=r/'drivers/bluetooth/hci_qca.c';s=p.read_text()
s=s.replace('static void qca_serdev_shutdown(struct serdev_device *serdev)\n{',
'''static void qca_serdev_shutdown(struct device *dev)
{
	struct serdev_device *serdev = to_serdev_device(dev);''')
s=s.replace('\t.shutdown = qca_serdev_shutdown,\n','')
start=s.index('static struct serdev_device_driver qca_serdev_driver')
head=s[:start];tail=s[start:]
tail=tail.replace('\t.driver = {','\t.driver = {\n\t\t.shutdown = qca_serdev_shutdown,',1)
p.write_text(head+tail)
