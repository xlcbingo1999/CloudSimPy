from core.alogrithm import Algorithm
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class FirstFitAlgorithm(Algorithm):
    def __call__(self, cluster, clock):
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
        if candidate_machine != None and candidate_task != None and schedule_candidate_task_instance != None:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.waiting_task_instances_number) for task in tasks], candidate_machine.id, schedule_candidate_task_instance.task.task_index))
        else:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.waiting_task_instances_number) for task in tasks], candidate_machine, schedule_candidate_task_instance))
        return candidate_machine, candidate_task, schedule_candidate_task_instance
