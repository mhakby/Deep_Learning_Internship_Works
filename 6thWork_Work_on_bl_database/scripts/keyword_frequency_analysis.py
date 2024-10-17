# Fourth Process
import json
import csv
import os
import re
from collections import defaultdict

data_directory = '../data'
input_csv_file = os.path.join(data_directory, "all_categories_data.csv")
output_csv_file = os.path.join(data_directory, "keyword_frequency_all_categories.csv")

# Tek JSON dosyasının yolu
json_file = os.path.join(data_directory, 'keywords.json')

# JSON dosyasını yükleme (tüm dilleri içinde barındıran JSON)
with open(json_file, 'r', encoding='ISO-8859-1') as f:
    keywords = json.load(f)


# Keywordlerin sayısını hesaplama
def count_keyword_occurrences(text, keywords):
    counts = defaultdict(int)
    text = text.lower()
    # Her bir kategori değeri için JSON içerisindeki kategorilerdeki keyword listesi kullanılarak arama yapılır.
    for category, words_list in keywords.items():
        for keyword in words_list:
            # Anahtar kelimelerin text'te olup olmadığını kontrol etme
            counts[category] += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text))
    return counts


# Dil kodunu normalize etme
def normalize_language_code(lang_code):
    if not lang_code or lang_code.lower() == 'n/a':
        return None
    # Sadece dil kısmını almak için '-' ile split işlemi
    normalized_code = lang_code.split('-')[0].lower()
    return normalized_code if normalized_code in keywords else None


# Varolan dosyayı okuyup, yeni dosyaya yazma
with open(input_csv_file, mode='r', newline='', encoding='ISO-8859-1') as infile, \
        open(output_csv_file, mode='w', newline='', encoding='ISO-8859-1') as outfile:
    reader = csv.DictReader(infile)
    # Mevcut başlıkları alıyoruz
    base_headers = reader.fieldnames
    # Kategori değerlerine göre başlıklara feature ekliyoruz
    keyword_headers = sorted(set(keyword for lang_keywords in keywords.values() for keyword in lang_keywords))
    # Nihai başlıkları oluşturuyoruz
    headers = base_headers + keyword_headers
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()

    for row in reader:
        url = row['URL']
        title = row['Title']
        meta_description = row['Meta_Description']
        language_code = row['Language']

        normalized_lang_code = normalize_language_code(language_code)

        # Dil koduna göre keyword'leri alıyoruz
        if normalized_lang_code in keywords:
            lang_keywords = keywords[normalized_lang_code]
        else:
            print(f"Language code {language_code} not recognized after normalization. Skipping...")
            continue

        # URL+Title+Meta_Desc'deki keyword sıklıklarını sayıyoruz
        url_counts = count_keyword_occurrences(url, lang_keywords)
        title_counts = count_keyword_occurrences(title, lang_keywords)
        meta_counts = count_keyword_occurrences(meta_description, lang_keywords)

        total_counts = defaultdict(int)
        for category in lang_keywords.keys():
            total_counts[category] = url_counts[category] + title_counts[category] + meta_counts[category]

        # Mevcut satıra keyword sayımlarını ekleme
        for category in keyword_headers:
            row[category] = total_counts[category]

        writer.writerow(row)

print(f"Keyword frequency analysis has been saved to {output_csv_file}.")
