import requests
import pandas as pd

def query_fhir_include(include_cookie, query_statement="https://include-api-fhir-service.includedcc.org/DocumentReference?_tag=HTP&category=RNA-Seq&type=Gene-Expression,Gene-Expression-Quantifications&location:missing=false"):
    

    req = requests.get(query_statement, cookies = {"AWSELBAuthSessionCookie-0" : include_cookie})
    req_j = req.json()
    FHIR_SERVER_ROOT =  "https://" + query_statement.split("//")[1].split('/')[0]
    data = []
    for entry in req_j['entry']:
        item = {}
        item["document_reference_attachement_uri"] = entry['resource']['content'][0]['attachment']['url']
        item['drs_uri'] = entry['resource']['content'][0]['attachment']['url']
        item['document_reference_reference'] = entry['fullUrl']
        item['file_path'] = ""
        item['specimen_bodySite'] = ""
        item['condition_code'] =  entry["resource"]['meta']['tag'][0]['code']
        item['filename'] = entry['resource']['content'][0]['attachment']['title']
        item['research_study_reference'] = entry["resource"]['meta']['tag'][0]['code']
        item['patience_reference'] = FHIR_SERVER_ROOT + "/" + entry["resource"]['subject']['reference']
        item['specimen_reference'] = FHIR_SERVER_ROOT + "/" + entry["resource"]['context']['related'][0]['reference']
        data.append(item)
    df = pd.DataFrame(data)
    df.set_index("document_reference_attachement_uri", inplace=True)
    return df

