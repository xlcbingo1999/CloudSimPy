from operator import attrgetter
import pandas as pd
import numpy as np

from core.job import JobConfig, TaskConfig
import sys
from playground.Non_DAG.utils.tools import debugPrinter
from core.machine import MachineActionConfig, MachineConfig

class CSVReader(object):
    def __init__(self, filename):
        self.filename = filename
        df = pd.read_csv(self.filename)

        df.task_id = df.task_id.astype(dtype=int)
        df.job_id = df.job_id.astype(dtype=int)
        df.instances_num = df.instances_num.astype(dtype=int)

        job_task_map = {}
        job_submit_time_map = {}
        for i in range(len(df)):
            series = df.iloc[i]
            job_id = series.job_id
            task_id = series.task_id

            cpu = series.cpu
            memory = series.memory
            disk = series.disk
            gpu = series.gpu
            gpu_memory = series.gpu_memory
            duration = series.duration
            submit_time = series.submit_time
            instances_num = series.instances_num
            gpu_type_require = series.gpu_type_require

            task_configs = job_task_map.setdefault(job_id, [])
            task_config = TaskConfig(task_id, instances_num, cpu, memory, disk, gpu, gpu_memory, duration, submit_time, gpu_type_require)
            task_configs.append(task_config)
            job_submit_time_map[job_id] = submit_time

        job_configs = []
        for job_id, task_configs in job_task_map.items():
            job_configs.append(JobConfig(job_id, job_submit_time_map[job_id], task_configs))
        job_configs.sort(key=attrgetter('submit_time'))

        self.job_configs = job_configs

    def generate(self, offset, number):
        number = number if offset + number < len(self.job_configs) else len(self.job_configs) - offset
        ret = self.job_configs[offset: offset + number]
        the_first_job_config = ret[0]
        submit_time_base = the_first_job_config.submit_time

        tasks_number = 0
        task_instances_numbers = []
        task_instances_durations = []
        task_instances_cpu = []
        task_instances_memory = []
        task_instances_gpu = []
        task_instances_gpu_memory = []
        for job_config in ret:
            job_config.submit_time -= submit_time_base
            tasks_number += len(job_config.task_configs)
            for task_config in job_config.task_configs:
                task_instances_numbers.append(task_config.instances_number)
                task_instances_durations.extend([task_config.duration] * int(task_config.instances_number))
                task_instances_cpu.extend([task_config.cpu] * int(task_config.instances_number))
                task_instances_memory.extend([task_config.memory] * int(task_config.instances_number))
                task_instances_gpu.extend([task_config.gpu] * int(task_config.instances_number))
                task_instances_gpu_memory.extend([task_config.gpu_memory] * int(task_config.instances_number))

        print('Jobs number: ', len(ret))
        print('Tasks number:', tasks_number)

        print('Task instances number mean: ', np.mean(task_instances_numbers))
        print('Task instances number std', np.std(task_instances_numbers))

        print('Task instances cpu mean: ', np.mean(task_instances_cpu))
        print('Task instances cpu std: ', np.std(task_instances_cpu))

        print('Task instances memory mean: ', np.mean(task_instances_memory))
        print('Task instances memory std: ', np.std(task_instances_memory))

        print('Task instances gpu mean: ', np.mean(task_instances_gpu))
        print('Task instances gpu std: ', np.std(task_instances_gpu))

        print('Task instances gpu_memory mean: ', np.mean(task_instances_gpu_memory))
        print('Task instances gpu_memory std: ', np.std(task_instances_gpu_memory))

        print('Task instances duration mean: ', np.mean(task_instances_durations))
        print('Task instances duration std: ', np.std(task_instances_durations))

        return ret

class MachineConfigReader(object):
    def __init__(self, filename):
        super().__init__()
        self.machine_action_configs = []

        self.filename = filename
        df = pd.read_csv(self.filename)        
        
        for i in range(len(df)):
            series = df.iloc[i]
            submite_time = series.submit_time
            operation = series.operation
            machine_id = series.machine_id
            cpu_capacity = series.cpu_capacity
            memory_capacity = series.memory_capacity
            disk_capacity = series.disk_capacity
            gpu_capacity = series.gpu_capacity
            gpu_memory_capacity = series.gpu_memory_capacity
            gpu_type = series.gpu_type
            
            machine_action_config = MachineActionConfig(submite_time, operation, machine_id, 
                                                        cpu_capacity, memory_capacity, disk_capacity, 
                                                        gpu_capacity, gpu_memory_capacity, gpu_type)
            self.machine_action_configs.append(machine_action_config)
        self.machine_action_configs.sort(key=lambda action: action.submite_time)

    @property
    def action_size(self):
        return len(self.machine_action_configs)

    def generate(self, offset, number):
        number = number if offset + number < len(self.machine_action_configs) else len(self.machine_action_configs) - offset
        ret = self.machine_action_configs[offset: offset + number]
        return ret