from enum import Enum
import operator
import sys
from playground.Non_DAG.utils.tools import debugPrinter

class MachineActionConfig(object):
    def __init__(self, submite_time, operation, machine_id, 
                 cpu_capacity, memory_capacity, disk_capacity, gpu_capacity, gpu_memory_capacity):
        self.submite_time = submite_time
        self.operation = operation
        self.machine_id = machine_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.disk_capacity = disk_capacity
        self.gpu_capacity = gpu_capacity
        self.gpu_memory_capacity = gpu_memory_capacity

    @property
    def state(self):
        prefix = '[检查MachineActionConfig]: '
        operationStr = 'operation: ' + str(self.operation) + '; '
        machineIdStr = 'machine_id: ' + str(self.machine_id) + '; '
        cpuStr =  'cpu: ' + str(self.cpu_capacity) + '; '
        memoryStr =  'memory: ' + str(self.memory_capacity) + '; '
        diskStr =  'disk: ' + str(self.disk_capacity) + '; '
        gpuStr =  'gpu: ' + str(self.gpu_capacity) + '; '
        gpuMemoryStr =  'gpu_memory: ' + str(self.gpu_memory_capacity) + '; '
        return prefix + operationStr + machineIdStr + cpuStr + memoryStr + diskStr + gpuStr + gpuMemoryStr



class MachineConfig(object):
    # idx = 0

    def __init__(self, hash_idx, cpu_capacity, memory_capacity, disk_capacity, gpu_capacity, gpu_memory_capacity, cpu=None, memory=None, disk=None, gpu=None, gpu_memory=None):
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.disk_capacity = disk_capacity
        self.gpu_capacity = gpu_capacity
        self.gpu_memory_capacity = gpu_memory_capacity

        self.cpu = cpu_capacity if cpu is None else cpu
        self.memory = memory_capacity if memory is None else memory
        self.disk = disk_capacity if disk is None else disk
        self.gpu = gpu_capacity if gpu is None else gpu
        self.gpu_memory = gpu_memory_capacity if gpu_memory is None else gpu_memory

        self.id = hash_idx
        # self.id = MachineConfig.idx
        # MachineConfig.idx += 1 # 每次新建一个对象都会增加一个id，这种方式还是尽量改掉吧

    def __init__(self, machine_action_config, cpu=None, memory=None, disk=None, gpu=None, gpu_memory=None):
        self.id = machine_action_config.machine_id
        self.cpu_capacity = machine_action_config.cpu_capacity
        self.memory_capacity = machine_action_config.memory_capacity
        self.disk_capacity = machine_action_config.disk_capacity
        self.gpu_capacity = machine_action_config.gpu_capacity
        self.gpu_memory_capacity = machine_action_config.gpu_memory_capacity

        self.cpu = machine_action_config.cpu_capacity if cpu is None else cpu
        self.memory = machine_action_config.memory_capacity if memory is None else memory
        self.disk = machine_action_config.disk_capacity if disk is None else disk
        self.gpu = machine_action_config.gpu_capacity if gpu is None else gpu
        self.gpu_memory = machine_action_config.gpu_memory_capacity if gpu_memory is None else gpu_memory

class MachineDoor(Enum):
    TASK_IN = 0
    TASK_OUT = 1
    NULL = 3


class Machine(object):
    def __init__(self, machine_config):
        self.id = machine_config.id
        self.cpu_capacity = machine_config.cpu_capacity
        self.memory_capacity = machine_config.memory_capacity
        self.disk_capacity = machine_config.disk_capacity
        self.gpu_capacity = machine_config.gpu_capacity
        self.gpu_memory_capacity = machine_config.gpu_memory_capacity
        self.cpu = machine_config.cpu
        self.memory = machine_config.memory
        self.disk = machine_config.disk
        self.gpu = machine_config.gpu
        self.gpu_memory = machine_config.gpu_memory

        self.cluster = None
        self.task_instances = []
        self.machine_door = MachineDoor.NULL

    def run_task_instance(self, task_instance):
        self.cpu -= task_instance.cpu
        self.memory -= task_instance.memory
        self.disk -= task_instance.disk
        self.gpu -= task_instance.gpu
        self.gpu_memory -= task_instance.gpu_memory
        self.task_instances.append(task_instance)
        self.machine_door = MachineDoor.TASK_IN

    def stop_task_instance(self, task_instance):
        self.cpu += task_instance.cpu
        self.memory += task_instance.memory
        self.disk += task_instance.disk
        self.gpu += task_instance.gpu
        self.gpu_memory += task_instance.gpu_memory
        self.task_instances.remove(task_instance) 
        self.machine_door = MachineDoor.TASK_OUT

    def add_resource(self, cpu_capacity, memory_capacity, disk_capacity, gpu_capacity, gpu_memory_capacity):
        self.cpu_capacity += cpu_capacity
        self.memory_capacity += memory_capacity
        self.disk_capacity += disk_capacity
        self.gpu_capacity += gpu_capacity
        self.gpu_memory_capacity += gpu_memory_capacity

    def remove_resource(self, cpu_capacity, memory_capacity, disk_capacity, gpu_capacity, gpu_memory_capacity):
        self.cpu_capacity -= cpu_capacity
        self.memory_capacity -= memory_capacity
        self.disk_capacity -= disk_capacity
        self.gpu_capacity -= gpu_capacity
        self.gpu_memory_capacity -= gpu_memory_capacity

    @property
    def running_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.started and not task_instance.finished:
                ls.append(task_instance)
        return ls

    @property
    def finished_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.finished:
                ls.append(task_instance)
        return ls

    def attach(self, cluster):
        self.cluster = cluster
    
    def dis_attach(self):
        self.cluster = None

    def accommodate(self, task):
        return self.cpu >= task.task_config.cpu and \
               self.memory >= task.task_config.memory and \
               self.disk >= task.task_config.disk and \
               self.gpu >= task.task_config.gpu and \
               self.gpu_memory >= task.task_config.gpu_memory

    @property
    def feature(self):
        return [self.cpu, self.memory, self.disk, self.gpu, self.gpu_memory]

    @property
    def capacity(self):
        return [self.cpu_capacity, self.memory_capacity, self.disk_capacity, self.gpu_capacity, self.gpu_memory_capacity]

    @property
    def state(self):
        return {
            'id': self.id,
            'cpu_capacity': int(self.cpu_capacity),
            'memory_capacity': int(self.memory_capacity),
            'disk_capacity': int(self.disk_capacity),
            'gpu_capacity': int(self.gpu_capacity),
            'gpu_memory_capacity': int(self.gpu_memory_capacity),
            'cpu': self.cpu / self.cpu_capacity,
            'memory': self.memory / self.memory_capacity,
            'disk': self.disk / self.disk_capacity,
            'gpu': self.gpu / self.gpu_capacity,
            'gpu_memory': self.gpu_memory / self.gpu_memory_capacity,
            'running_task_instances': len(self.running_task_instances),
            'finished_task_instances': len(self.finished_task_instances)
        }

    def __eq__(self, other):
        return isinstance(other, Machine) and other.id == self.id
