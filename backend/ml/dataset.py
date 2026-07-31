import csv
import torch
from torch.utils.data import Dataset
import numpy as np

class LandmarkDataset(Dataset):
    def __init__(self, csv_file: str, normalize: bool = True):
        """
        Loads dataset from CSV file.
        Format: label, x0, y0, z0, ..., x20, y20, z20 (64 columns total)
        """
        super().__init__()
        self.samples = []
        self.labels = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None) # Skip header
                
                for row in reader:
                    if len(row) == 64:
                        label = int(row[0])
                        features = [float(val) for val in row[1:]]
                        self.labels.append(label)
                        self.samples.append(features)
        except Exception as e:
            # Fallback for when dataset doesn't exist
            print(f"Warning: Could not load dataset {csv_file}: {e}")
            self.samples = []
            self.labels = []
            
        self.samples = np.array(self.samples, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)
        
        if normalize and len(self.samples) > 0:
            self._normalize()

    def _normalize(self):
        """
        Normalizes landmarks. Centralizes around the wrist (landmark 0).
        Then scales them to unit variance.
        """
        for i in range(len(self.samples)):
            # x0, y0, z0 are indices 0, 1, 2
            wrist_x = self.samples[i, 0]
            wrist_y = self.samples[i, 1]
            wrist_z = self.samples[i, 2]
            
            for j in range(0, 63, 3):
                self.samples[i, j] -= wrist_x
                self.samples[i, j+1] -= wrist_y
                self.samples[i, j+2] -= wrist_z
                
            # Scale to max absolute value
            max_val = np.max(np.abs(self.samples[i]))
            if max_val > 0:
                self.samples[i] /= max_val

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x = torch.tensor(self.samples[idx], dtype=torch.float32)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        return x, y
