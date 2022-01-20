from core.job import Job
from core.machine import MachineConfig
import sys
from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter
import time
from tqdm import tqdm, trange

class JobBroker(object):
    job_cls = Job

    def __init__(self, env, job_configs):
        self.env = env
        self.simulation = None
        self.cluster = None
        self.destroyed = False
        self.job_configs = job_configs

    def attach(self, simulation):
        self.simulation = simulation
        self.cluster = simulation.cluster

    def run(self):
        for i in tqdm(range(len(self.job_configs))):
            job_config = self.job_configs[i]
            assert job_config.submit_time >= self.env.now
            yield self.env.timeout(job_config.submit_time - self.env.now)
            infoPrinter(__file__, sys._getframe(),"xiaolinchang用户提交任务: 当前时间: " + str(self.env.now) + str(job_config.printState()) + "\n\n")
            job = JobBroker.job_cls(self.env, job_config)
            # print('a task arrived at time %f' % self.env.now)
            self.cluster.add_job(job)
        self.destroyed = True

class MachineBroker(object):
    def __init__(self, env, machine_action_configs):
        self.env = env
        self.destroyed = False
        self.simulation = None
        self.cluster = None
        self.machine_action_configs = machine_action_configs

    def attach(self, simulation):
        self.simulation = simulation
        self.cluster = simulation.cluster

    def initMachineActionRun(self):
        assert self.cluster is not None 
        for machine_action_config in self.machine_action_configs:
            if machine_action_config.submite_time < 0 and machine_action_config.operation == 'init_m':
                infoPrinter(__file__, sys._getframe(), "当前时间: {0} 初始化集群 action: {1}".format(self.env.now, machine_action_config.state))
                machine_config = MachineConfig(machine_action_config)
                self.cluster.add_machines([machine_config])

    def run(self):
        for i in tqdm(range(len(self.machine_action_configs))):
            machine_action_config = self.machine_action_configs[i]
            if machine_action_config.operation == 'init_m':
                continue
            assert machine_action_config.submite_time >= self.env.now
            yield self.env.timeout(machine_action_config.submite_time - self.env.now)
            assert self.cluster is not None
            infoPrinter(__file__, sys._getframe(), "当前时间: {0} 检查修改machine状态 action: {1}".format(self.env.now, machine_action_config.state))
            
            if machine_action_config.operation == 'add_m':
                machine_config = MachineConfig(machine_action_config)
                self.cluster.add_machines([machine_config])
            elif machine_action_config.operation == 'remove_m':
                self.cluster.remove_machine(machine_action_config.machine_id)
            elif machine_action_config.operation == 'add_resource_m':
                self.cluster.add_machine_resource(machine_action_config)
            elif machine_action_config.operation == 'remove_resource_m':
                self.cluster.remove_machine_resource(machine_action_config)
            elif machine_action_config.operation == 'init_m':
                continue
            else:
                raise RuntimeError("当前动作错误: {0}".format(machine_action_config.operation))
            debugPrinter(__file__, sys._getframe(), "当前时间: {0} 检查集群状态: {1}".format(self.env.now, self.cluster.state))
        self.destroyed = True