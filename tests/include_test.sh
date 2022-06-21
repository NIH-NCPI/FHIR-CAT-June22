#!/usr/bin/bash

curl $INCLUDE_FHIR/ResearchStudy \
   -H "Accept: application/fhir+json" \
   --cookie $INCLUDE_COOKIE