import cloudscraper
from bs4 import BeautifulSoup
import re
import os

out_path='Out'
if not os.path.exists(out_path):
    os.makedirs(out_path)
out_folder=os.path.join(out_path,'New.pdf')

scraper = cloudscraper.create_scraper()

def new_function(firstUrl):
    headers1 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "Sec-Ch-Ua-Arch": '"x86"',
        "Sec-Ch-Ua-Bitness": '"64"',
        "Sec-Ch-Ua-Full-Version": '"134.0.6998.89"',
        "Sec-Ch-Ua-Full-Version-List": '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Model": '""',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Ch-Ua-Platform-Version": '"15.0.0"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }


    response = scraper.get(firstUrl, headers=headers1)
    print(BeautifulSoup(response.content, 'html.parser'))



new_function("https://legiscan.com/OR/text/SB546/id/2771979")

# response=scraper.get("https://jdmlm.ub.ac.id/index.php/jdmlm/issue/archive",headers=headers1)
# soup = BeautifulSoup(response.content, 'html.parser')
# print(soup)


# pdf_link="https://journals.physiology.org/doi/pdf/10.1152/ajpcell.00289.2024?download=true"
# pdf_content = scraper.get(pdf_link,headers=headers3).content
# with open(out_folder, 'wb') as file:
#     file.write(pdf_content)


