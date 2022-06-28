#!/usr/bin/env python

from wstlr.hostfile import load_hosts_file
from collections import defaultdict

from ncpi_fhir_client.fhir_client import FhirClient

from pathlib import Path
import json

import csv
import sys
from argparse import ArgumentParser, FileType

import pdb

class FhirDoc:
    def __init__(self, resource, title, url):
        self.title = title
        self.url = url
        self.subject = None
        self.subject_ref = resource['subject']['reference']
        self.specimen_ref = []
        self.study_tag = resource['meta']['tag'][0]['code']
        self.sex = ""
        
        if 'context' in resource:
            self.specimen_ref = self.get_specimen_ref(resource.get("context"))

    def get_specimen_ref(self, context):
        specimen = []

        for entry in context['related']:
            specimen.append(entry['reference'])
        return specimen

    def get_tissue_display(self, client, ref):
        response = client.get(ref)
        if response.success():
            if 'parent' in response.entries[0]:
                return self.get_tissue_display(client, response.entries[0]['parent']['reference'])
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
            "filename",
            "url",
            "tissue_type",
            "condition-disease",
            "study_name",
            "patient_sex"
        ])

    def write_row(self, writer):
        writer.writerow([
            tag,
            self.title,
            self.url,
            self.tissue_list,
            "TBD",
            self.study_tag,
            self.sex
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
    "qa-kf-inc": ["HTP", "DS-COG-ALL", "DS-PCGC", "DS360-CHD"],
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
                        doc = FhirDoc(resource, title, url)
                        docrefs.append(doc)

            #pdb.set_trace()
            for doc in docrefs:
                doc.load_other_resources(fhir_client)
                doc.write_row(writer)
