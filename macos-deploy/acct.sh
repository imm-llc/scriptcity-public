#!/usr/bin/env bash

# Not a huge fan of making users local admin but here we are 
# 
echo ""
echo "***********************"
echo ""

read -p "Type the primary user's sAMAccountName (e.g. jdoe): " samacctname

echo ""
echo "Ensuring user is an admin"
echo ""

sudo dscl . -append /Groups/admin GroupMembership $samacctname

echo ""
echo "Ensuring user is a mobile account"
echo ""

if ! dscl /Local/Default -list Users | grep -i $samacctname
then
  echo ""
  echo "***************************"
  echo "USER ${samacctname} NOT FOUND IN MOBILE USERS"
  echo ""
else
  echo ""
  echo "Mobile account check passed [X]"
fi

echo ""
echo "Checks complete"
echo "Exiting" 
echo ""
exit 0

