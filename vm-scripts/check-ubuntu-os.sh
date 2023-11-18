#!/bin/bash 

version=$(cat /etc/issue | awk '{print $2}')
echo -e "[+] Checking ubuntu os version"
if [ $(printf '%s\n' "20.04" "$version" | sort -V | tail -n 1) = "$version" ]; then 
    exit 0
else 
    exit 1
fi