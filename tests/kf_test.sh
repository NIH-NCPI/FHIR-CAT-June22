#!/usr/bin/bash

curl $KF_FHIR/ResearchStudy \
   -H "Accept: application/fhir+json" \
   --cookie $KF_COOKIE