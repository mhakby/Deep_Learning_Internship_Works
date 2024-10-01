import json
import csv
import os
import re
from collections import defaultdict

data_directory = '../data'
input_csv_file = os.path.join(data_directory, "website_content_analysis201.csv")
output_csv_file = os.path.join(data_directory, "keyword_frequency_analysis200.csv")

# JSON files' paths
json_files = {
    'en': os.path.join(data_directory, 'keywords_en.json'),
    'de': os.path.join(data_directory, 'keywords_de.json'),
    'tr': os.path.join(data_directory, 'keywords_tr.json')
}

# Getting keywords from JSON files
keywords = {}
for lang, json_file in json_files.items():
    with open(json_file, 'r', encoding='utf-8') as f:
        keywords[lang] = json.load(f)


# Counting keywords
def count_keyword_occurrences(text, keywords):
    counts = defaultdict(int)
    text = text.lower()
    # Her bir kategori değeri için JSON içerisindeki kategoriler içerisinde yer alan keyword listesi kullanılarak arama yapılması.
    for category, words_list in keywords.items():
        for keyword in words_list:
            # Control of matching keyword/text
            counts[category] += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text))
    return counts


# Normalizing lang code
def normalize_language_code(lang_code):
    if not lang_code or lang_code.lower() == 'n/a':
        return None
    # Sadece dil kısmını almak için '-' ile split işlemi
    normalized_code = lang_code.split('-')[0].lower()
    return normalized_code if normalized_code in keywords else None


# Reading existing file and writing a new.
with open(input_csv_file, mode='r', newline='', encoding='utf-8') as infile, \
        open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    # Getting existing headers
    base_headers = reader.fieldnames
    # Adding values of category to headers as features
    keyword_headers = sorted(set(keyword for lang_keywords in keywords.values() for keyword in lang_keywords))
    # Creating final headers
    headers = base_headers + keyword_headers
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()

    for row in reader:
        url = row['URL']
        title = row['Title']
        meta_description = row['Meta_Description']
        language_code = row['Language']

        normalized_lang_code = normalize_language_code(language_code)

        # Getting keywords for URL-Lang.
        if normalized_lang_code in keywords:
            lang_keywords = keywords[normalized_lang_code]
        else:
            print(f"Language code {language_code} not recognized after normalization. Skipping...")
            continue

        # Counting keywords density for each URL+Title+Meta_Desc.
        url_counts = count_keyword_occurrences(url, lang_keywords)
        title_counts = count_keyword_occurrences(title, lang_keywords)
        meta_counts = count_keyword_occurrences(meta_description, lang_keywords)

        total_counts = defaultdict(int)
        for category in lang_keywords.keys():
            total_counts[category] = url_counts[category] + title_counts[category] + meta_counts[category]

        # Adding counts to current row
        for category in keyword_headers:
            row[category] = total_counts[category]

        writer.writerow(row)

print(f"Keyword frequency analysis has been saved to {output_csv_file}.")
