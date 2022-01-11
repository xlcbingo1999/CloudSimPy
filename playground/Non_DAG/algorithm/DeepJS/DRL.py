import tensorflow as tf
import numpy as np
import sys
from playground.Non_DAG.utils.tools import debugPrinter
from core.scheduler import SchedulerOperation


tf.enable_eager_execution()


class Node(object):
    def __init__(self, observation, action, reward, clock):
        self.observation = observation
        self.action = action
        self.reward = reward
        self.clock = clock


class RLAlgorithm(object):
    def __init__(self, agent, reward_giver, feature_size, features_extract_normalize_func):
        self.agent = agent
        self.reward_giver = reward_giver
        self.features_extract_normalize_func = features_extract_normalize_func
        self.feature_size = feature_size
        self.current_trajectory = [] # (state, action, reward, time)

    def extract_features(self, valid_pairs):
        features = []
        for machine, task, _ in valid_pairs:
            # 原来: 6维向量[machine.cpu, machine.memory, task.cpu, task.memory, task.duration, task.waiting_task_instances_number]
            # 修改: 12维向量[machine.cpu, machine.memory, machine.disk, machine.gpu, machine.gpu_memory, machine.gpu_type, 
            #               task.task_config.cpu, task.task_config.memory, 
            #               task.task_config.gpu, task.task_config.gpu_memory, task.task_config.gpu_type_require, 
            #               task.waiting_task_instances_number]
            current_feature = machine.normal_feature + self.features_extract_normalize_func(task, machine)
            assert len(current_feature) == self.feature_size
            features.append(current_feature)
        return features

    def __call__(self, cluster, clock):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        all_candidates = []

        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    all_candidates.append((machine, task, task.waiting_task_instances[0]))
        operator_index = SchedulerOperation.SILENCE
        if len(all_candidates) == 0:
            self.current_trajectory.append(Node(None, None, self.reward_giver.get_reward(), clock))
            operator_index = SchedulerOperation.OVER_SCHEDULER
            return operator_index, None, None, None
        else:
            features = self.extract_features(all_candidates)
            features = tf.convert_to_tensor(features, dtype=np.float32)
            debugPrinter(__file__, sys._getframe(), "所有候选集构成的维度: {0}".format(features.get_shape().as_list()))
            logits = self.agent.brain(features)
            debugPrinter(__file__, sys._getframe(), "经过Brain后维度: {0}".format(logits.get_shape().as_list()))
            pair_index = tf.squeeze(tf.multinomial(logits, num_samples=1), axis=1).numpy()[0]
            debugPrinter(__file__, sys._getframe(), "Action: (machine: {0}; task: {1})".format(all_candidates[pair_index][0].id, all_candidates[pair_index][1].task_index))

            node = Node(features, pair_index, 0, clock) # 四元组, 用于经验回放
            self.current_trajectory.append(node)
            
            operator_index = SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN
        return operator_index, all_candidates[pair_index][0], all_candidates[pair_index][1], all_candidates[pair_index][2]
