import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import os

# Load the data
data = pd.read_csv('../data/keyword_frequency_all_categories.csv', encoding='ISO-8859-1')
data.dropna(inplace=True)

# Additional features we want to add
additional_features = ["news_and_media", "shopping", "games", "social_networking"]

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

# Applying SMOTE to the training data to balance the classes
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

# Scaling the data (Standard Scaler)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_smote)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Save the processed data in the current directory
current_directory = os.getcwd()

# Save the files with full path
np.save(os.path.join(current_directory, 'X_train_scaled.npy'), X_train_scaled)
np.save(os.path.join(current_directory, 'y_train.npy'), y_train_smote)
np.save(os.path.join(current_directory, 'X_val_scaled.npy'), X_val_scaled)
np.save(os.path.join(current_directory, 'y_val.npy'), y_val)
np.save(os.path.join(current_directory, 'X_test_scaled.npy'), X_test_scaled)
np.save(os.path.join(current_directory, 'y_test.npy'), y_test)

print("Data processing completed and saved.")
