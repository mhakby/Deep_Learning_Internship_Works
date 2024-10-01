import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

# Load the data
data = pd.read_csv('../data/data200.csv')  # Ensure the correct path to your dataset
data.dropna(inplace=True)

# Additional features we want to add
additional_features = ["abortion", "advertising", "advocacy_organizations", "alcohol", "alternative_beliefs",
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
        "web_based_email", "web_chat", "web_hosting"]

# Define the Features and Target columns
features = data[['Word_Count', 'Link_Count', 'Image_Count', 'Video_Count', 'Has_Ads', 'Domain_Age',
                 'Payment_Present', 'Login_Present', 'User_Comments', 'Cookies_Present', 'H1_Count', 'H2_Count'] + additional_features]

# Target: Category column
target = data['Category']

# Remove classes with insufficient samples
min_samples_per_class = 2
class_counts = target.value_counts()
valid_classes = class_counts[class_counts >= min_samples_per_class].index

# Filter data and target to only keep valid classes
filtered_data = data[data['Category'].isin(valid_classes)]
features = features.loc[filtered_data.index]  # Select rows only in valid indices
target = filtered_data['Category']

# First data split
X_train, X_temp, y_train, y_temp = train_test_split(features, target, test_size=0.3, random_state=42, stratify=target)

# Remove classes with insufficient samples from the temporary set (X_temp, y_temp)
temp_class_counts = y_temp.value_counts()
valid_temp_classes = temp_class_counts[temp_class_counts >= min_samples_per_class].index

# Filter the temporary set to remove classes with insufficient samples
X_temp = X_temp[y_temp.isin(valid_temp_classes)]
y_temp = y_temp[y_temp.isin(valid_temp_classes)]

# Second data split
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# Scaling the data (Standard Scaler)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Save the processed data in the current directory
current_directory = os.getcwd()

# Save the files with full path
np.save(os.path.join(current_directory, 'X_train_scaled.npy'), X_train_scaled)
np.save(os.path.join(current_directory, 'y_train.npy'), y_train)
np.save(os.path.join(current_directory, 'X_val_scaled.npy'), X_val_scaled)
np.save(os.path.join(current_directory, 'y_val.npy'), y_val)
np.save(os.path.join(current_directory, 'X_test_scaled.npy'), X_test_scaled)
np.save(os.path.join(current_directory, 'y_test.npy'), y_test)

print("Data processing completed and saved.")
