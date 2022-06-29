#!/usr/bin/env python

from wstlr.hostfile import load_hosts_file
from collections import defaultdict

from ncpi_fhir_client.fhir_client import FhirClient

from pathlib import Path
import json

import csv
import sys
from argparse import ArgumentParser, FileType

from collections import defaultdict

import pdb

class Patient:
    # client => {id => Patient }
    _cache = defaultdict(dict)

    def __init__(self, client, resource):
        self.id = resource['id']
        self.client = client
        self.identifier = resource['identifier'][0]['value']
        self.sex = resource['gender']
        self.resource = resource

    @classmethod
    def get_resource(cls, client, ref):
        id = ref.split("/")[-1]
        if id in Patient._cache[client]:
            return Patient._cache[client][id]
        else:
            response = client.get(ref)
            if response.success():
                assert(len(response.entries) == 1)

                resource = response.entries[0]
                Patient._cache[client][id] = Patient(client, resource)

class Specimen:
    # client => {id => Specimen }
    _cache = defaultdict(dict)

    def __init__(self, client, resource):
        self.id = resource['id']
        self.client = client
        self.identifier = resource['identifier'][0]['value']
        self.resource = resource

    @classmethod
    def get_resource(cls, client, ref):
        id = ref.split("/")[-1]
        if id in Specimen._cache[client]:
            return Specimen._cache[client][id]
        else:
            response = client.get(ref)
            if response.success():
                assert(len(response.entries) == 1)

                resource = response.entries[0]
                Specimen._cache[client][id] = Specimen(client, resource)

class FhirDoc:
    def __init__(self, fhir_endpoint, resource, title, url):
        self.title = title
        self.url = url
        self.id = resource['id']
        self.subject = None
        self.endpoint = fhir_endpoint
        self.subject_ref = resource['subject']['reference']
        self.specimen_ref = []
        self.study_tag = resource['meta']['tag'][0]['code']
        self.sex = ""
        self.study_ref = ""
        self.study_title = ""
        self.study_id = ""
        
        if 'context' in resource:
            self.specimen_ref = self.get_specimen_ref(resource.get("context"))

    def get_study_details(self, client):
        response = client.get("ResearchStudy?identifier={self.study_tag}")
        if response.success():
            resource = response.entries[0]['resource']
            self.study_title = resource['title']
            self.study_id = resource['id']

            self.study_ref = f"ResearchStudy/{self.study_id}"

    @property
    def document_reference_full_url(self):
        return f"{self.endpoint}/DocumentReference/{self.id}"

    @property
    def patient_reference_full_url(self):
        return f"{self.endpoint}/{self.subject_ref}"

    @property
    def study_reference_full_url(self):
        return f"{self.endpoint}/{self.study_ref}"
    
    @property
    def specimen_reference_full_url(self):
        specimens = []
        for specref in self.specimen_ref:
            specimens.append(f"{self.endpoint}/{specref}")

        if len(specimens) > 1:
            print(f"We found {len(specimens)} specimens for this one")
        return ":".join(specimens)
        

    def get_specimen_ref(self, context):
        specimen = []

        for entry in context['related']:
            specimen.append(entry['reference'])
        return specimen

    def get_tissue_display(self, client, ref):
        response = client.get(ref)
        if response.success():
            if 'parent' in response.entries[0]:
                #pdb.set_trace()
                # Is it safe to assume only one parent? For now, yes, but later that may not be true
                return self.get_tissue_display(client, response.entries[0]['parent'][0]['reference'])
            else:
                return response.entries[0]['type']['coding'][0]['display']

    def collect_tissue_types(self, client):
        tissues = set()

        for specref in self.specimen_ref:
            tissues.add(self.get_tissue_display(client, specref))

        self.tissue_list = ", ".join(sorted(list(tissues)))

    def get_patient(self, client):
        response = client.get(self.subject_ref)
        if response.success():
            assert(len(response.entries) == 1)
            self.collect_demographics(response.entries[0])
            # self.full_urls['subject'] = response.entries[0]['fullUrl']
            #self.raw['subject'] = response.entries[0]


    def collect_demographics(self, resource):
        if 'gender' in resource:
            self.sex = resource['gender']

    def load_other_resources(self, client):
        self.get_patient(client)
        self.collect_tissue_types(client)

    @classmethod
    def print_header(self, writer):
        writer.writerow([
            "document_reference_attachment_uri",
            "drs_uri",
            "document_reference_reference",
            "file_path",
            "specimen_bodySite",
            "condition_code",
            "research_study_reference",
            "patient_reference",
            "specimen_reference",
            "study_name",
            "filename",
            "study_id",
            "patient_sex",
            "disease_status"
        ])

    def write_row(self, writer):
        drs_id = ""
        if self.url.split(":")[0] == "drs":
            drs_id = self.url
        writer.writerow([
            self.url,
            drs_id,
            self.docref_url,
            "",
            self.tissue_list,
            "TBD",
            self.study_url,
            self.specimen_url,
            self.study_name,
            self.study_tag,
            self.sex,
            self.disease_status,
            "TBD"
        ])

