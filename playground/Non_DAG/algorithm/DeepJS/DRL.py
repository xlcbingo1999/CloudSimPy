import tensorflow as tf
import numpy as np
import sys
from playground.Non_DAG.utils.tools import debugPrinter


tf.enable_eager_execution()


class Node(object):
    def __init__(self, observation, action, reward, clock):
        self.observation = observation
        self.action = action
        self.reward = reward
        self.clock = clock


class RLAlgorithm(object):
    def __init__(self, agent, reward_giver, features_normalize_func, features_extract_func):
        self.agent = agent
        self.reward_giver = reward_giver
        self.features_normalize_func = features_normalize_func
        self.features_extract_func = features_extract_func
        self.current_trajectory = []

    def extract_features(self, valid_pairs):
        features = []
        for machine, task in valid_pairs:
            features.append([machine.cpu, machine.memory] + self.features_extract_func(task))
        features = self.features_normalize_func(features)
        return features

    def __call__(self, cluster, clock):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        all_candidates = []

        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    all_candidates.append((machine, task))
        if len(all_candidates) == 0:
            self.current_trajectory.append(Node(None, None, self.reward_giver.get_reward(), clock))
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], None, None))
            return None, None
        else:
            features = self.extract_features(all_candidates)
            features = tf.convert_to_tensor(features, dtype=np.float32)
            logits = self.agent.brain(features)
            pair_index = tf.squeeze(tf.multinomial(logits, num_samples=1), axis=1).numpy()[0]

            node = Node(features, pair_index, 0, clock)
            self.current_trajectory.append(node)
        debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], all_candidates[pair_index][0].id, all_candidates[pair_index][1].task_index))
        return all_candidates[pair_index]
