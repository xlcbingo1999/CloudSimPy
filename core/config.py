class TaskInstanceConfig(object):
    def __init__(self, task_config):
        self.cpu = task_config.cpu
        self.memory = task_config.memory
        self.disk = task_config.disk
        self.duration = task_config.duration


class TaskConfig(object):
    def __init__(self, task_index, instances_number, cpu, memory, disk, duration, parent_indices=None):
        self.task_index = task_index
        self.instances_number = instances_number
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.duration = duration
        self.parent_indices = parent_indices

    def printState(self):
        return "[检查task]: task_index: " + str(self.task_index) + " duration: " + str(self.duration) +  " cpu: " +  str(self.cpu) + " memory: " + str(self.memory)


class JobConfig(object):
    def __init__(self, idx, submit_time, task_configs):
        self.submit_time = submit_time
        self.task_configs = task_configs
        self.id = idx

    def printState(self):
        return "[检查job]: job_id: " + str(self.id) + " 当前job提交时间: " + str(self.submit_time) +  " taskConfig:" +  str(self.printTasksDetail())

    def printTasksDetail(self):
        res = "\n"
        for task in self.task_configs:
            res += ("\t" + task.printState() + "\n")
        return res