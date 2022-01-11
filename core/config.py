class TaskInstanceConfig(object):
    def __init__(self, task_config):
        self.cpu = task_config.cpu
        self.memory = task_config.memory
        self.disk = task_config.disk
        self.gpu = task_config.gpu
        self.gpu_memory = task_config.gpu_memory 
        self.duration = task_config.duration
        self.submit_time = task_config.submit_time
        self.gpu_type_require = task_config.gpu_type_require


class TaskConfig(object):
    def __init__(self, task_index, instances_number, cpu, memory, disk, gpu, gpu_memory, duration, submit_time, gpu_type_require,parent_indices=None):
        self.task_index = task_index
        self.instances_number = instances_number
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.gpu = gpu
        self.gpu_memory = gpu_memory 
        self.duration = duration
        self.submit_time = submit_time
        self.gpu_type_require = gpu_type_require
        self.parent_indices = parent_indices

    def printState(self):
        checkPrefix = "[检查task]: "
        taskIndexStr = "task_index: " + str(self.task_index) + '; '
        durationStr = "duration: " + str(self.duration) + '; '
        cpuStr = "cpu: " +  str(self.cpu) + '; '
        cpuMemoryStr = "memory: " + str(self.memory) + '; '
        gpuStr = "gpu: " + str(self.gpu) + '; '
        gpuMemoryStr = "gpu_memory: " + str(self.gpu_memory) + '; '
        submitTimeStr = "submit_time: " + str(self.submit_time) + '; '
        gpuTypeRequireStr = 'gpu_type_require: ' + str(self.gpu_type_require.name) + ' with id: ' + str(self.gpu_type_require.value) + '; '
        return checkPrefix + taskIndexStr + durationStr + cpuStr + cpuMemoryStr + gpuStr + gpuMemoryStr + submitTimeStr + gpuTypeRequireStr


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