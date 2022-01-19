import os
import time
import numpy as np
import torch

import sys
sys.path.insert(0, '/home/linchangxiao/labInDiWu/CloudSimPy')

from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter, mustPrinter
from playground.Non_DAG.algorithm.TorchA2C.brain import Brain
from playground.Non_DAG.algorithm.TorchA2C.RL import RLAlgorithm
from playground.Non_DAG.algorithm.TorchA2C.agent import Agent

from playground.Non_DAG.utils.csv_reader import CSVReader, MachineConfigReader
from playground.Non_DAG.utils.feature_functions import features_extract_normalize_func
from playground.Non_DAG.utils.tools import average_completion, average_slowdown
from playground.Non_DAG.utils.episode import Episode

machine_config_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/machines.csv'
machine_action_config_csv_reader = MachineConfigReader(machine_config_csv)
machine_action_configs = machine_action_config_csv_reader.generate(0, machine_action_config_csv_reader.action_size)
machines_number = len(machine_action_configs)

jobs_len = 100
jobs_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/jobs.csv'
csv_reader = CSVReader(jobs_csv)
jobs_configs = csv_reader.generate(0, jobs_len)

np.random.seed(41)

use_cuda = torch.cuda.is_available()
device   = torch.device("cuda:1" if use_cuda else "cpu")

feature_size = 12
brain = Brain(feature_size).to(device)
features_extract_normalize_func = features_extract_normalize_func

agent = Agent(brain, 0.95)

name = 'torch-%s-m%d' % (brain.name, machines_number)
model_dir = './agents/%s' % name
if not os.path.isdir(model_dir):
    os.makedirs(model_dir)


n_iter = 100

for itr in range(n_iter):
    print("********** Iteration %i ************" % itr)
    tic = time.time()
    algorithm = RLAlgorithm(agent, feature_size, features_extract_normalize_func=features_extract_normalize_func, device=device, update_step_num=12)
    episode = Episode(machine_action_configs, jobs_configs, algorithm, None)
    episode.run()
    print("result makespan: ", episode.env.now, time.time() - tic, average_completion(episode), average_slowdown(episode))