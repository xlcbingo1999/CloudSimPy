import numpy as np
from core.alogrithm import Algorithm
from core.scheduler import SchedulerOperation

class Tetris(Algorithm):
    @staticmethod
    def calculate_alignment(valid_pairs):
        machine_features = []
        task_features = []
        for index, pair in enumerate(valid_pairs):
            machine = pair[0]
            task = pair[1]
            machine_features.append(machine.feature[:4])
            task_features.append([task.task_config.cpu, task.task_config.memory, task.task_config.gpu, task.task_config.gpu_memory])
        return np.argmax(np.sum(np.array(machine_features) * np.array(task_features), axis=1), axis=0)

    def __call__(self, cluster, clock, is_last_step=False):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        valid_pairs = []
        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    valid_pairs.append((machine, task, task.waiting_task_instances[0]))
        if len(valid_pairs) == 0:
            return SchedulerOperation.OVER_SCHEDULER, None, None, None
        pair_index = Tetris.calculate_alignment(valid_pairs)
        pair = valid_pairs[pair_index]
        operator_index = SchedulerOperation.SILENCE
        if pair[0] != None and pair[1] != None and pair[2] != None:
            operator_index = SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN
        else:
            operator_index = SchedulerOperation.OVER_SCHEDULER
        return operator_index, pair[0], pair[1], pair[2]
