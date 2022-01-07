from core.machine import Machine

class Cluster(object):
    def __init__(self):
        self.machines = []
        self.jobs = []

    @property
    def unfinished_jobs(self):
        ls = []
        for job in self.jobs:
            if not job.finished:
                ls.append(job)
        return ls

    @property
    def unfinished_tasks(self):
        ls = []
        for job in self.jobs:
            ls.extend(job.unfinished_tasks)
        return ls

    @property
    def ready_unfinished_tasks(self):
        ls = []
        for job in self.jobs:
            ls.extend(job.ready_unfinished_tasks)
        return ls

    @property
    def tasks_which_has_waiting_instance(self):
        ls = []
        for job in self.jobs:
            ls.extend(job.tasks_which_has_waiting_instance)
        return ls

    @property
    def ready_tasks_which_has_waiting_instance(self):
        ls = []
        for job in self.jobs:
            ls.extend(job.ready_tasks_which_has_waiting_instance)
        return ls

    @property
    def finished_jobs(self):
        ls = []
        for job in self.jobs:
            if job.finished:
                ls.append(job)
        return ls

    @property
    def finished_tasks(self):
        ls = []
        for job in self.jobs:
            ls.extend(job.finished_tasks)
        return ls

    @property
    def running_task_instances(self):
        task_instances = []
        for machine in self.machines:
            task_instances.extend(machine.running_task_instances)
        return task_instances

    def target_machine(self, machine_id):
        machine = next((machine for machine in self.machines if machine.id == machine_id), None)
        return machine

    def add_machines(self, machine_configs):
        for machine_config in machine_configs:
            assert self.target_machine(machine_config.id) is None
            machine = Machine(machine_config)
            self.machines.append(machine)
            machine.attach(self)
    
    def remove_machine(self, machine_id):
        rem_target_machine = self.target_machine(machine_id)
        assert rem_target_machine is not None
        for instance in rem_target_machine.task_instances:
            if instance.started and not instance.finished and not instance.paused:
                instance.interruptstop()
            else:
                raise RuntimeError("当前动作错误: {0}".format(instance.info))
        rem_target_machine.dis_attach()
        self.machines = [machine for machine in self.machines if machine.id != machine_id]

    def add_machine_resource(self, machine_action_config):
        add_target_machine = self.target_machine(machine_action_config.machine_id)
        assert add_target_machine is not None
        add_target_machine.add_resource(machine_action_config.cpu_capacity, 
                                        machine_action_config.memory_capacity, 
                                        machine_action_config.disk_capacity, 
                                        machine_action_config.gpu_capacity, 
                                        machine_action_config.gpu_memory_capacity)

    def remove_machine_resource(self, machine_action_config):
        remove_target_machine = self.target_machine(machine_action_config.machine_id)
        assert remove_target_machine is not None
        for instance in remove_target_machine.task_instances:
            if instance.started and not instance.finished and not instance.paused:
                instance.interruptstop()
            else:
                raise RuntimeError("当前动作错误: {0}".format(instance.info))
        # 必须先置判断，绝对不可以后置判断，不然会有除以0现象发生
        if (
            remove_target_machine.cpu_capacity == machine_action_config.cpu_capacity
            and remove_target_machine.memory_capacity == machine_action_config.memory_capacity
            and remove_target_machine.disk_capacity == machine_action_config.disk_capacity
            and remove_target_machine.gpu_capacity == machine_action_config.gpu_capacity
            and remove_target_machine.gpu_memory_capacity == machine_action_config.gpu_memory_capacity
        ):
            self.remove_machine(remove_target_machine.id)
            return
        if (
            remove_target_machine.cpu_capacity < machine_action_config.cpu_capacity
            or remove_target_machine.memory_capacity < machine_action_config.memory_capacity
            or remove_target_machine.disk_capacity < machine_action_config.disk_capacity
            or remove_target_machine.gpu_capacity < machine_action_config.gpu_capacity
            or remove_target_machine.gpu_memory_capacity < machine_action_config.gpu_memory_capacity
        ):
            raise RuntimeError("当前机器状态错误: {0}".format(remove_target_machine.state))
        remove_target_machine.remove_resource(machine_action_config.cpu_capacity, 
                                            machine_action_config.memory_capacity, 
                                            machine_action_config.disk_capacity, 
                                            machine_action_config.gpu_capacity, 
                                            machine_action_config.gpu_memory_capacity)


    def add_job(self, job):
        self.jobs.append(job)

    @property
    def cpu(self):
        return sum([machine.cpu for machine in self.machines])

    @property
    def memory(self):
        return sum([machine.memory for machine in self.machines])

    @property
    def disk(self):
        return sum([machine.disk for machine in self.machines])

    @property
    def gpu(self):
        return sum([machine.gpu for machine in self.machines])

    @property
    def gpu_memory(self):
        return sum([machine.gpu_memory for machine in self.machines])

    @property
    def cpu_capacity(self):
        return sum([machine.cpu_capacity for machine in self.machines])

    @property
    def memory_capacity(self):
        return sum([machine.memory_capacity for machine in self.machines])

    @property
    def disk_capacity(self):
        return sum([machine.disk_capacity for machine in self.machines])

    @property
    def gpu_capacity(self):
        return sum([machine.gpu_capacity for machine in self.machines])

    @property
    def gpu_memory_capacity(self):
        return sum([machine.gpu_memory_capacity for machine in self.machines])

    @property
    def state(self):
        return {
            'arrived_jobs': len(self.jobs),
            'unfinished_jobs': len(self.unfinished_jobs),
            'finished_jobs': len(self.finished_jobs),
            'unfinished_tasks': len(self.unfinished_tasks),
            'finished_tasks': len(self.finished_tasks),
            'running_task_instances': len(self.running_task_instances),
            'machine_states': [machine.state for machine in self.machines],
            'cpu': self.cpu / self.cpu_capacity,
            'memory': self.memory / self.memory_capacity,
            'disk': self.disk / self.disk_capacity,
            'gpu': self.gpu / self.gpu_capacity,
            'gpu_memory': self.gpu_memory / self.gpu_memory_capacity,
        }
