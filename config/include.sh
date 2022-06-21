#!/usr/bin/bash

export INCLUDE_FHIR="https://include-api-fhir-service.includedcc.org"

#The file should be a plain text file containing only the complete cookie value.
echo "Log into https://include-api-fhir-service.includedcc.org and retrieve the cookie value for key 'AWSELBAuthSessionCookie-0'. Store that value in a plain text file to reference next (file), or simply paste it at the prompt (text)."

read -p "INCLUDE Cookie is File or Text [F/t]:" i_type
i_type=${i_type:-F}

if [ "$i_type" == "t" ]; then
 read -p "Enter INCLUDE cookie value:" i_cookie
else
 read -p "Enter INCLUDE cookie filename [~/config/include_cookie]:" i_cookie
 i_cookie=${i_cookie:-~/config/include_cookie}
 i_cookie=`cat $i_cookie`
fi

export INCLUDE_COOKIE="AWSELBAuthSessionCookie-0=$i_cookie"
