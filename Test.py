import time
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import random
#comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://www.scielo.br/j/ramb/grid"
retry_attempts = 50
retry_delay = 5
errors = ["No erros"]

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "referer": "https://www.scielo.br/"
}

cookies = {"language": "en"}

chrome_options = Options()
# chrome_options.add_argument("--headless=new")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(), options=chrome_options)

def url_check(link, headers, cookies):
    for attempt in range(retry_attempts):
        try:
            driver.get(link)

            for k, v in cookies.items():
                try:
                    driver.add_cookie({"name": k, "value": v})
                except Exception:
                    pass

            driver.refresh()  

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            html = driver.page_source
            return html
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retry_attempts - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                errors.append(f"Failed after {retry_attempts} attempts: {e}")
                raise
    return None


def get_latest_issue_link(soup, base_url):
    issue_list_div = soup.find("div", {"id": "issueList", "class": "col content issueList"})
    if not issue_list_div:
        return None

    first_row = issue_list_div.find("tbody").find("tr")
    if not first_row:
        return None

    issue_links = first_row.find_all("a", class_="btn")
    if not issue_links:
        return None

    numeric_links = [a for a in issue_links if a.get_text(strip=True).isdigit()]
    if not numeric_links:
        return None

    return urljoin(base_url, numeric_links[-1]["href"])


def fetch_latest_issue(base_url, retries=20, delay=7):
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt} to fetch latest issue...")
        html = url_check(base_url, headers=headers, cookies=cookies)
        if not html:
            time.sleep(delay)
            continue

        soup = BeautifulSoup(html, "html.parser")
        latest_issue_link = get_latest_issue_link(soup, base_url)
        if latest_issue_link:
            return latest_issue_link

        time.sleep(delay)
    return None


latest_issue_link = fetch_latest_issue(base_url)

if latest_issue_link:
    print(f"✅ Latest issue link: {latest_issue_link}")
    latest_issue_html = url_check(latest_issue_link, headers=headers, cookies=cookies)
    latest_issue_link_soup = BeautifulSoup(latest_issue_html, "html.parser")

    if latest_issue_link_soup:
        issue_div_ = latest_issue_link_soup.find("div", {"id": "issueIndex", "class": "col content issueIndex"})

        if issue_div_:
            strong_text = issue_div_.find("strong").get_text(strip=True)
            match = re.search(r"Volume:\s*(\d+),\s*Número:\s*(\d+),\s*Publicado:\s*(\d{4})", strong_text)
            if match:
                volume, issue, year = match.groups()
            else:
                volume = issue = year = None

            issue_divs = issue_div_.find_all("div", class_="issueIndent")

            article_div = None
            for div in issue_divs:
                if div.find("table"):
                    article_div = div
                    break

            if article_div:
                all_rows = article_div.find_all("tr")

                for row in all_rows:

                    title_tag = row.find("strong", class_="d-block mt-2")
                    title = title_tag.get_text(strip=True) if title_tag else None

                    links = row.find_all("li", class_="nav-item me-4")

                    article_url_inc = links[0].find("a")["href"] if len(links) > 0 and links[0].find("a") else None
                    article_url = urljoin(latest_issue_link, article_url_inc) if article_url_inc else None

                    article_html = url_check(article_url, headers=headers, cookies=cookies) if article_url else None
                    article_url_soup = BeautifulSoup(article_html, "html.parser") if article_html else None
                    div = article_url_soup.find("div", class_="articleBadge-editionMeta-doi-copyLink") if article_url_soup else None
                    doi_tag = div.find("a", class_="_doi") if div else None

                    doi = None
                    if doi_tag and doi_tag.get("href"):
                        doi = doi_tag["href"].replace("https://doi.org/", "").strip()

                    pdf_url_inc = links[1].find("a")["href"] if len(links) > 1 and links[1].find("a") else None
                    pdf_url = urljoin(latest_issue_link, pdf_url_inc) if pdf_url_inc else None

                    if title or article_url or pdf_url:
                        print("Title:", title)
                        print("Article URL:", article_url)
                        print("Doi", doi)
                        print("PDF URL:", pdf_url)
                        print("Volume:", volume)
                        print("Issue:", issue)
                        print("Year:", year)
                        print("-" * 80)
                    time.sleep(random.randint(5, 8))

else:
    print("❌ Failed to fetch latest issue link after retries")
    if errors:
        print("Errors:", errors)


driver.quit()
