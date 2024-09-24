import requests
from bs4 import BeautifulSoup
import csv
import os
import whois
from datetime import datetime
import concurrent.futures
import time
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(f"website_content_analysis")
logger.setLevel(logging.INFO)

# Log dosyası oluşturma
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(base_dir, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file = os.path.join(logs_dir, f"website_content_analysis.log")
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
handler.suffix = "%Y%m%d"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = time.gmtime
handler.setFormatter(formatter)
logger.addHandler(handler)

end_time = datetime.now()

data_directory = '../data'
input_csv_file = os.path.join(data_directory, "url_meta_info_shp.csv")
output_csv_file = os.path.join(data_directory, "website_content_analysis_shp.csv")

# Adding New Features
new_headers = ['Word_Count', 'Link_Count', 'Image_Count', 'Video_Count', 'Has_Ads', 'Domain_Age', 'Payment_Present',
               'Login_Present', 'User_Comments', 'Cookies_Present', 'H1_Count', 'H2_Count']

# Combining all headers
headers = ['URL', 'Category', 'Language', 'Title', 'Meta_Description'] + new_headers


# Getting Domain Age
def get_domain_age(url):
    try:
        domain_info = whois.whois(url)
        creation_date = domain_info.creation_date
        if creation_date:
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            age = (datetime.now() - creation_date).days // 365
            return age
        else:
            return 'N/A'
    except Exception as e:
        logger.error(f"Exception : {e}")
        return 'N/A'


# Checking Payment
def has_payment_system(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = ['pay', 'credit card', 'checkout', 'payment']
        for keyword in keywords:
            if soup.find_all(string=lambda text: keyword in text.lower()):
                return '1'
        return '0'
    except Exception as e:
        logger.error(f"Exception : {e}")
        return 'N/A'


# Checking login
def has_login(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('input', {'type': 'password'}):
            return '1'
        keywords = ['login', 'sign in', 'account']
        for keyword in keywords:
            if soup.find_all(string=lambda text: keyword in text.lower()):
                return '1'
        return '0'
    except Exception as e:
        logger.error(f"Exception : {e}")
        return 'N/A'


# Checking comments
def has_user_comments(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = ['comments', 'review', 'feedback']
        for keyword in keywords:
            if soup.find_all(string=lambda text: keyword in text.lower()):
                return '1'
        return '0'
    except Exception as e:
        logger.error(f"Exception : {e}")
        return 'N/A'


# Checking Cookies
def has_cookies(url):
    try:
        response = requests.get(url, timeout=12)
        if 'set-cookie' in response.headers:
            return '1'
        return '0'
    except Exception as e:
        logger.error(f"Exception : {e}")
        return 'N/A'


# Checking Word_Count, Link_Count, Image_Count, Video_Count, Has_Ads, H1/H2_counts
def analyze_website_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=12)
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
        logger.error(f"Exception : {e}")
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'


# Main process for each URL
def process_url(row):
    url = row['URL']

    word_count, link_count, image_count, video_count, has_ads, h1_count, h2_count = analyze_website_content(url)

    # Check if any of the new headers are 'N/A'. If so, skip this URL.
    if 'N/A' in [word_count, link_count, image_count, video_count, has_ads, h1_count, h2_count]:
        logger.info(f"Skipping {url} due to being N/A for some features.")
        return None  # Skip this row

    domain_age = get_domain_age(url)
    payment_present = has_payment_system(url)
    login_present = has_login(url)
    user_comments = has_user_comments(url)
    cookies_present = has_cookies(url)

    new_row = [
        row['URL'], row['Category'], row['Language'],
        row['Title'], row['Meta_Description'], word_count, link_count, image_count,
        video_count, has_ads, domain_age, payment_present, login_present, user_comments,
        cookies_present, h1_count, h2_count
    ]

    return new_row


# Reading CSV and processing with multi-threading
with open(input_csv_file, mode='r', newline='', encoding='ISO-8859-1') as infile, \
        open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    writer.writerow(headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(process_url, reader)

        for result in results:
            if result is not None:
                writer.writerow(result)

print(f"Content analysis has been saved to {output_csv_file}. {end_time}")
