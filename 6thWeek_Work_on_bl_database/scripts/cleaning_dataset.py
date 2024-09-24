import csv

input_csv_file = '../data/url_meta_info.csv'
output_csv_file = '../data/url_and_categories_shp.csv'

# Okuma ve yazma işlemi
with open(input_csv_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        if row['Language'] != 'N/A' and row['Title'] != 'N/A' and row['Meta_Description'] != 'N/A':
            writer.writerow(row)

print(f"Cleaned CSV file has been saved as {output_csv_file}.")
