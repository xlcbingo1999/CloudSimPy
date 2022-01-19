import time
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import sys
from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter


class Agent(object):
    def __init__(self, brain, gamma, model_save_path):
        super().__init__()

        self.gamma = gamma
        self.brain = brain
        self.optimizer = optim.Adam(self.brain.parameters())
        self.model_save_path = model_save_path

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