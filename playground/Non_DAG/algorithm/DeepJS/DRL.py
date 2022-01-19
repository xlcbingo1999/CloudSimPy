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

    def __call__(self, cluster, clock, is_last_step=False):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        all_candidates = []
        candidate_task = None
        candidate_machine = None
        schedule_candidate_task_instance = None

        # 这里其实就是慢的根源，每次都要将所有的machine和task做笛卡尔乘积。可以做一些加速
        for machine in machines:
            # 当machine的资源所有资源都降低到0的时候，应该可以提前终止，不过感觉优化的速率不会特别高
            for task in tasks:
                if machine.accommodate(task):
                    all_candidates.append((machine, task, task.waiting_task_instances[0]))
        operator_index = SchedulerOperation.SILENCE
        if len(all_candidates) == 0:
            self.current_trajectory.append(Node(None, None, self.reward_giver.get_reward(), clock))
            operator_index = SchedulerOperation.OVER_SCHEDULER
        else:
            # 这里问题是: 为什么每次都只是传入state的局部观察observation，而不是整个state? 用于压缩空间? 
            features = self.extract_features(all_candidates)
            features = tf.convert_to_tensor(features, dtype=np.float32)
            debugPrinter(__file__, sys._getframe(), "所有候选集构成的维度: {0}".format(features.get_shape().as_list()))
            # 注意: 这里每个迭代中，会有多个Episode，每个Episode得到的结果是不一样的
            # 强化学习策略函数的返回结果，选择某个index的概率，使用概率的原因是为了支持探索。这是离散化策略学习的正常返回结果。
            logits = self.agent.brain(features)
            debugPrinter(__file__, sys._getframe(), "经过Brain后得到结果: {0}".format(logits))
            # 这里是根据logits的概率，采样index结果，之后删除维度为1的dim，转化为numpy数组后返回第一个index
            pair_index = tf.squeeze(tf.multinomial(logits, num_samples=1), axis=1).numpy()[0]
            

            node = Node(features, pair_index, 0, clock) # 四元组, 用于经验回放
            self.current_trajectory.append(node)
            operator_index = SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN

            candidate_machine = all_candidates[pair_index][0]
            candidate_task = all_candidates[pair_index][1]
            schedule_candidate_task_instance = all_candidates[pair_index][2]

            debugPrinter(__file__, sys._getframe(), "Action: (machine: {0}; task: {1})".format(candidate_machine.id, candidate_task.task_index))
        return operator_index, candidate_machine, candidate_task, schedule_candidate_task_instance
