import csv
import time
import requests
from bs4 import BeautifulSoup
import socket
import certifi


def has_ssl(url):
    try:
        response = requests.get(url, timeout=5, verify=certifi.where())
        return response.url.startswith("https")
    except requests.exceptions.RequestException:
        return None


def get_page_length_and_links(url):
    try:
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.text, 'html.parser')
        page_length = len(soup.get_text())
        link_count = len(soup.find_all('a'))
        return page_length, link_count
    except Exception:
        return None, None


def get_image_count(url):
    try:
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.text, 'html.parser')
        image_count = len(soup.find_all('img'))
        return image_count
    except Exception:
        return None


def get_video_count(url):
    try:
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.text, 'html.parser')
        video_count = len(soup.find_all('video')) + len(soup.find_all('iframe'))
        return video_count
    except Exception:
        return None


def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return None


def get_hosting_info(ip_address, retries=2, wait_time=2):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json", verify=certifi.where())
            data = response.json()
            org_info = data.get('org')

            if org_info and org_info.startswith("AS"):
                asn_number = org_info.split()[0][2:]  # example : "AS16509" -> "16509"
                return asn_number
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}. Retrying...")
            attempt += 1
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error fetching hosting info: {e}")
            return None
    return None


def update_csv(file_name="results_3.csv"):
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    fieldnames = reader.fieldnames + ['ssl_certificate', 'page_length', 'link_count', 'image_count',
                                      'video_count', 'hosting_org']

    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            url = row['link']
            domain = url.split("//")[-1].split("/")[0]

            ip_address = get_ip_address(domain)
            if ip_address:
                hosting_org = get_hosting_info(ip_address)
            else:
                hosting_org = None

            ssl_status = has_ssl(url)
            if ssl_status is not None:
                row['ssl_certificate'] = int(ssl_status)
            else:
                row['ssl_certificate'] = "N/A"
            row['page_length'], row['link_count'] = get_page_length_and_links(url)
            row['image_count'] = get_image_count(url)
            row['video_count'] = get_video_count(url)
            row['hosting_org'] = hosting_org

            writer.writerow(row)


if __name__ == "__main__":
    update_csv()
