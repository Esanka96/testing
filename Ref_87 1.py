import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
import cloudscraper

base_url = "https://www.scielo.br/j/ramb/grid"
retry_attempts = 50
retry_delay = 5
errors = []

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "Sec-Ch-Ua-Arch": "\"x86\"",
    "Sec-Ch-Ua-Bitness": "\"64\"",
    "Sec-Ch-Ua-Full-Version": "\"126.0.6478.127\"",
    "Sec-Ch-Ua-Full-Version-List": "\"Not/A)Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"126.0.6478.127\", \"Google Chrome\";v=\"126.0.6478.127\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Model": "\"\"",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Ch-Ua-Platform-Version": "\"15.0.0\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}
cookies = {"language": "en"}

scraper = cloudscraper.create_scraper()


def url_check(link, headers, cookies):
    for attempt in range(retry_attempts):
        try:
            response = scraper.get(link, headers=headers, cookies=cookies, timeout=180)
            response.encoding = "utf-8"
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retry_attempts - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                errors.append(f"Failed to retrieve the page after {retry_attempts} attempts: {e}")
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
        soup_response = url_check(base_url, headers=headers, cookies=cookies)
        if not soup_response:
            time.sleep(delay)
            continue

        soup = BeautifulSoup(soup_response.content, "html.parser")
        latest_issue_link = get_latest_issue_link(soup, base_url)
        if latest_issue_link:
            return latest_issue_link

        time.sleep(delay)
    return None

latest_issue_link = fetch_latest_issue(base_url)

if latest_issue_link:
    print(f"✅ Latest issue link: {latest_issue_link}")
    latest_issue_response = url_check(latest_issue_link, headers=headers, cookies=cookies)
    latest_issue_link_soup = BeautifulSoup(latest_issue_response.content, "html.parser")

    if latest_issue_link_soup:
        issue_div_ = latest_issue_link_soup.find("div", {"id": "issueIndex", "class": "col content issueIndex"})

        if issue_div_:
            strong_text = issue_div_.find("strong").get_text(strip=True)
            match = re.search(r"Volume:\s*(\d+),\s*Issue:\s*(\d+),\s*Published:\s*(\d{4})", strong_text)
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
                    article_url = urljoin(latest_issue_link,article_url_inc) if article_url_inc else None

                    article_url_response = url_check(article_url, headers=headers, cookies=cookies) if article_url else None
                    article_url_soup = BeautifulSoup(article_url_response.content, "html.parser") if article_url_response else None
                    div = article_url_soup.find("div", class_="articleBadge-editionMeta-doi-copyLink") if article_url_soup else None
                    doi_tag = div.find("a", class_="_doi") if div else None

                    doi = None
                    if doi_tag and doi_tag.get("href"):
                        doi = doi_tag["href"].replace("https://doi.org/", "").strip()

                    pdf_url_inc = links[1].find("a")["href"] if len(links) > 1 and links[1].find("a") else None
                    pdf_url = urljoin(latest_issue_link,pdf_url_inc) if pdf_url_inc else None

                    if title or article_url or pdf_url:
                        print("Title:", title)
                        print("Article URL:", article_url)
                        print("Doi", doi)
                        print("PDF URL:", pdf_url)
                        print("Volume:", volume)
                        print("Issue:", issue)
                        print("Year:", year)
                        print("-" * 80)

else:
    print("❌ Failed to fetch latest issue link after retries")
    if errors:
        print("Errors:", errors)


