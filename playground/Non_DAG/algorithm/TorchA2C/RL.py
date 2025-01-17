import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import sys
from playground.Non_DAG.utils.tools import debugPrinter
from core.scheduler import SchedulerOperation

class Node(object):
    def __init__(self, observation, action, reward, clock):
        self.observation = observation
        self.action = action
        self.reward = reward
        self.clock = clock

class RLAlgorithm(object):
    def __init__(self, agent, feature_size, features_extract_normalize_func, update_step_num, iter_num):
        super().__init__()
        self.agent = agent
        self.features_extract_normalize_func = features_extract_normalize_func
        self.feature_size = feature_size
        self.device = self.agent.device
        self.iter_num = iter_num

        self.entropy = 0
        self.current_step = 0
        self.update_step_num = update_step_num
        self.log_probs = []
        self.values    = []
        self.rewards   = []
        self.masks     = []

        # self.current_trajectory = [] # (state, action, reward, time)

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
        debugPrinter(__file__, sys._getframe(), "检查feature shape: {}".format(len(features)))
        return features

    def check_rl_var(self):
        debugPrinter(__file__, sys._getframe(), "current_step: {}; entropy: {}; log_probs: {}; values: {}; rewards: {}; masks: {}"
                    .format(self.current_step, self.entropy, len(self.log_probs), len(self.values), len(self.rewards), len(self.masks)))
    
    def reset_rl(self):
        self.entropy = 0
        self.log_probs = []
        self.values    = []
        self.rewards   = []
        self.masks     = []
        self.current_step = 0

    def compute_returns(self, next_value, rewards, masks, gamma): # 没问题
        R = next_value
        returns = []
        for step in reversed(range(len(rewards))):
            R = rewards[step] + gamma * R * masks[step]
            returns.insert(0, R)
        return returns


    def update_brain(self, all_candidates, clock):
        if self.current_step == self.update_step_num and len(all_candidates) > 0: # TODO: 只有在笛卡尔积结果不为空时，才会更新brain
            next_features = self.extract_features(all_candidates)
            next_features = torch.tensor(next_features, dtype=torch.float32).to(self.device)

            next_value = self.agent.brain.critic_network(next_features)
            final_returns = self.compute_returns(next_value, self.rewards, self.masks, self.agent.gamma)

            self.log_probs = torch.cat(self.log_probs)
            final_returns  = torch.cat(final_returns).detach()
            self.values    = torch.cat(self.values)

            advantage = final_returns - self.values

            actor_loss  = -(self.log_probs * advantage.detach()).mean() - 0.001 * self.entropy
            critic_loss = advantage.pow(2).mean()
            
            self.agent.log('actor_loss', actor_loss, clock * self.iter_num)
            self.agent.log('critic_loss', critic_loss, clock * self.iter_num)

            self.agent.actor_network_optimizer.zero_grad()
            actor_loss.backward(retain_graph=True) # 保留backward后的中间参数。
            self.agent.actor_network_optimizer.step()
            
            self.agent.value_network_optimizer.zero_grad()
            critic_loss.backward()
            self.agent.value_network_optimizer.step()

            self.reset_rl()


    def __call__(self, cluster, clock, is_last_step=False):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        all_candidates = []
        candidate_task = None
        candidate_machine = None
        schedule_candidate_task_instance = None
        
        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    all_candidates.append((machine, task, task.waiting_task_instances[0]))
        
        self.update_brain(all_candidates, clock)

        # TODO: 这里应该过滤掉没有任务存在时候的情况，此时不应该判定为集群资源不足，而是一种正常的逻辑?
        # TODO: 上面的这种情况下，按照我们对集群优化的理解，应该是需要执行减少集群资源节点的操作，所以这里是需要商榷的

        if len(all_candidates) == 0:
            reward = torch.FloatTensor([-1]).to(self.device) # TODO: 待设计
            sub1done = torch.FloatTensor([1 - is_last_step]).to(self.device)
            value = torch.FloatTensor([0]).to(self.device)
            log_prob = torch.FloatTensor([0]).to(self.device)
            entropy = 0
            
            operator_index = SchedulerOperation.OVER_SCHEDULER
        else:
            # 这里问题是: 为什么每次都只是传入state的局部观察observation，而不是整个state? 用于压缩空间? 
            features = self.extract_features(all_candidates)
            features = torch.tensor(features, dtype=torch.float32).to(self.device)
            debugPrinter(__file__, sys._getframe(), "所有候选集构成的维度: {0}".format(features.shape))

            dist = self.agent.brain.actor_network(features)
            action = dist.sample() # 采样Action，单值Tensor
            log_prob = dist.log_prob(action) # 策略目标函数 J(theta) ln Π(a|s; theta) = log p(a|Π^{theta}(s))
            entropy = dist.entropy().mean() # 计算熵的平均值，用于带熵正则的策略学习中
            reward = torch.FloatTensor([1]).to(self.device) # TODO: 待设计
            sub1done = torch.FloatTensor([1 - False]).to(self.device)

            value = self.agent.brain.critic_network(features)

            candidate_machine = all_candidates[action][0]
            candidate_task = all_candidates[action][1]
            schedule_candidate_task_instance = all_candidates[action][2]

            operator_index = SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN

            debugPrinter(__file__, sys._getframe(), "Action: (machine: {0}; task: {1})".format(candidate_machine.id, candidate_task.task_index))
        
        self.entropy += entropy
        self.log_probs.append(log_prob)
        self.values.append(value)
        self.rewards.append(reward)
        self.masks.append(sub1done)
        self.current_step += 1

        return operator_index, candidate_machine, candidate_task, schedule_candidate_task_instance