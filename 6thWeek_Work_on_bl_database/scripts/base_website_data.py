import requests
import csv
from bs4 import BeautifulSoup
import concurrent.futures
from datetime import datetime
import os
import time
import logging
from logging.handlers import TimedRotatingFileHandler

end_time = datetime.now()

logger = logging.getLogger(f"base_website_data")
logger.setLevel(logging.INFO)

# Creating log file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(base_dir, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file = os.path.join(logs_dir, f"base_website_data.log")
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
handler.suffix = "%Y%m%d"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = time.gmtime
handler.setFormatter(formatter)
logger.addHandler(handler)

input_csv_file = '../data/url_and_categories_shp.csv'
output_csv_file = '../data/url_meta_info_shp.csv'

headers = ['URL', 'Category', 'Language', 'Title', 'Meta_Description']


def get_website_metadata(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, timeout=12, verify=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        meta_description = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={
            'property': 'og:description'})
        description_content = meta_description['content'] if meta_description else 'N/A'

        lang = soup.find('html')['lang'] if soup.find('html') and 'lang' in soup.find('html').attrs else 'N/A'

        title = soup.find('title').get_text().strip() if soup.find('title') else 'N/A'

        return lang, title, description_content

    except Exception as e:
        logger.info(f"Error while parsing {url}: {e}")
        return 'N/A', 'N/A', 'N/A'


def add_scheme(url):
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url


def process_url(row):
    url = row['URL']
    category = row['Category']

    full_url = add_scheme(url)

    language, title, meta_description = get_website_metadata(full_url)

    if 'N/A' in [language, title, meta_description]:
        logger.info(f"Skipping {url} due to missing metadata (Language: {language}, Title: {title}, Meta: {meta_description})")
        return None

    return [full_url, category, language, title, meta_description]


with open(input_csv_file, mode='r', newline='', encoding='utf-8') as infile, \
        open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    writer.writerow(headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(process_url, reader)

        for result in results:
            if result is not None:
                writer.writerow(result)

print(f"Metadata has been saved to {output_csv_file}. {end_time}")