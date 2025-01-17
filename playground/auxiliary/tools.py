import time
import numpy as np
import tensorflow as tf


def average_completion(exp):
    completion_time = 0
    number_task = 0
    for job in exp.simulation.cluster.jobs:
        for task in job.tasks:
            number_task += 1
            # completion_time += (task.finished_timestamp - task.started_timestamp) # 这里有问题吧，计算的应该是job的提交时间
            completion_time += (task.finished_timestamp - task.task_config.submit_time)
    return completion_time / number_task


def average_slowdown(exp):
    slowdown = 0
    number_task = 0
    for job in exp.simulation.cluster.jobs:
        for task in job.tasks:
            number_task += 1
            # slowdown += (task.finished_timestamp - task.started_timestamp) / task.task_config.duration
            slowdown += (task.finished_timestamp - task.task_config.submit_time)
    return slowdown / number_task


def multiprocessing_run(episode, trajectories, makespans, average_completions, average_slowdowns):
    np.random.seed(int(time.time()))
    tf.random.set_random_seed(time.time())
    episode.run()
    trajectories.append(episode.simulation.scheduler.algorithm.current_trajectory)
    makespans.append(episode.simulation.env.now)
    # print(episode.simulation.env.now)
    average_completions.append(average_completion(episode))
    average_slowdowns.append(average_slowdown(episode))

def debugPrinter(file, lineno, data=None):
    """
    输出带有文件名和行号的调试信息
    :param file: 对应__file__变量
    :param lineno: 对应sys._getframe().f变量
    :param data: 需要输出的信息
    :return:
    """
    fileName = file.split('/')[-1]
    lineno = lineno.f_lineno

    print(f'[{fileName} {lineno}] {data}')
