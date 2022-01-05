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
            machine, task, task_instance = self.algorithm(self.cluster, self.env.now)
            if machine is None or task is None or task_instance is None:
                break
            else:
                # 这里需要传递非负数的index，用于启动和抢占instance
                task.start_task_instance(machine, task_instance)
                task.pause_task_instance(task_instance)
                task.start_task_instance(machine, task_instance)

    def run(self):
        while not self.simulation.finished:
            self.make_decision()
            yield self.env.timeout(1)
        self.destroyed = True
