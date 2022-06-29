#!/usr/env python

from csv import DictReader
from pathlib import Path

# wstlr is the name of the library from NCPI Whistler, the framework I've written
# to automate the projection of CSV data into FHIR resourses using Google's 
# Whistle language. I'm just borrowing the host configuration reader to simplify
# the script. This file contains the various server authentication details and
# endpoint information to permit simple targeting of resources (such as dev vs qa or
# prod or even completely different types of FHIR servers)
from wstlr.hostfile import load_hosts_file
from collections import defaultdict

# This is a wrapper for the KF Fhir API client. This uses the information from the host
# selection made by the user to authenticate and interact with the FHIR server.
from ncpi_fhir_client.fhir_client import FhirClient

import csv
import pdb

# GTEX, include and kf are arbitrary keys initially used to point to the 
# files where the original URIs to be explored were found (these were provided
# by Robert). 
input = {
	"GTEX": "data/gtex.tsv",
	"include": "data/include.tsv",
	"kf": "data/kf.tsv"
}

# Just a cheat to move GTEX to the back since it takes far longer than the other two
# combined to complete. Necessary to verify no additional errors were encountered with
# data in either of the other two servers
study_order = ["include", "kf", "GTEX"]

# fhir-cat, prod-kf-inc and kf are keys from the hosts file associated with authentication
# and endpoint details required for communicating with the remote servers.
srvr = {
	"GTEX": "fhir-cat",
	"include": "prod-kf-inc",
	"kf": "kf"
}

# Recursive function to crawl up the specimen tree to find the root node (probably Blood or
# Saliva)
def get_tissue_display(client, ref):
	if 'Specimen' in ref:
		response = client.get(ref)
		if len(response.entries) > 0:
			resource = response.entries[0]

			if 'resource' in resource:
				resource = resource['resource']

			assert(response.success())
			if 'parent' in response.entries[0]:
				#pdb.set_trace()
				# Is it safe to assume only one parent? For now, yes, but later that may not be true
				return get_tissue_display(client, resource['parent'][0]['reference'])
			else:
				if 'type' not in resource:
					pdb.set_trace()
				return resource['type']['coding'][0]['display']

		else:
			print(f"Skipping specimen reference because the query returned {len(response.entries)}")

# Boring wrapper to pull data into a uniform format regardless whether we are using a query
# or specifying an exact resource			
def get_resource(client, ref):
	response = client.get(ref)

	assert(response.success())
	resource = response.entries[0]

	if 'resource' in resource:
		resource = resource['resource']

	return resource

# We can use the cheat if it exists, but not everything is linked with meta.tags so 
# we crawl up to the ResearchSubject and get a reference for the study from there
def get_study(client, patient_resource):
	if 'tag' in patient_resource['meta']:
		study_id = patient_resource['meta']['tag'][0]['code']
		return get_resource(client, f"ResearchStudy?identifier={study_id}")
	else:
		research_subj = get_resource(client, f"ResearchSubject?patient=Patient/{patient_resource['id']}")
		return get_resource(client, research_subj['study']['reference'])

host_config = load_hosts_file("fhir_hosts")

# For some reason, the title didn't make it into the FHIR representation of the 
# research study for the GTEX load
titles = {
	"GTEX": "Genotype-Tissue Expression (GTEx)"
}

Path("output").mkdir(exist_ok=True, parents=True)
new_filename= "output/patient_details.tsv"
with open(new_filename, 'wt') as outf:
	writer = csv.writer(outf, delimiter='\t', quotechar='"')

	writer.writerow([
		"docref_uri",
		"tissue_type",
		"condition_disease",
		"study_name",
		"patient_sex"
	])	


	for study in study_order:
		filename = input[study]

		print(f"Pulling data for {study} from {filename}")

		client = FhirClient(host_config[srvr[study]])
		with open(filename, 'rt') as f:
			reader = DictReader(f, delimiter='\t', quotechar='"')

			for line in reader:
				specuri = line.get("specimen_uri")

				tissue_type=""

				# Not everything has a specimen properly provided at the docref
				if specuri:
					id = specuri.split("/")[-1]
					tissue_type = get_tissue_display(client, f"Specimen/{id}")
			
				# We are assuming that there is always a patient (which is currently
				# a valid assumption)
				paturi = line.get("patient_uri")
				id = paturi.split("/")[-1]

				patient_resource = get_resource(client, f"Patient/{id}")

				study_resource = get_study(client, patient_resource)

				study_title = study_resource.get('title')

				if study_title is None:
					study_title = titles[study]

				# There wasn't sufficient time to deal with the conditions so 
				# that is going to be an empty string 
				writer.writerow([
					line.get("docref_uri"),
					tissue_type,
					"",
					study_title,
					patient_resource.get("gender")
				])


