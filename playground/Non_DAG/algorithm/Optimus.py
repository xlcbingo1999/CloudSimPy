from core.alogrithm import Algorithm
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class OptimusAlgorithm(Algorithm):
    # 还没改完，但是有问题，因为需要ps-worker架构的设计
    def __call__(self, cluster, clock, is_last_step=False):
        machines = cluster.machines # 总机器
        tasks = cluster.tasks_which_has_waiting_instance # 等待队列
        candidate_task = None
        candidate_machine = None

        for machine in machines:
            for task in tasks:
                if machine.accommodate(task): # 是否满足task的需求
                    candidate_machine = machine
                    candidate_task = task
                    break
        if candidate_machine != None and candidate_task != None:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], candidate_machine.id, candidate_task.task_index))
        else:
            debugPrinter(__file__, sys._getframe(), "当前时间: {0}; 等待队列: {1}; 候选机器和task: [{2}, {3}] ".format(clock, [(task.task_index, task.task_config.instances_number - task.next_instance_pointer) for task in tasks], candidate_machine, candidate_task))
        return candidate_machine, candidate_task
