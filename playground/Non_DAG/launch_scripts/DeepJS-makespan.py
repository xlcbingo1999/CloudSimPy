import os
import time
import numpy as np
import tensorflow as tf
from multiprocessing import Process, Manager
import sys

# append是往后放，insert可以选择放的位置，一般可以用于解决冲突
# sys.path.append('..')
sys.path.insert(0, '/home/linchangxiao/labInDiWu/CloudSimPy')

from core.machine import MachineConfig
from playground.Non_DAG.utils.tools import debugPrinter
from playground.Non_DAG.algorithm.DeepJS.DRL import RLAlgorithm
from playground.Non_DAG.algorithm.DeepJS.agent import Agent
from playground.Non_DAG.algorithm.DeepJS.brain import BrainSmall
from playground.Non_DAG.algorithm.DeepJS.reward_giver import MakespanRewardGiver

from playground.Non_DAG.utils.csv_reader import CSVReader
from playground.Non_DAG.utils.feature_functions import features_extract_func, features_normalize_func
from playground.Non_DAG.utils.tools import multiprocessing_run, average_completion, average_slowdown
from playground.Non_DAG.utils.episode import Episode

os.environ['CUDA_VISIBLE_DEVICES'] = ''

np.random.seed(41)
tf.random.set_random_seed(41)

machines_number = 5
jobs_len = 10
n_iter = 1
n_episode = 1
jobs_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/jobs.csv'

brain = BrainSmall(6)
reward_giver = MakespanRewardGiver(-1)
features_extract_func = features_extract_func
features_normalize_func = features_normalize_func # 这里的公式没看懂啊

name = '%s-%s-m%d' % (reward_giver.name, brain.name, machines_number)
model_dir = './agents/%s' % name

if not os.path.isdir(model_dir):
    os.makedirs(model_dir)

agent = Agent(name, brain, 1, reward_to_go=True, nn_baseline=True, normalize_advantages=True,
              model_save_path='%s/model.ckpt' % model_dir)

# xiaolinchang: without GPU, cpu: 64 mem: 1 disk: 1
machine_configs = [MachineConfig(64, 1, 1) for i in range(machines_number)]
csv_reader = CSVReader(jobs_csv)
jobs_configs = csv_reader.generate(0, jobs_len)

for itr in range(n_iter):
    tic = time.time()
    print("********** Iteration %i ************" % itr)
    processes = []

    manager = Manager()
    trajectories = manager.list([])
    makespans = manager.list([])
    average_completions = manager.list([])
    average_slowdowns = manager.list([])

    for i in range(n_episode):
        algorithm = RLAlgorithm(agent, reward_giver, features_extract_func=features_extract_func,
                                features_normalize_func=features_normalize_func)
        episode = Episode(machine_configs, jobs_configs, algorithm, None)
        algorithm.reward_giver.attach(episode.simulation)
        p = Process(target=multiprocessing_run,
                    args=(episode, trajectories, makespans, average_completions, average_slowdowns))

        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    agent.log('makespan', np.mean(makespans), agent.global_step)
    agent.log('average_completions', np.mean(average_completions), agent.global_step)
    agent.log('average_slowdowns', np.mean(average_slowdowns), agent.global_step)

    toc = time.time()

    debugPrinter(__file__, sys._getframe(), "makespans平均值: {0}; duration: {1}; 平均完成时间: {2}; 平均slowdowns:{3}".format(np.mean(makespans), toc - tic, np.mean(average_completions), np.mean(average_slowdowns)))
    
    all_observations = []
    all_actions = []
    all_rewards = []
    for trajectory in trajectories:
        observations = []
        actions = []
        rewards = []
        for node in trajectory:
            observations.append(node.observation)
            actions.append(node.action)
            rewards.append(node.reward)

        all_observations.append(observations)
        all_actions.append(actions)
        all_rewards.append(rewards)

    all_q_s, all_advantages = agent.estimate_return(all_rewards)

    agent.update_parameters(all_observations, all_actions, all_advantages)

agent.save()