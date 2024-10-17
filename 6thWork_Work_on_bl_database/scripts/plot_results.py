import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np


# Plotting loss and accuracy
def plot_training_history(history):
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()


# Creating confusion matrix
def plot_confusion_matrix(y_true, y_pred, label_encoder):
    conf_matrix = confusion_matrix(y_true, y_pred)
    predicted_labels = label_encoder.inverse_transform(np.unique(y_pred))
    true_labels = label_encoder.inverse_transform(np.unique(y_true))

    plt.figure(figsize=(12, 10))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=predicted_labels, yticklabels=true_labels)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.show()


# Creating classification report
def plot_classification_report(y_true, y_pred, label_encoder):
    labels = np.unique(y_true)
    class_report = classification_report(y_true, y_pred, labels=labels,
                                         target_names=label_encoder.inverse_transform(labels))
    print(class_report)
