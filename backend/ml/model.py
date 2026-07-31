import torch
import torch.nn as nn

class SignLanguageNN(nn.Module):
    def __init__(self, num_classes: int = 10):
        super(SignLanguageNN, self).__init__()
        # Input: 21 landmarks * 3 coordinates (x, y, z) = 63 features
        self.fc1 = nn.Linear(63, 128)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(128, 64)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(64, num_classes)
        
    def forward(self, x):
        # x expected shape: (batch_size, 63)
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        return x
