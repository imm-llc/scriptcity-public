#!/usr/bin/env bash
# curl --silent http://kickstart/xenutil/xen.sh | bash
dash="============================================"
echo "${dash}"
echo "Downloading Xen Guest Utils"

curl -o /tmp/xen.tgz http://kickstart/xenutil/xen-guest-util.tgz
echo "${dash}"
echo "Downloaded Xen Guest Utils"
cd /tmp/ && tar zxvf xen.tgz
echo "${dash}"
echo "Unpacked Xen Guest Utils"
echo "${dash}"
echo "Installing Xen Guest Utils"
sleep 1
/tmp/Linux/install.sh -n 1> /dev/null
echo "${dash}"
echo "Installed Xen Guest Utils"
echo "${dash}"
echo "Rebooting in 5 seconds"
sleep 5
reboot
