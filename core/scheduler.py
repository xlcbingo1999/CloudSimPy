import sys
from playground.Non_DAG.utils.tools import debugPrinter
from enum import Enum

class SchedulerOperation(Enum):
    TASK_INSTANCE_SCHEDULER_IN = 0
    TASK_INSTANCE_SCHEDULER_OUT = 1
    SILENCE = 2
    OVER_SCHEDULER = 3

class Scheduler(object):
    def __init__(self, env, algorithm):
        self.env = env
        self.algorithm = algorithm
        self.simulation = None
        self.cluster = None
        self.destroyed = False
        self.valid_pairs = {}

    def attach(self, simulation):
        self.simulation = simulation
        self.cluster = simulation.cluster

    def make_decision(self):
        # 这个函数的作用边界是: 执行放置和取消放置，不应该和调度算法耦合！
        while True:
            # 返回值: operatorIndex, candidate_machine, candidate_task, candidate_task_instance
            # operatorIndex: 0 - 调度instance到新机器上去; 1 - 将instance从机器上抢占出来; 2 - 静默状态; 3 - 结束状态
            operatorIndex, machine, task, task_instance = self.algorithm(self.cluster, self.env.now)
            if operatorIndex == SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:0 调度执行 taskInstanceId-machineId: {1}-{2}".format(self.env.now, task_instance.id, machine.id))
                task.start_task_instance(machine, task_instance)
            elif operatorIndex == SchedulerOperation.TASK_INSTANCE_SCHEDULER_OUT:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:1 卸载任务 taskInstanceId: {1}".format(self.env.now, task_instance.id))
                task.pause_task_instance(task_instance)
            elif operatorIndex == SchedulerOperation.SILENCE:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:2 静默状态 执行算法内调度等操作".format(self.env.now))
            elif operatorIndex == SchedulerOperation.OVER_SCHEDULER:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:3 结束该时刻的调度状态".format(self.env.now))
                break
            else:
                raise RuntimeError("xiaolinchang: 返回值错误: {0} 目标operatorIndex: 0 - 调度instance到新机器上去; 1 - 将instance从机器上抢占出来; 2 - 什么都不干".format(operatorIndex))


    def run(self):
        while not self.simulation.finished:
            self.make_decision()
            yield self.env.timeout(1)
        self.destroyed = True
