from core.alogrithm import Algorithm
from core.scheduler import SchedulerOperation

class DRF(Algorithm):
    def __call__(self, cluster, clock, is_last_step=False):
        machines = cluster.machines
        unfinished_tasks = cluster.unfinished_tasks
        candidate_task = None
        candidate_machine = None
        schedule_candidate_task_instance = None

        for machine in machines:
            for task in unfinished_tasks:
                if machine.accommodate(task):
                    candidate_machine = machine
                    candidate_task = task
                    schedule_candidate_task_instance = task.waiting_task_instances[0]
                    break
        operator_index = SchedulerOperation.SILENCE
        if candidate_machine != None and candidate_task != None and schedule_candidate_task_instance != None:
            operator_index = SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN
        else:
            operator_index = SchedulerOperation.OVER_SCHEDULER
        return operator_index, candidate_machine, candidate_task, schedule_candidate_task_instance
