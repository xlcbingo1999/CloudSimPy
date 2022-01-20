from core.alogrithm import Algorithm
from core.scheduler import SchedulerOperation

class FirstFitAlgorithm(Algorithm):
    def __call__(self, cluster, clock, is_last_step=False):
        machines = cluster.machines # 总机器
        tasks = cluster.tasks_which_has_waiting_instance # 等待队列
        candidate_task = None
        candidate_machine = None
        schedule_candidate_task_instance = None

        for machine in machines:
            for task in tasks:
                if machine.accommodate(task): # 是否满足task的需求
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
