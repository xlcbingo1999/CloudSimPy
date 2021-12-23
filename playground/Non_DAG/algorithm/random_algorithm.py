import numpy as np
from core.alogrithm import Algorithm
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class RandomAlgorithm(Algorithm):
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def __call__(self, cluster, clock):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        candidate_task = None
        candidate_machine = None
        all_candidates = []

        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    all_candidates.append((machine, task))
                    if np.random.rand() > self.threshold:
                        candidate_machine = machine
                        candidate_task = task
                        break
        if len(all_candidates) == 0:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for _, task in all_candidates], None, None))
            return None, None
        if candidate_task is None:
            pair_index = np.random.randint(0, len(all_candidates))
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for _, task in all_candidates], all_candidates[pair_index][0].id, all_candidates[pair_index][1].task_index))
            return all_candidates[pair_index]
        else:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for _, task in all_candidates], candidate_machine.id, candidate_task.task_index))
            return candidate_machine, candidate_task
