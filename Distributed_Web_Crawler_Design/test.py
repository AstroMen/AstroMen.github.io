import requests
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

    # Rating Score
    rating_score = soup.find('div', class_="jILTFe").div.text.strip()

    # Similar Apps Names
    similar_apps_section = soup.find('section', jscontroller="NkbkFd")
    similar_apps_names = [app.span.text.strip() for app in similar_apps_section.find_all('span', class_="DdYX5")]

    return {
        'App Name': app_name,
        'Download Count': download_count,
        'App Description': app_description,
        'Rating Score': rating_score,
        'Similar Apps Names': similar_apps_names
    }

url = "https://play.google.com/store/apps/details?id=com.deepl.mobiletranslator"
app_details = get_app_details(url)
print(app_details)
