import time
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import sys
from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter


class Agent(object):
    def __init__(self, brain, gamma):
        super().__init__()

        self.gamma = gamma
        self.brain = brain
        self.optimizer = optim.Adam(self.brain.parameters())
