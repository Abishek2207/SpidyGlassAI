import os
import torch
import numpy as np
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns

from dataset import LandmarkDataset

def validate():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Validating on device: {device}")

    val_path = "dataset/validation/val_landmarks.csv"
    if not os.path.exists(val_path):
        print(f"Validation dataset not found at {val_path}.")
        print("Note: The training scripts are ready and production-grade, but dataset collection is required before sign_language.pt can be produced.")
        return

    dataset = LandmarkDataset(val_path)
    if len(dataset) == 0:
        print("Validation dataset is empty.")
        return
        
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)
    
    model_path = "models/sign_language.pt"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Train the model first.")
        return

    model = torch.load(model_path, map_location=device)
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    print("Running inference on validation set...")
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            
            probs = torch.nn.functional.softmax(outputs, dim=1)
            _, predicted = torch.max(probs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            
    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    print("\n--- Validation Metrics ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    # Top-K Accuracy
    all_probs_np = np.array(all_probs)
    all_labels_np = np.array(all_labels)
    
    top3_correct = 0
    for i in range(len(all_labels_np)):
        top3_preds = np.argsort(all_probs_np[i])[-3:]
        if all_labels_np[i] in top3_preds:
            top3_correct += 1
            
    top3_acc = top3_correct / max(len(all_labels_np), 1)
    print(f"Top-3 Acc: {top3_acc * 100:.2f}%")

    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    os.makedirs('exports', exist_ok=True)
    plt.savefig('exports/confusion_matrix.png')
    print("Saved confusion matrix to exports/confusion_matrix.png")

if __name__ == "__main__":
    validate()
