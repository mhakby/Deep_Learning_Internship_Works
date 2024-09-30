import csv
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SERPAPI_KEY')


def search_google(query, num_results=10):
    params = {
        "q": query,
        "num": num_results,
        "engine": "google",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get('organic_results', [])


def save_to_csv(results, query, file_name="results.csv"):
    fields = ['link', 'title', 'snippet', 'query']

    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()  # Her zaman baþlýklarý yaz

        for result in results:
            link = result.get('link')
            title = result.get('title')
            snippet = result.get('snippet')

            # Sonuçlarý yaz
            writer.writerow({
                'link': link,
                'title': title,
                'snippet': snippet,
                'query': query
            })


if __name__ == "__main__":
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

    for query in queries:
        print(f"Searching for: {query}")
        search_results = search_google(query)
        save_to_csv(search_results, query)
        print(f"{len(search_results)} results for '{query}' saved to CSV.")
