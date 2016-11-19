@echo on
net start vmci
net start vmx86
net start VMnetuserif
cd "D:\Program Files (x86)\VMware\VMware Workstation"
"D:\Program Files (x86)\VMware\VMware Workstation\VMrun" -T ws start "C:\Ubuntu 64-bit - dlab.vmwarevm\Clone of Ubuntu 64-bit - dlab.vmx"
@pause