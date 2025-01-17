import os
import time
import numpy as np
import tensorflow as tf
# from multiprocessing import Process, Manager
import sys

# append是往后放，insert可以选择放的位置，一般可以用于解决冲突
# sys.path.append('..')
sys.path.insert(0, '/home/linchangxiao/labInDiWu/CloudSimPy')

from core.machine import MachineConfig
from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter, mustPrinter
from playground.Non_DAG.algorithm.DeepJS.DRL import RLAlgorithm
from playground.Non_DAG.algorithm.DeepJS.agent import Agent
from playground.Non_DAG.algorithm.DeepJS.brain import BrainSmall
from playground.Non_DAG.algorithm.DeepJS.reward_giver import MakespanRewardGiver

from playground.Non_DAG.utils.csv_reader import CSVReader, MachineConfigReader
from playground.Non_DAG.utils.feature_functions import features_extract_normalize_func
from playground.Non_DAG.utils.tools import multiprocessing_run, average_completion, average_slowdown
from playground.Non_DAG.utils.episode import Episode

os.environ['CUDA_VISIBLE_DEVICES'] = '2'

machine_config_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/machines.csv'
machine_action_config_csv_reader = MachineConfigReader(machine_config_csv)
machine_action_configs = machine_action_config_csv_reader.generate(0, machine_action_config_csv_reader.action_size)
machines_number = len(machine_action_configs)

jobs_len = 100
jobs_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/jobs.csv'
csv_reader = CSVReader(jobs_csv)
jobs_configs = csv_reader.generate(0, jobs_len)


n_iter = 4
n_episode = 2
np.random.seed(41)
tf.random.set_random_seed(41)

feature_size = 12
brain = BrainSmall(feature_size) # TODO(gpu): 原来statesize是6
reward_giver = MakespanRewardGiver(-1)
features_extract_normalize_func = features_extract_normalize_func

name = '%s-%s-m%d' % (reward_giver.name, brain.name, machines_number)
model_dir = './agents/%s' % name
if not os.path.isdir(model_dir):
    os.makedirs(model_dir)

agent = Agent(name, brain, 0.95, reward_to_go=True, nn_baseline=True, normalize_advantages=True,
              model_save_path='%s/model.ckpt' % model_dir)


for itr in range(n_iter):
    tic = time.time()
    print("********** Iteration %i ************" % itr)

    trajectories = list()
    makespans = list()
    average_completions = list()
    average_slowdowns = list()

    for i in range(n_episode):
        # 在这个循环中，其实是没有更新agent的参数的，只是随机地结果会不太一样
        print("********** Episode %i ************" % i)
        algorithm = RLAlgorithm(agent, reward_giver, feature_size, features_extract_normalize_func=features_extract_normalize_func)
        episode = Episode(machine_action_configs, jobs_configs, algorithm, None)
        algorithm.reward_giver.attach(episode.simulation)
        multiprocessing_run(episode, trajectories, makespans, average_completions, average_slowdowns)

    agent.log('makespan', np.mean(makespans), agent.global_step)
    agent.log('average_completions', np.mean(average_completions), agent.global_step)
    agent.log('average_slowdowns', np.mean(average_slowdowns), agent.global_step)

    toc = time.time()

    mustPrinter(__file__, sys._getframe(), "makespans平均值: {0}; duration: {1}; 平均完成时间: {2}; 平均slowdowns:{3}".format(np.mean(makespans), toc - tic, np.mean(average_completions), np.mean(average_slowdowns)))
    
    all_observations = []
    all_actions = []
    all_rewards = []
    # n_episode条轨迹[ [(o, a, r, t), ..., (o, a, r, t)], [(o, a, r, t), ..., (o, a, r, t)], ... , [(o, a, r, t), ..., (o, a, r, t)]  ] 
    for trajectory in trajectories:
        infoPrinter(__file__, sys._getframe(),"检查trajectories: size: {0}".format(len(trajectories)))
        observations = []
        actions = []
        rewards = []
        for node in trajectory:
            if node.observation != None and node.action != None:
                infoPrinter(__file__, sys._getframe(),"\tnode: observation: {0}; action: {1}; reward: {2}"
                .format(node.observation.get_shape().as_list(), # (候选index, 6)
                        node.action, # (选择的index)
                        node.reward)) # (0表示选择了内容， -1表示没选)
            else:
                infoPrinter(__file__, sys._getframe(),"\tnode: observation: {0}; action: {1}; reward: {2}"
                .format(node.observation, 
                        node.action,
                        node.reward))
            observations.append(node.observation)
            actions.append(node.action)
            rewards.append(node.reward)

        all_observations.append(observations)
        all_actions.append(actions)
        all_rewards.append(rewards)

    # 经验回放更新Agent
    all_q_s, all_advantages = agent.estimate_return(all_rewards)

    agent.update_parameters(all_observations, all_actions, all_advantages) # 只有在这里才会更新brain的参数

agent.save()