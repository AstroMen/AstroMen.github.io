import json
import logging
import time
import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class URLFetcher:
    MAX_RETRIES = 3  # Max retries before giving up

    def __init__(self, user_agent_list, proxy_manager):
        self.user_agent_list = user_agent_list
        # self.proxy_pool = proxy_pool
        self.proxy_manager = proxy_manager
        self.base_url = 'https://play.google.com/store/apps/details?id={}'

    def fetch_with_retry(self, url, retry_count=0):
        if retry_count >= self.MAX_RETRIES:
            logging.error(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts.")
            return None

        # Randomly select a User-Agent
        user_agent = random.choice(self.user_agent_list)
        # Fetch web page using randomly selected User-Agent and proxy
        proxy = self.proxy_manager.get_proxy()
        # proxy = random.choice(self.proxy_pool)
        if not proxy:
            logging.error("No valid proxies available!")
            return None

        try:
            # return self.fetch_single_url(url)
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers={'User-Agent': user_agent})
            response.raise_for_status()  # This will raise an HTTPError for 4xx and 5xx status codes
            self.proxy_manager.report_proxy_success(proxy)
        except (requests.ConnectionError, requests.Timeout):
            self.proxy_manager.report_proxy_failure(proxy)
            # ... handle the error, maybe retry with another proxy
            logging.warning(f"Proxy {proxy} failed or request timed out for URL {url}.")
            if retry_count < self.MAX_RETRIES:
                logging.info(f"Retrying with a different proxy...")
                return self.fetch_with_retry(url, retry_count + 1)
            else:
                logging.error(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts.")
                return None
        except requests.HTTPError as e:
            if e.response.status_code in [403, 503]:  # proxy-related
                self.proxy_manager.report_proxy_failure(proxy)
            if e.response.status_code == 429:  # Too Many Requests
                logging.warning("Rate limited by the server. Waiting for a while before retrying...")
                time.sleep(2 ** (retry_count + 1))  # Exponential backoff
                return self.fetch_with_retry(url, retry_count + 1)
            else:
                logging.error(f"Failed to fetch the URL {url} with HTTP error: {e}")
                return None

        data = self.get_app_details(response.text)
        # Serialize similar_apps_info into a JSON string
        data['similar_apps_info'] = json.dumps(data['similar_apps_info'])

        # Add a random delay between requests to avoid being banned for rapid requests
        time.sleep(random.uniform(0.5, 1.5))
        return data

    def fetch(self, max_threads=10):
        new_urls = []
        with open('ids.txt', 'r') as f:
            for line in f:
                new_urls.append(self.base_url.format(line.strip()))

        # 使用线程池来并发爬取
        with ThreadPoolExecutor(max_threads) as executor:
            results = list(executor.map(self.fetch_with_retry, new_urls))

        return results

    @staticmethod
    def get_app_details(html_content):
        # Extract app details from the webpage content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # App Name
        app_name = soup.find('h1', itemprop="name").span.text.strip()

        # Download Count
        download_div = soup.find('div', string='Downloads')
        if download_div:
            # Finding the parent div
            parent_div = download_div.find_parent()
            if parent_div:
                # Extracting the nested div's text (i.e., "1B+")
                download_count = parent_div.find('div').text
            else:
                download_count = "Not found"
        else:
            download_count = "Not found"

        # App Description
        app_description = soup.find('div', {'data-g-id': "description"}).text.strip()

        # Rating Score (Modified as per requirement)
        rating_div = soup.find('div', itemprop="starRating")
        if rating_div:
            rating_score = rating_div.text.strip()
        else:
            rating_score = "Not found"

        # Extracting similar apps names and IDs:
        similar_apps_links = soup.select('a[href*="/store/apps/details?"]')
        similar_apps = {link.get('href').split('=')[-1]: link.find('span', string=True).text for link in
                        similar_apps_links
                        if link.find('span', string=True)}

        # Extracting App Category
        app_categories_links = soup.select('a[aria-label][href*="/store/apps/category/"]')
        app_categories = [link.get('aria-label') for link in app_categories_links]

        # Extracting Developer Name
        developer_div = soup.find('div', class_='Vbfug auoIOc')
        developer_name = developer_div.find('span').text if developer_div else "Not found"

        # Extracting Review Count
        review_count_div = soup.find('div', class_='g1rdde')
        review_count = review_count_div.text.strip() if review_count_div else "Not found"

        # Extract the relevant script tag
        script_tags = soup.find_all('script', type="application/ld+json")
        relevant_script_content = None
        for script in script_tags:
            json_data = json.loads(script.string)
            if json_data.get("@type") == "SoftwareApplication" and json_data.get("name") == app_name:
                relevant_script_content = json_data
                break
        # Extract the necessary details from the relevant script content
        if relevant_script_content:
            extracted_data = {
                "name": relevant_script_content.get("name", "N/A"),
                "url": relevant_script_content.get("url", "N/A"),
                "description": relevant_script_content.get("description", "N/A"),
                "operatingSystem": relevant_script_content.get("operatingSystem", "N/A"),
                "applicationCategory": relevant_script_content.get("applicationCategory", "N/A"),
                "contentRating": relevant_script_content.get("contentRating", "N/A"),
                "author": relevant_script_content.get("author", {}).get("name", "N/A"),
                "ratingValue": relevant_script_content.get("aggregateRating", {}).get("ratingValue", "N/A"),
                "ratingCount": relevant_script_content.get("aggregateRating", {}).get("ratingCount", "N/A"),
                "price": relevant_script_content.get("offers", [{}])[0].get("price", "N/A"),
                "priceCurrency": relevant_script_content.get("offers", [{}])[0].get("priceCurrency", "N/A"),
            }
        else:
            extracted_data = {}

        return {
            'App Name': app_name,
            'Download Count': download_count,
            'App Description': app_description,
            'Rating Score': rating_score,
            'Similar Apps': similar_apps,
            'App Categories': app_categories,
            'Developer Name': developer_name,
            'Review Count': review_count,
            'More App Data': extracted_data,
        }
