import requests
import csv
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Bing API info
subscription_key = os.getenv('SUBSCRIPTION_KEY')
search_url = "https://api.bing.microsoft.com/v7.0/search"

# query list
queries = [
        "abortion", "advertising", "advocacy_organizations", "alcohol", "alternative_beliefs",
        "armed_forces", "arts_and_culture", "auction", "brokerage_and_trading", "business",
        "child_abuse", "child_education", "content_servers", "dating", "denied_by_btk",
        "digital_postcards", "discrimination", "domain_parking", "drug_abuse", "dynamic_content",
        "dynamic_dns", "education", "entertainment", "explicit_violence", "file_sharing_and_storage",
        "finance_and_banking", "folklore", "freeware_and_software_downloads", "gambling", "games",
        "general_organizations", "global_religion", "government_and_legal_organizations", "hacking",
        "health_and_wellness", "illegal_or_unethical", "information_and_computer_security",
        "information_technology", "instant_messaging", "internet_radio_and_tv", "internet_telephony",
        "job_search", "lingerie_and_swimsuit", "malicious_websites", "marijuana", "meaningless_content",
        "medicine", "news_and_media", "newsgroups_and_message_boards", "nudity_and_risque",
        "other_adult_materials", "peer_to_peer_file_sharing", "personal_vehicles", "personal_websites_and_blogs",
        "phishing", "plagiarism", "political_organizations", "pornography", "proxy_avoidance", "real_estate",
        "reference", "restaurant_and_dining", "search_engines_and_portals", "secure_websites", "sex_education",
        "shopping", "social_networking", "society_and_lifestyles", "spam_urls", "sports", "sports_hunting_and_war",
        "streaming_media_and_download", "tobacco", "travel", "unrated", "weapons_sales", "web_based_applications",
        "web_based_email", "web_chat", "web_hosting"
    ]

data_directory = '../data'
os.makedirs(data_directory, exist_ok=True)
csv_file = os.path.join(data_directory, "bing_search_results200.csv")

# CSV column values
headers = ['Language', 'Category', 'URL', 'Title', 'Meta_Description']

# Bing Web Search via API
def bing_search(query, subscription_key, search_url, count=50, offset=0):
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML", "count": count, "offset": offset}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()  # Hataları kontrol ediyoruz.
    search_results = response.json()
    return search_results

# Getting lang, meta desc. of the website
def get_website_metadata(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Meta desc bulma
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description_content = meta_description['content'] if meta_description else 'N/A'

        # Dil kodu
        lang = soup.find('html')['lang'] if soup.find('html') and 'lang' in soup.find('html').attrs else 'N/A'

        return lang, description_content

    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return 'N/A', 'N/A'  # Sadece 2 değer döndürüyoruz

# Writing to CSV
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    # Search for each query
    for query in queries:
        print(f"Searching for query: {query}")
        total_results = 0

        # İlk istekte 50 sonuç, diğerlerinde de 50 sonuç olmak üzere toplamda 200 sonuç
        for offset in [0, 50, 100, 150]:
            try:
                results = bing_search(query, subscription_key, search_url, count=50, offset=offset)
                web_pages = results.get("webPages", {}).get("value", [])

                for result in web_pages:
                    url = result.get("url", "No URL")
                    title = result.get("name", "No title")

                    # Getting meta info
                    language_code, meta_description = get_website_metadata(url)

                    writer.writerow([language_code, query, url, title, meta_description])
                    total_results += 1

            except Exception as e:
                print(f"Error fetching results for {query} with offset {offset}: {e}")

        print(f"Total results for '{query}': {total_results}")

print(f"Search results have been saved to {csv_file}.")
