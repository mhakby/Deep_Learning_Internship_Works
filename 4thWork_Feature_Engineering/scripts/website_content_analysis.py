import requests
from bs4 import BeautifulSoup
import csv
import os
import whois
from datetime import datetime

data_directory = '../data'
input_csv_file = os.path.join(data_directory, "bing_search_results200.csv")
output_csv_file = os.path.join(data_directory, "website_content_analysis201.csv")

# Adding New Features
new_headers = ['Word_Count', 'Link_Count', 'Image_Count', 'Video_Count', 'Has_Ads', 'Domain_Age', 'Payment_Present',
               'Login_Present', 'User_Comments', 'Cookies_Present', 'H1_Count', 'H2_Count']

# Combining all headers
headers = ['Language', 'Category', 'URL', 'Title', 'Meta_Description'] + new_headers

# Getting Domain Age
def get_domain_age(url):
    try:
        domain_info = whois.whois(url)
        creation_date = domain_info.creation_date
        if creation_date:
            if isinstance(creation_date, list):
                creation_date = creation_date[0]  # Bazı domainler için birden fazla creation date olabilir
            age = (datetime.now() - creation_date).days // 365
            return age
        else:
            return 'N/A'
    except Exception as e:
        print(f"Error getting domain age for {url}: {e}")
        return 'N/A'

# Checking Payment
def has_payment_system(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = ['pay', 'credit card', 'checkout', 'payment']
        for keyword in keywords:
            if soup.find_all(string=lambda text: keyword in text.lower()):
                return '1'
        return '0'
    except Exception as e:
        print(f"Error checking payment system for {url}: {e}")
        return 'N/A'

# Checking login
def has_login(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('input', {'type': 'password'}):
            return '1'
        keywords = ['login', 'sign in', 'account']
        for keyword in keywords:
            if soup.find_all(string=lambda text: keyword in text.lower()):
                return '1'
        return '0'
    except Exception as e:
        print(f"Error checking login presence for {url}: {e}")
        return 'N/A'

# Checking comments
def has_user_comments(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = ['comments', 'review', 'feedback']
        for keyword in keywords:
            if soup.find_all(string=lambda text: keyword in text.lower()):
                return '1'
        return '0'
    except Exception as e:
        print(f"Error checking user comments for {url}: {e}")
        return 'N/A'

# Checking Cookies
def has_cookies(url):
    try:
        response = requests.get(url, timeout=10)
        if 'set-cookie' in response.headers:
            return '1'
        return '0'
    except Exception as e:
        print(f"Error checking cookies for {url}: {e}")
        return 'N/A'

# Checking Word_Count, Link_Count, Image_Count, Video_Count, Has_Ads, H1/H2_counts
def analyze_website_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Getting content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Word Count
        text = soup.get_text()
        words = text.split()
        word_count = len(words)

        # Link Count
        link_count = len(soup.find_all('a'))

        # Image Count
        image_count = len(soup.find_all('img'))

        # Video Count
        video_count = len(soup.find_all('video'))

        # Has Ads
        has_ads = '1' if soup.find_all(['iframe', 'ins', 'ad']) else '0'

        # H1 and H2 Tag Counts
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))

        return word_count, link_count, image_count, video_count, has_ads, h1_count, h2_count

    except Exception as e:
        print(f"Error analyzing {url}: {e}")
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'


with open(input_csv_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    writer.writerow(headers)

    for row in reader:
        url = row['URL']

        word_count, link_count, image_count, video_count, has_ads, h1_count, h2_count = analyze_website_content(url)
        domain_age = get_domain_age(url)
        payment_present = has_payment_system(url)
        login_present = has_login(url)
        user_comments = has_user_comments(url)
        cookies_present = has_cookies(url)

        new_row = [
            row['Language'], row['Category'], row['URL'],
            row['Title'], row['Meta_Description'], word_count, link_count, image_count,
            video_count, has_ads, domain_age, payment_present, login_present, user_comments,
            cookies_present, h1_count, h2_count
        ]

        writer.writerow(new_row)

print(f"Content analysis has been saved to {output_csv_file}.")
