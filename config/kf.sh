#!/usr/bin/bash

export KF_FHIR="https://kf-api-fhir-service.kidsfirstdrc.org/ "

#The file should be a plain text file containing only the complete cookie value.
echo "Log into https://kf-api-fhir-service.kidsfirstdrc.org/ and retrieve the cookie value for key 'AWSELBAuthSessionCookie-0'. Store that value in a plain text file to reference next (file), or simply paste it at the prompt (text)."

read -p "Kids First Cookie is File or Text [F/t]:" kf_type
kf_type=${kf_type:-F}

if [ "$kf_type" == "t" ]; then
 read -p "Enter Kids First cookie value:" kf_cookie
else
 read -p "Enter Kids First cookie filename [~/config/kf_cookie]:" kf_cookie
 kf_cookie=${kf_cookie:-~/config/kf_cookie}
 kf_cookie=`cat $kf_cookie`
fi

export KF_COOKIE="AWSELBAuthSessionCookie-0=$kf_cookie"
