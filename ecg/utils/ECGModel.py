import torch
import torch.nn as nn
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights

class ECGClassifier(nn.Module):
    def __init__(self, num_classes=4):
        super(ECGClassifier, self).__init__()

        # Load ResNet18 with updated weights parameter
        weights = ResNet18_Weights.DEFAULT  # or IMAGENET1K_V1
        self.base_model = models.resnet18(weights=weights)

        # Freeze early layers
        for param in self.base_model.parameters():
            param.requires_grad = False
        for param in self.base_model.layer4.parameters():
            param.requires_grad = True

        # Replace final FC layer
        num_ftrs = self.base_model.fc.in_features
        self.base_model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.base_model(x)


class CNNModel2(nn.Module):
    def __init__(self, num_classes=4):
        super(CNNModel, self).__init__()
        # Using a pretrained ResNet18
        self.base_model = models.resnet18(pretrained=True)

        # Freeze initial layers
        for param in self.base_model.parameters():
            param.requires_grad = False

        # Unfreeze last few layers
        for param in self.base_model.layer4.parameters():
            param.requires_grad = True

        # Replace the final fully connected layer
        num_ftrs = self.base_model.fc.in_features
        self.base_model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.base_model(x)


class CNNModel1(nn.Module):
    def __init__(self, num_classes, input_size=(150, 150)):
        super(CNNModel, self).__init__()

        # Load the pretrained ResNet18 model
        resnet18 = models.resnet18(weights=ResNet18_Weights.DEFAULT)

        # Remove the fully connected (classifier) part of ResNet18
        self.features = nn.Sequential(*list(resnet18.children())[:-1])  # Exclude the last fully connected layer

        # Dynamically compute the input size for the linear layer
        dummy_input = torch.zeros(1, 3, *input_size)  # Adjust size to match input images
        features_output = self.features(dummy_input)
        flattened_size = features_output.view(-1).shape[0]

        # Add your custom classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(flattened_size, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)  # Extract features from ResNet18
        x = self.classifier(x)  # Pass through custom classifier
        return x
