import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class Brain(nn.Module):
    name = 'Brain'

    def __init__(self, state_size):
        super(Brain, self).__init__()
        
        self.critic = nn.Sequential(
            nn.Linear(state_size, 256),
            nn.ReLU(),
            nn.Linear(256, 1) # 维度应该为1
        )
        
        self.actor = nn.Sequential(
            nn.Linear(state_size, 256),
            nn.ReLU(),
            nn.Linear(256, 1), # 维度应该为候选采样action的数量大小，用于返回动作概率
            nn.Softmax(dim=1)
        )
        
    def forward(self, state):
        value = self.critic(state)
        probs = self.actor(state)
        res_probs = torch.unsqueeze(torch.squeeze(probs, -1), 0)
        res_value = torch.squeeze(value, -1)
        
        dist  = Categorical(res_probs) # 返回分布
        mean_res_value = torch.unsqueeze(torch.mean(res_value), 0)
        debugPrinter(__file__, sys._getframe(), "brain res_value {}".format(mean_res_value.shape))
        return dist, mean_res_value
        
