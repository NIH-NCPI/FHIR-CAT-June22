# AnVIL GTEx Open Access Data

For this event, we have generated a Google Healthcare API FHIR Datastore from Open Access GTEx data. The Resources present focus around the individuals, their samples, the assays, and the resulting Gene TPM files. FHIR services are not generally available for the AnVIL at this time, and this datastore will only be up for a limited time. 

## Data Resources
There are two primary data resources:
- Google Healthcare API FHIR datastore
- Google Cloud Storage containing the assay results
Authentication is linked to your Terra-linked Google account, with details to gain access below.

### Data Source
All data is Open Access, sourced from the [GTEx Portal](https://gtexportal.org/home/datasets). We are using the GTEx Analysis V8 set.

### FHIR Datastore
API Requests can be made against the FHIR Base URL: https://healthcare.googleapis.com/v1/projects/ncpi-fhir-cat-2022/locations/us-central1/datasets/GTEx_Open_Access/fhirStores/gtex_v8/fhir 
The web cloud console interface, which allows some viewing of resources, can be found here: https://console.cloud.google.com/healthcare/fhirviewer/us-central1/GTEx_Open_Access/fhirStores/gtex_v8/browse?authuser=0&project=ncpi-fhir-cat-2022 

Note that some project configured commands, eg `gcloud healthcare fhir-stores list`, won't work unless you specify another project as the Terra workspace project does not have the healthcare API enabled. You can use the `ncpi-fhir-cat-2022` project, eg with the `--project` flag, to perform queries in these cases.

### AnVIL Workspace on Terra
Participants in this Code-a-thon will have access [provided to this workspace](https://anvil.terra.bio/#workspaces/ncpi-fhir-2022/NCPI%20FHIR%20CAT%202022-%20GTeX%20Public%20Data). The workspace bucket contains the Gene TPM data.

#### GCS Bucket
The cloud storage uri is: gs://fc-a2df0708-c407-468e-a93f-00a42640ee56
The web cloud console interface, which allows some browsing, can be found here: https://console.cloud.google.com/storage/browser/fc-a2df0708-c407-468e-a93f-00a42640ee56;tab=objects?authuser=0&prefix=&forceOnObjectsSortingFiltering=false

## Access
To receive access to this dataset, please reach out to Robert Carroll leading up to or during the event. Access is controlled via the [NCPI-FHIR-CAT-2022 group](https://anvil.terra.bio/#groups/NCPI-FHIR-CAT-2022) managed within Terra. This will enable access to both the bucket and the FHIR Service. If you have not used Terra before, you will need to [login with an existing Google Account](https://anvil.terra.bio/). If you do not have one, [you will need to create one](https://support.google.com/accounts/answer/27441?hl=en).

## Authentication
Once you have received permissions, you can access the data in either of the following ways.

### Terra Pet Service account
Terra creates pet service accounts for each user that are given permissions to the resources shared with you in Terra or shared with Terra groups or Terra identity proxies. [See here for more details.](https://support.terra.bio/hc/en-us/articles/360031023592-Pet-service-accounts-and-proxy-groups-)

When using the provided workspace images in Terra, one is able to easily generate a Bearer token for use in API calls:
`gcloud auth print-access-token`
Note that you can also use `gcloud auth list` and then specify the service account instead of relying on the default behavior.

[Details on `list`](https://cloud.google.com/sdk/gcloud/reference/auth/list)
[Details on `print-access-token`](https://cloud.google.com/sdk/gcloud/reference/auth/print-access-token)

### User Account OAuth
You can use a standard OAuth flow to generate a Bearer token that can be sent with your requests. 

[Per this page](https://developers.google.com/identity/protocols/oauth2/scopes#healthcare), the scope `https://www.googleapis.com/auth/cloud-platform` is required. **Note that this is a broad scope and care should be taken.** These tokens will allow access to any Google Cloud resources you have access to, as compared to the service account approach with is limited to what you can access managed by Terra.

Some References:
- [Google OAuth2 playground, which allows you to get Bearer Tokens in a UI](https://developers.google.com/oauthplayground/)
- [Google on using Oauth for desktop apps and APIs](https://developers.google.com/identity/protocols/oauth2/native-app)
