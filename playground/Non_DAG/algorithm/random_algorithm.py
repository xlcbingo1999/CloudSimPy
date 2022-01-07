import numpy as np
from core.alogrithm import Algorithm
from core.scheduler import SchedulerOperation

class RandomAlgorithm(Algorithm):
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def __call__(self, cluster, clock):
        machines = cluster.machines
        tasks = cluster.tasks_which_has_waiting_instance
        candidate_task = None
        candidate_machine = None
        schedule_candidate_task_instance = None
        all_candidates = []

        for machine in machines:
            for task in tasks:
                if machine.accommodate(task):
                    candi_instance = task.waiting_task_instances[0]
                    all_candidates.append((machine, task, candi_instance))
                    if np.random.rand() > self.threshold:
                        candidate_machine = machine
                        candidate_task = task
                        schedule_candidate_task_instance = candi_instance
                        break
        if len(all_candidates) == 0:
            return SchedulerOperation.OVER_SCHEDULER, None, None, None
        if candidate_task is None:
            pair_index = np.random.randint(0, len(all_candidates))
            return SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN, all_candidates[pair_index][0], all_candidates[pair_index][1], all_candidates[pair_index][2]
        else:
            if candidate_machine != None and candidate_task != None and schedule_candidate_task_instance != None:
                return SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN, candidate_machine, candidate_task, schedule_candidate_task_instance
            else:
                return SchedulerOperation.OVER_SCHEDULER, candidate_machine, candidate_task, schedule_candidate_task_instance
