import numpy as np


def features_extract_normalize_func(task, machine):
    # 原来: 4维数组: [task.task_config.cpu, task.task_config.memory, task.task_config.duration, task.waiting_task_instances_number]
    # 原来: 7维数组: [task.task_config.cpu, task.task_config.memory, task.task_config.disk,
    #               task.task_config.gpu, task.task_config.gpu_memory, task.task_config.gpu_type_require, 
    #               task.waiting_task_instances_number]
    # 这里对machine去预先的归一化，毕竟是已经预先可知满足条件的了
    # 这里的duration和waiting_task_instances_number需要对整个集群中当前还在等待中的所有task进行平均归一化
    # 之前的做法有问题: 为什么可以直接把duration放下去...
    normal_cpu = (task.task_config.cpu / machine.cpu_capacity) if machine.cpu_capacity > 0 else 1.0
    normal_memory = (task.task_config.memory / machine.memory_capacity) if machine.memory_capacity > 0 else 1.0
    normal_disk = (task.task_config.disk / machine.disk_capacity) if machine.disk_capacity > 0 else 1.0
    normal_gpu = (task.task_config.gpu / machine.gpu_capacity) if machine.gpu_capacity > 0 else 1.0
    normal_gpu_memory = (task.task_config.gpu_memory / machine.gpu_memory_capacity) if machine.gpu_memory_capacity > 0 else 1.0
    normal_waiting_instances_count = (len(task.waiting_task_instances) / len(task.task_instances))

    return [
        normal_cpu, normal_memory, normal_disk, 
        normal_gpu, normal_gpu_memory,task.task_config.gpu_type_require.value,
        normal_waiting_instances_count
    ]


def features_extract_func_ac(task):
    # 原来: 7维数组 = 4 + 3
    # 现在: 11维数组 = 7 + 3
    # TODO(gpu): 未修改
    return features_extract_normalize_func(task) + [task.task_config.instances_number, len(task.running_task_instances),
                                          len(task.finished_task_instances)]

# def features_normalize_func(x):
#     # TODO(gpu): min-max归一化
#     # 原来: 5维数组
#     # 现在
#     # [machine.cpu, machine.memory, machine.disk, machine.gpu, machine.gpu_memory, machine.gpu_type]

#     # [task.task_config.cpu, task.task_config.memory, 
#     # task.task_config.gpu, task.task_config.gpu_memory, task.task_config.gpu_type_require, 
#     # task.task_config.duration, task.waiting_task_instances_number]
    
#     y = (np.array(x) - np.array([0, 0, 0.65, 0.009, 74.0, 80.3])) / np.array([64, 1, 0.23, 0.005, 108.0, 643.5])
#     return y


def features_normalize_func_ac(x):
    # TODO(gpu)
    # 原来: 9维数组
    y = (np.array(x) - np.array([0, 0, 0.65, 0.009, 74.0, 80.3, 80.3, 80.3, 80.3])) / np.array(
        [64, 1, 0.23, 0.005, 108.0, 643.5, 643.5, 643.5, 643.5])
    return y
