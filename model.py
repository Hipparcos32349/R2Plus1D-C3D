import torch
from capsule_layer import CapsuleLinear
from torch import nn
from torch_geometric.nn import GCNConv
from torch_geometric.utils import remove_self_loops

from utils import global_sort_pool


class Model(nn.Module):
    def __init__(self, num_features, num_classes, num_iterations=3):
        super(Model, self).__init__()

        self.conv1 = GCNConv(num_features, 32)
        self.conv2 = GCNConv(32, 32)
        self.conv3 = GCNConv(32, 32)
        self.classifier = CapsuleLinear(out_capsules=num_classes, in_length=96, out_length=32, in_capsules=50,
                                        share_weight=False, routing_type='k_means', num_iterations=num_iterations)

    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        edge_index, _ = remove_self_loops(edge_index)

        x_1 = torch.tanh(self.conv1(x, edge_index))
        x_2 = torch.tanh(self.conv2(x_1, edge_index))
        x_3 = torch.tanh(self.conv3(x_2, edge_index))
        x = torch.cat([x_1, x_2, x_3], dim=-1)
        out = self.classifier(global_sort_pool(x, batch, k=50))
        classes = out.norm(dim=-1)

        return classes
