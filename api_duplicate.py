import re
import requests
from bs4 import BeautifulSoup
import json

def check_duplicate(doi,art_title,src_id,vol_no,iss_no):
    url = 'https://ism-portal.innodata.com/api/validate-record'

    data = {'token': '6547bdf3f07202413b5daf3216e511028c14034b36ff47c514c0220a911785b3:1698740839',
            'doi': doi, 'art_title': art_title, 'srcid': src_id, 'volume_no': vol_no, 'issue_no': iss_no}

    responseData=json.loads(BeautifulSoup(requests.post(url, data=data).content, 'html.parser').text)
    print(responseData)

    duplicateCheckValue=responseData.get("status",{})
    tpa_id=responseData.get("tpa_id",{})

    if not duplicateCheckValue:
        return True,tpa_id
    else:
        return False,tpa_id

DOI=""
Article_title="Editor's Notes"
url_id="808068920"
Volume="21"
Issue=""

# DOI="10.18280/ria.380201"
# Article_title="Design of an AI Layer for Real-Time Skin Cancer Diagnosis"
# url_id="77669799"
# Volume="38"
# Issue="2"

check_value,tpa_id = check_duplicate(DOI, Article_title, url_id, Volume, Issue)
