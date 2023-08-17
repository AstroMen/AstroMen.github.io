import json
import re, requests
from bs4 import BeautifulSoup


def get_app_details_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # App Name
    app_name = soup.find('h1', itemprop="name").span.text.strip()

    # Download Count
    # download_section = soup.find_all('div', string=re.compile(r"(M\+|K\+|B\+)"))
    # download_count = None
    # for section in download_section:
    #     if "M+" in section.text or "K+" in section.text:
    #         download_count = section.text
    #         break

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
    similar_apps = {link.get('href').split('=')[-1]: link.find('span', string=True).text for link in similar_apps_links
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


def get_app_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return get_app_details_from_html(response.text)


if __name__ == "__main__":
    url = "https://play.google.com/store/apps/details?id="
    app_id = 'com.deepl.mobiletranslator'
    app_id = 'com.ebay.mobile'
    app_id = 'com.microsoft.teams'
    app_id = 'org.thoughtcrime.securesms'
    # app_id = 'com.skype.raider'

    app_details = get_app_details(f'{url}{app_id}')
    for key in ['App Name', 'Download Count', 'App Description', 'Rating Score', 'App Categories', 'Developer Name', 'Review Count', 'Similar Apps', 'More App Data']:
        print(f"{key}: {app_details[key]}")
