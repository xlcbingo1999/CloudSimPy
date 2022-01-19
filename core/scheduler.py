import sys
from playground.Non_DAG.utils.tools import debugPrinter
from enum import Enum

class SchedulerOperation(Enum):
    TASK_INSTANCE_SCHEDULER_IN = 0 # 调度instance到新机器上去
    TASK_INSTANCE_SCHEDULER_OUT = 1 # 将instance从机器上抢占出来
    SILENCE = 2 # 静默状态
    CLUSTER_ADD_MACHINE = 3
    CLUSTER_REMOVE_MACHINE = 4
    OVER_SCHEDULER = -1 # 结束状态

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
        # 尽可能减少不必要的时间消耗，让效率提升
        current_last_step = self.simulation.is_end_broker
        # 这个函数的作用边界是: 执行放置和取消放置，不应该和调度算法耦合
        while True:
            operatorIndex, machine, task, task_instance = self.algorithm(self.cluster, self.env.now, current_last_step and self.simulation.finished)
            if operatorIndex == SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:TASK_INSTANCE_SCHEDULER_IN 调度执行 taskInstanceId-machineId: {1}-{2}".format(self.env.now, task_instance.id, machine.id))
                task.start_task_instance(machine, task_instance)
            elif operatorIndex == SchedulerOperation.TASK_INSTANCE_SCHEDULER_OUT:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:TASK_INSTANCE_SCHEDULER_OUT 卸载任务 taskInstanceId: {1}".format(self.env.now, task_instance.id))
                task.pause_task_instance(task_instance)
            elif operatorIndex == SchedulerOperation.SILENCE:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:SILENCE 静默状态 执行算法内调度等操作".format(self.env.now))
            elif operatorIndex == SchedulerOperation.CLUSTER_ADD_MACHINE:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:CLUSTER_ADD_MACHINE 增加机器".format(self.env.now))
                assert self.cluster is not None
            elif operatorIndex == SchedulerOperation.CLUSTER_REMOVE_MACHINE:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:CLUSTER_REMOVE_MACHINE 减少机器".format(self.env.now))
                assert self.cluster is not None
            elif operatorIndex == SchedulerOperation.OVER_SCHEDULER:
                debugPrinter(__file__, sys._getframe(), "当前时间: {0}: 算法准备返回operatorIndex:3 结束该时刻的调度状态".format(self.env.now))
                break
            else:
                raise RuntimeError("xiaolinchang: 返回值错误: {0} 目标operatorIndex: ".format(operatorIndex))


    def run(self):
        while not self.simulation.finished:
            self.make_decision()
            yield self.env.timeout(1)
        self.destroyed = True