host_config = load_hosts_file("fhir_hosts")
# Just capture the available environments to let the user
# make the selection at runtime
env_options = sorted(host_config.keys())

parser = ArgumentParser(description="Pull data from the specified FHIR server")
parser.add_argument(
    "-e",
    "--env",
    choices=env_options,
    required=True,
    help=f"Remote configuration to be used to access the FHIR server. If no environment is provided, the system will stop after generating the whistle output (no validation, no loading)",
)

args = parser.parse_args(sys.argv[1:])

# First, pull the document references using the base query: 
# DocumentReference?type=Gene-Expression,Gene-Expression-Quantifications&category=https://includedcc.org/fhir/code-systems/experimental_strategies|RNA-Seq&location:missing=false
# I think this should work for all of the different fhir servers and datasets

study_tags = {
    "fhir-cat": ["GTEx"],
    "prod-kf-inc": ["HTP", "DS-COG-ALL", "DS-PCGC", "DS360-CHD"],
    "kf-fhir": [        
        "SD_ZXJFFMEF",
        "SD_46SK55A3",
        "SD_PET7Q6F2",
        "SD_46RR9ZR6",
        "SD_Z6MWD3H0",
        "SD_P445ACHV",
        "SD_8Y99QZJJ",
        "SD_6FPYJQBR",
        "SD_YGVA0E1C",
        "SD_DZTB5HRR",
        "SD_BHJXBDQK",
        "SD_VTTSHWV4",
        "SD_DYPMEHHF",
        "SD_0TYVY1TW",
        "SD_ZFGDG5YS",
        "SD_DZ4GPQX6",
        "SD_RM8AFW0R",
        "SD_R0EPRSGS",
        "SD_W0V965XZ",
        "SD_YNSSAPHE",
        "SD_JWS3V24D",
        "SD_PREASA7S",
        "SD_NMVV8A1Y",
        "SD_DK0KRWK8",
        "SD_B8X3C1MX",
        "SD_7NQ9151J",
        "SD_9PYZAHHE",
        "SD_1P41Z782",
        "SD_HGHFVPFD",]
}

outdir = Path("output")
outdir.mkdir(parents=True, exist_ok=True)
fhir_client = FhirClient(host_config[args.env])

documents = []

_valid_filetypes = ['rsem.genes.results.gz', 'tpm.tsv.gz']
def valid_filetype(title):
    for vft in _valid_filetypes:
        if vft in title:
            return True
    return False

output_filename = f"{outdir}/{args.env}-fhircat.csv"
with open(output_filename, 'wt') as outf:
    writer = csv.writer(outf, delimiter=',', quotechar='"')
    FhirDoc.print_header(writer)
    for tag in study_tags[args.env]:
        if args.env == "fhir-cat":
            qry = f"DocumentReference?_tag={tag}&category=https://includedcc.org/fhir/code-systems/experimental_strategies|RNA-Seq&location:missing=false"
        else:
            qry = f"DocumentReference?_tag={tag}&type=Gene-Expression,Gene-Expression-Quantifications&category=https://includedcc.org/fhir/code-systems/experimental_strategies|RNA-Seq&location:missing=false"
        docrefs = []
        result = fhir_client.get(qry)
        #pdb.set_trace()
        if result.success():
            for entry in result.entries:
                resource = entry['resource']
                    
                #pdb.set_trace()
                for content_entry in resource['content']:
                    attachment = content_entry['attachment']
                    title = attachment['title']
                    url = attachment['url']

                    if valid_filetype(title):
                        doc = FhirDoc(fhir_client.target_service_url, resource, title, url)
                        docrefs.append(doc)

            #pdb.set_trace()
            for doc in docrefs:
                doc.load_other_resources(fhir_client)
                doc.write_row(writer)
