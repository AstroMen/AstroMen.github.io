import re, requests
from bs4 import BeautifulSoup


def get_app_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # App Name
    app_name = soup.find('h1', itemprop="name").span.text.strip()

    # Download Count
    download_section = soup.find_all('div')
    download_count = None
    for section in download_section:
        if "M+" in section.text or "K+" in section.text:
            download_count = section.text
            break

    # App Description
    app_description = soup.find('div', {'data-g-id': "description"}).text.strip()

    # Extracting the rating score using a more robust method:
    rating_div = soup.find('div', {'aria-label': re.compile(r"Rated")})
    if rating_div:
        potential_rating = rating_div.find_previous('div')
        if potential_rating:
            rating_score = potential_rating.get_text(strip=True)
        else:
            rating_score = "Not found"
    else:
        rating_score = "Not found"

    # Extracting similar apps names and IDs:
    similar_apps_links = soup.select('a[href*="/store/apps/details?"]')
    # Parsing the similar apps' IDs from the href attributes
    similar_apps_ids = [link.get('href').split('=')[-1] for link in similar_apps_links]
    similar_apps_names = [link.find('span', string=True).text for link in similar_apps_links if
                          link.find('span', string=True)]

    # Creating the dictionary of similar apps using app IDs as keys and app names as values:
    similar_apps_dict = dict(zip(similar_apps_ids, similar_apps_names))

    return {
        'App Name': app_name,
        'Download Count': download_count,
        'App Description': app_description,
        'Rating Score': rating_score,
        'Similar Apps': similar_apps_dict
    }


url = "https://play.google.com/store/apps/details?id=com.deepl.mobiletranslator"
url = "https://play.google.com/store/apps/details?id=com.ebay.mobile"
app_details = get_app_details(url)
print(app_details)
