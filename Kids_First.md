# Kids First Portal Registered Tier Data

## Access
To receive access to this dataset, you will need to sign up with Kids First and agree to the terms of use. [Visit the login page](https://portal.kidsfirstdrc.org/login), and click sign up. You will need either a Google Account, an ORCID, or NIH RAS (eg, eRA Commons) as your authentication method. [Here are instructions to create a Google Account](https://support.google.com/accounts/answer/27441?hl=en)- it can also be used for AnVIL on Terra.

 ![Kids First login page with sign up highlighted](img/kids_first_sign_up.png)

## Data Resources

### Portal
The [Kids First DRC Portal](https://portal.kidsfirstdrc.org/) UI may provide insight into the FHIR Resources and other data available.

### Data Source
The Kids First platform has data from many studies available. Most clinical data is accesible to registered users, and most genomic data require additional authorization, eg, through a dbGaP request. [The Kids First Neuroblastoma Study](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001436.v1.p1) has open access clinical data and gene expression results, one example of the data we can use for this event.

### FHIR Service
API Requests can be made against the FHIR Base URL: https://kf-api-fhir-service.kidsfirstdrc.org/ 

### DRS Service
The file data in across INCLUDE is indexed via the Kids First DRS server (an instance of Gen3). It is typically hosted in AWS s3 buckets.

## Authentication
Once you have registered, you can access the FHIR services using cookie-based authentication.

### Within the browser
Your browser will manage the cookie to enable access transparently to you the user. You will need to login one time, then you will be able to make HTTP REST requests via the browser. Once the cookie expires or you log out, you'll need to log in again.

### Supplying the cookie for programmatic requests
To access the FHIR services via programmtic requests, eg using `curl`, you will need to pass along a cookie. Some methods to retrieve this cookie:
1. Visit the [FHIR Service](https://kf-api-fhir-service.kidsfirstdrc.org/) in your browser.
2. Login, if you have not already.
3. Using browser-specific tools, view cookies. 
- For Chrome, you can visit this [settings URI](chrome://settings/cookies/detail?site=kf-api-fhir-service.kidsfirstdrc.org) to view the specific cookies for the INCLUDE FHIR Service.
- While at the FHIR Service URL, you can also use the Chrome developer tools -> Application -> Storage -> Cookies.
- For Firefox, they can be found in the [Storage Inspector](https://firefox-source-docs.mozilla.org/devtools-user/storage_inspector/index.html).
4. Find `AWSELBAuthSessionCookie-0`, and copy the ENTIRE value. 
5. Configure your tool to use this cookie.
- The cookie's "key" is `AWSELBAuthSessionCookie-0` and the cookie's "value" is what you recorded previously.
- If your HTTP tool has a cookie specific option, you can add this key-value pair to the cookie list. EG:
- For `curl`, you can use `curl --cookie "AWSELBAuthSessionCookie-0=<your cookie here>"`
- If your HTTP tool does not have a cookie specific option, you'll need to add it to the headers, a la `header = { "Cookie": "AWSELBAuthSessionCookie-0=<the value you copied>" }`.
- For `curl`, you can use `curl --cookie "AWSELBAuthSessionCookie-0=<your cookie here>"
- This is demonstrated in the [configuration](config/kidsfirst.sh) and [test](tests/kidsfirst_test.sh) bash scripts.
