import os
import csv

base_directory = "../data/bl"

output_csv = "urls_and_categories.csv"

headers = ["URL", "Category"]

with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headers)  # Writing headers

    for category_folder in os.listdir(base_directory):
        category_path = os.path.join(base_directory, category_folder)

        if os.path.isdir(category_path):
            for file_name in os.listdir(category_path):
                file_path = os.path.join(category_path, file_name)

                if os.path.isfile(file_path) and file_name == 'domains':
                    with open(file_path, 'r', encoding='utf-8') as file:
                        urls = file.readlines()  # Read all rows

                        for url in urls:
                            cleaned_url = url.strip()  # Cleaning blanks
                            if cleaned_url:
                                writer.writerow([cleaned_url, category_folder])

print(f"Data was written at {output_csv} file.")
