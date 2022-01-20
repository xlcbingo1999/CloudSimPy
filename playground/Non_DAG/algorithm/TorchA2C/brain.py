import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class ValueNetwork(nn.Module):
    def __init__(self, state_size):
        super(ValueNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 1)
    
    def forward(self, state):
        value = F.relu(self.fc1(state))
        value = self.fc2(value)

        # 先压缩维度，然后得到value的平均值，最后上升维度为1维向量
        # TODO: 观察了实验结果，发现这个value的值基本上一直在下降，而且基本上都是负数
        mean_res_value = torch.unsqueeze(torch.mean(torch.squeeze(value, -1)), 0)
        debugPrinter(__file__, sys._getframe(), "brain res_value {}".format(mean_res_value))

        return mean_res_value

class ActorNetwork(nn.Module):
    def __init__(self, state_size):
        super(ActorNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 1)
    
    def forward(self, state):
        probs = F.relu(self.fc1(state))
        probs = F.softmax(self.fc2(probs), dim=0)

        res_probs = torch.unsqueeze(torch.squeeze(probs, -1), 0) # 2维转置
        dist  = Categorical(res_probs) # 返回分布，在外部进行Action采样
        debugPrinter(__file__, sys._getframe(), "check res_probs: {}".format(res_probs))

        return dist

class Brain(object):
    name = 'Brain'

    def __init__(self, state_size):
        super(Brain, self).__init__()
        self.critic_network = ValueNetwork(state_size)
        self.actor_network = ActorNetwork(state_size)

    def to_device(self, device):
        self.critic_network = self.critic_network.to(device)
        self.actor_network = self.actor_network.to(device)

    def get_state_dicts(self):
        return self.critic_network.state_dict(), self.actor_network.state_dict()

    def load_state_dicts(self, critic_checkpoint, actor_checkpoint):
        self.critic_network.load_state_dict(critic_checkpoint)
        self.actor_network.load_state_dict(actor_checkpoint)

    def get_parameters(self):
        return self.critic_network.parameters(), self.actor_network.parameters()

    def go_train(self):
        self.critic_network.train()
        self.actor_network.train()

    def go_eval(self):
        self.critic_network.eval()
        self.actor_network.eval()