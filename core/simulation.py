from core.monitor import Monitor


class Simulation(object):
    def __init__(self, env, cluster, task_broker, machine_broker, scheduler, event_file):
        self.env = env
        self.cluster = cluster
        self.task_broker = task_broker
        self.machine_broker = machine_broker
        self.scheduler = scheduler
        self.event_file = event_file
        if event_file is not None:
            self.monitor = Monitor(self)

        self.task_broker.attach(self)
        self.machine_broker.attach(self)
        self.scheduler.attach(self)

    def run(self):
        # Starting monitor process before task_broker process
        # and scheduler process is necessary for log records integrity.
        self.machine_broker.initMachineActionRun()
        if self.event_file is not None:
            self.env.process(self.monitor.run())
        self.env.process(self.machine_broker.run())
        self.env.process(self.task_broker.run())
        self.env.process(self.scheduler.run())

    @property
    def finished(self):
        return self.task_broker.destroyed \
               and self.machine_broker.destroyed \
               and len(self.cluster.unfinished_jobs) == 0
