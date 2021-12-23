import numpy as np
from core.alogrithm import Algorithm
import sys
from playground.Non_DAG.utils.tools import debugPrinter


class Tetris(Algorithm):
    @staticmethod
    def calculate_alignment(valid_pairs):
        machine_features = []
        task_features = []
        for index, pair in enumerate(valid_pairs):
            machine = pair[0]
            task = pair[1]
            machine_features.append(machine.feature[:2])
            task_features.append([task.task_config.cpu, task.task_config.memory])
        return np.argmax(np.sum(np.array(machine_features) * np.array(task_features), axis=1), axis=0)

    def __call__(self, cluster, clock):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        valid_pairs = []
        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    valid_pairs.append((machine, task))
        if len(valid_pairs) == 0:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], None, None))
            return None, None
        pair_index = Tetris.calculate_alignment(valid_pairs)
        pair = valid_pairs[pair_index]
        if pair[0] != None and pair[1] != None:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], pair[0].id, pair[1].task_index))
        else:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], pair[0], pair[1]))
        return pair[0], pair[1]
