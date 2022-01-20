import time
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter   
import sys
from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter


class Agent(object):
    def __init__(self, name, brain, device, gamma, model_save_path, summary_path=None):
        super().__init__()

        self.name = name
        self.gamma = gamma
        self.brain = brain
        self.device = device
        self.brain.to_device(self.device)
        value_para, actor_para = self.brain.get_parameters()
        self.value_network_optimizer, self.actor_network_optimizer = optim.Adam(value_para), optim.Adam(actor_para)
        self.model_save_path = model_save_path
        self.summary_path = summary_path if summary_path is not None else './tensorboard/%s--%s' % (
            name, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
        self.summary_writer = SummaryWriter(self.summary_path)

    def save(self):
        value_network_state_dict, actor_network_state_dict = self.brain.get_state_dicts()
        torch.save({
            'value_network_state_dict': value_network_state_dict,
            'actor_network_state_dict': actor_network_state_dict,
            'value_network_optimizer_state_dict': self.value_network_optimizer.state_dict(),
            'actor_network_optimizer_state_dict': self.actor_network_optimizer.state_dict(),
        }, self.model_save_path)

    def restore(self):
        checkpoint = torch.load(self.model_save_path)
        self.brain.load_state_dicts(checkpoint['value_network_state_dict'], checkpoint['actor_network_state_dict'])
        self.value_network_optimizer.load_state_dict(checkpoint['value_network_optimizer_state_dict'])
        self.actor_network_optimizer.load_state_dict(checkpoint['actor_network_optimizer_state_dict'])
        self.brain.go_train()

    def log(self, tag, y_value, x_value):
        self.summary_writer.add_scalar(tag, y_value, x_value)