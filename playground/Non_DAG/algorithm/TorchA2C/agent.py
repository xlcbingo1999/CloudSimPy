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
    def __init__(self, name, brain, gamma, model_save_path, summary_path=None):
        super().__init__()

        self.name = name
        self.gamma = gamma
        self.brain = brain
        self.optimizer = optim.Adam(self.brain.parameters())
        self.model_save_path = model_save_path
        self.summary_path = summary_path if summary_path is not None else './tensorboard/%s--%s' % (
            name, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
        self.summary_writer = SummaryWriter(self.summary_path)

    def save(self):
        torch.save({
            'model_state_dict': self.brain.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, self.model_save_path)

    def restore(self):
        checkpoint = torch.load(self.model_save_path)
        self.brain.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        self.brain.train()

    def log(self, tag, y_value, x_value):
        self.summary_writer.add_scalar(tag, y_value, x_value)