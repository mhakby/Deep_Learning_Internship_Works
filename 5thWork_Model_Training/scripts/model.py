import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.initializers import HeNormal
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from preproccessing import target
from plot_results import plot_confusion_matrix, plot_classification_report, plot_training_history


# Creating Model Func
def create_model(input_shape, num_classes, dropout_rate=0.1, l1_reg=0.005, l2_reg=0.005):
    initializer = HeNormal()
    model = Sequential([
        Input(shape=(input_shape,)),
        Dense(64, activation='relu', kernel_regularizer=l1_l2(l1=l1_reg, l2=l2_reg), kernel_initializer=initializer),
        Dropout(dropout_rate),
        Dense(32, activation='relu', kernel_regularizer=l1_l2(l1=l1_reg, l2=l2_reg), kernel_initializer=initializer),
        Dropout(dropout_rate),
        Dense(num_classes, activation='softmax', kernel_initializer=initializer)
    ])

    optimizer = Adam(learning_rate=0.005)
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Defining number of classes
num_classes = len(target)

# Preparing for Label Encoding
label_encoder = LabelEncoder()
label_encoder.fit(target)

# Loading data
current_directory = os.getcwd()
X_train = np.load(os.path.join(current_directory, 'X_train_scaled.npy'))
y_train = np.load(os.path.join(current_directory, 'y_train.npy'), allow_pickle=True)
X_val = np.load(os.path.join(current_directory, 'X_val_scaled.npy'))
y_val = np.load(os.path.join(current_directory, 'y_val.npy'), allow_pickle=True)
X_test = np.load(os.path.join(current_directory, 'X_test_scaled.npy'))
y_test = np.load(os.path.join(current_directory, 'y_test.npy'), allow_pickle=True)

# Checking the target variables
def check_labels(y):
    unique_labels = np.unique(y)
    print(f'Unique labels in y: {unique_labels}')

check_labels(y_train)
check_labels(y_val)
check_labels(y_test)

# Converting string labels to numeric labels
y_train_encoded = label_encoder.transform(y_train)
y_val_encoded = label_encoder.transform(y_val)
y_test_encoded = label_encoder.transform(y_test)

# Encode targets with one-hot encoding
y_train_categorical = to_categorical(y_train_encoded, num_classes=num_classes)
y_val_categorical = to_categorical(y_val_encoded, num_classes=num_classes)
y_test_categorical = to_categorical(y_test_encoded, num_classes=num_classes)

# Creating model
model = create_model(X_train.shape[1], num_classes=num_classes)

# Setting EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Train the model
history = model.fit(X_train, y_train_categorical, epochs=50, validation_data=(X_val, y_val_categorical), callbacks=[early_stopping])

# Save the model
model.save('website_category_model.keras')

# Evaluating performance at Test's dataset
y_test_pred = model.predict(X_test)
y_test_pred_classes = np.argmax(y_test_pred, axis=1)
y_test_true_classes = np.argmax(y_test_categorical, axis=1)

# Creating graphs for history, confusion_matrix and classification_report
plot_training_history(history)
plot_confusion_matrix(y_test_true_classes, y_test_pred_classes, label_encoder)
plot_classification_report(y_test_true_classes, y_test_pred_classes, label_encoder)
