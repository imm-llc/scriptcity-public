#!/usr/bin/env bash

# Open SMB path in finder
open smb://fileserver/it
# We need to wait for this to mount
# When mounted, we'll have a /Volumes/it/ directory
while [ ! -d /Volumes/it ]
do
echo "Waiting for SMB Mount"
sleep 2
done
# Our SMB mount now lives here
SMB_PATH=/Volumes/it

echo ""
echo "**************************************"
echo ""
echo ""
# Get root easily and obviously
echo "Enter it password below"
echo ""
sudo echo "STARTING PROVISIONING"

read -p "Enter new hostname: " NEW_HN

NEW_HOSTNAME=$(echo ${NEW_HN}|tr a-z A-Z)

echo ""
echo "Setting hostname to: ${NEW_HOSTNAME}"
echo ""

# This is the hostname that shows in terminal and what we see in AD
sudo scutil --set HostName ${NEW_HOSTNAME}

# ComputerName is what shows in SysPref>Sharing

sudo scutil --set ComputerName ${NEW_HOSTNAME}

echo ""
echo "Stopping cups daemon"
echo ""

# Stop cupsd
sudo launchctl unload /System/Library/LaunchDaemons/org.cups.cupsd.plist

echo ""
echo "Installing printer driver"
echo ""

# Install driver
sudo cp "${SMB_PATH}"/New\ Computer\ Setup/Mac/SharpPrinter/MX-C26.pkg /Users/it/
sudo installer -allowUntrusted -pkg /Users/it/MX-C26.pkg -target /

# Copy printer config - unused, doesn't work
# sudo cp $SMB_PATH/New\ Computer\ Setup/Mac/SharpPrinter/printers.conf /etc/cups/printers.conf
# sudo cp $SMB_PATH/New\ Computer\ Setup/Mac/SharpPrinter/printers.conf /etc/cups/printers.conf.O

sudo cp $SMB_PATH/New\ Computer\ Setup/Mac/SharpPrinter/BHI_MFP.ppd /etc/cups/ppd/Sharp.ppd

echo ""
echo "Starting cups daemon"
echo ""

# Start cupsd, can't use lpadmin without it
sudo launchctl load /System/Library/LaunchDaemons/org.cups.cupsd.plist

echo ""
echo "Installing Sharp MFP"
echo ""

sudo lpadmin -p Sharp -L "Boulder" -E -v lpd://fileserver -P /Library/Printers/PPDs/Contents/Resources/SHARP\ MX-3610N.PPD.gz -o Option5=3TrayDrawer

echo ""
echo "Installing MDM profiles"
echo ""

# Install profiles
sudo /usr/bin/profiles -I -v -F "${SMB_PATH}"/New\ Computer\ Setup/Mac/profiles/Settings_for_Provisioners.mobileconfig
sudo /usr/bin/profiles -I -v -F "${SMB_PATH}"/New\ Computer\ Setup/Mac/profiles/Trust_Profile_for_IT.mobileconfig
#sudo /usr/bin/profiles -I -v -F "${SMB_PATH}"/New\ Computer\ Setup/Mac/profiles/mdm_profile.mobileconfig
sudo /usr/bin/profiles -I -v -F "${SMB_PATH}"/New\ Computer\ Setup/Mac/profiles/Mac_Enrollment_Profile.mobileconfig

echo ""
echo "*****************************"

read -p "Press enter once profiles are finished adding to this machine and you have approved the Remote Management profile" e

echo "******************************"
echo ""
echo "Setting printer defaults"
echo ""

if [ -f /etc/cups/ppd/Sharp.ppd ]
then
  sudo sed -i.bu 's/DefaultARCMode: CMAuto/DefaultARCMode: CMBW/' /etc/cups/ppd/Sharp.ppd
else
  sudo sed -i.bu 's/DefaultARCMode: CMAuto/DefaultARCMode: CMBW/' /etc/cups/ppd/mcx_0.ppd
fi

if [ -f /etc/cups/ppd/mcx_0.ppd ]
then
  sudo sed -i.bu 's/DefaultARCMode: CMAuto/DefaultARCMode: CMBW/' /etc/cups/ppd/mcx_0.ppd
fi


# Install Meraki Agent
sudo installer -pkg "${SMB_PATH}"/New\ Computer\ Setup/Mac/MerakiMacAgent.pkg -target /

# Install WatchGuard Client 
sudo installer -pkg "${SMB_PATH}"/New\ Computer\ Setup/Mac/WatchGuardVPN.mpkg -target /

# Install MWB

sudo installer -pkg "${SMB_PATH}"/New\ Computer\ Setup/Mac/Setup.MBEndpointAgent.pkg -target /

# Installing Chrome is sort of tricky because it's a .app, not a .pkg - we can't use `installer`

# hdiutil is a macOS tool for working with disk images
sudo hdiutil attach "${SMB_PATH}"/New\ Computer\ Setup/Mac/googlechrome.dmg

# We want to copy the entier Google Chrome.app folder to /Applications, not just the contents of the folder
sudo cp -R /Volumes/Google\ Chrome/Google\ Chrome.app /Applications/

# detach our dmg
sudo hdiutil detach /Volumes/Google\ Chrome

echo ""
echo "**********************"
echo ""
echo "Adding device to Snipe-IT"
echo ""

bash <(curl --silent http://yum/mac/snipeit.sh)

echo ""
echo ""
echo "**************************"
echo ""
echo "Initial provisioning complete"
echo ""
echo "You should now restart the computer and have the new primary user login"
echo ""
echo "After they have logged in, run: "
echo "bash <(http://yum/mac/acct.sh)"
echo ""
echo "Exiting"
exit 0
