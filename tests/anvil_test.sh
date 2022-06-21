#!/usr/bin/bash

curl $ANVIL_FHIR/ResearchStudy \
   -H "Accept: application/fhir+json" \
   -H "Authorization: Bearer $(gcloud auth print-access-token)"