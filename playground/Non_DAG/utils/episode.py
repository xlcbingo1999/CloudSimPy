import simpy
from core.cluster import Cluster
from core.scheduler import Scheduler
from core.broker import JobBroker, MachineBroker
from core.simulation import Simulation


class Episode(object):
    def __init__(self, machine_action_configs, task_configs, algorithm, event_file):
        self.env = simpy.Environment()
        cluster = Cluster()
        machine_broker = MachineBroker(self.env, machine_action_configs)

        task_broker = JobBroker(self.env, task_configs)

        scheduler = Scheduler(self.env, algorithm)

        self.simulation = Simulation(self.env, cluster, task_broker, machine_broker, scheduler, event_file)

    def run(self):
        self.simulation.run()
        self.env.run()
