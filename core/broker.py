from core.job import Job
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class Broker(object):
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
        for job_config in self.job_configs:
            assert job_config.submit_time >= self.env.now
            debugPrinter(__file__, sys._getframe(),"xiaolinchang用户提交任务: 当前时间: " + str(self.env.now) + str(job_config.printState()) + "\n\n")
            yield self.env.timeout(job_config.submit_time - self.env.now)
            job = Broker.job_cls(self.env, job_config)
            # print('a task arrived at time %f' % self.env.now)
            self.cluster.add_job(job)
        self.destroyed = True
