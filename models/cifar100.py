from capsule_layer import CapsuleLinear
from torch import nn


class CIFAR100CapsuleNet(nn.Module):
    def __init__(self, num_iterations=3):
        super(CIFAR100CapsuleNet, self).__init__()
        self.block1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=64),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=64)
        )
        self.block2 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=128),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=128),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(num_features=128)
        )
        self.block3 = nn.Sequential(
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=256),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=256),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(num_features=256)
        )
        self.block4 = nn.Sequential(
            nn.Conv2d(in_channels=256, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=512),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=512),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(num_features=512)
        )
        self.block5 = nn.Sequential(
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=512),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=512),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(num_features=512)
        )
        self.down_block1 = nn.Sequential(nn.Conv2d(in_channels=3, out_channels=64, kernel_size=1, stride=1),
                                         nn.BatchNorm2d(num_features=64))
        self.down_block2 = nn.Sequential(nn.Conv2d(in_channels=64, out_channels=128, kernel_size=1, stride=2),
                                         nn.BatchNorm2d(num_features=128))
        self.down_block3 = nn.Sequential(nn.Conv2d(in_channels=128, out_channels=256, kernel_size=1, stride=2),
                                         nn.BatchNorm2d(num_features=256))
        self.down_block4 = nn.Sequential(nn.Conv2d(in_channels=256, out_channels=512, kernel_size=1, stride=2),
                                         nn.BatchNorm2d(num_features=512))
        self.down_block5 = nn.Sequential(nn.Conv2d(in_channels=512, out_channels=512, kernel_size=1, stride=2),
                                         nn.BatchNorm2d(num_features=512))
        self.relu = nn.ReLU(inplace=True)
        self.classifier = nn.Sequential(CapsuleLinear(in_capsules=512, out_capsules=256, in_length=4, out_length=8,
                                                      routing_type='contract', share_weight=False,
                                                      num_iterations=num_iterations),
                                        CapsuleLinear(in_capsules=256, out_capsules=100, in_length=8, out_length=16,
                                                      routing_type='contract', share_weight=False,
                                                      num_iterations=num_iterations))

    def forward(self, x):
        features = x
        out = self.block1(features)
        out += self.down_block1(features)
        out = self.relu(out)

        features = out
        out = self.block2(features)
        out += self.down_block2(features)
        out = self.relu(out)

        features = out
        out = self.block3(features)
        out += self.down_block3(features)
        out = self.relu(out)

        features = out
        out = self.block4(features)
        out += self.down_block4(features)
        out = self.relu(out)

        features = out
        out = self.block5(features)
        out += self.down_block5(features)
        out = self.relu(out)

        out = out.view(*out.size()[:2], -1)
        out = out.transpose(-1, -2)
        out = out.contiguous().view(out.size(0), -1, 4)

        out = self.classifier(out)
        classes = out.norm(dim=-1)
        return classes
