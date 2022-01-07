from simpy import Interrupt
from core.config import *
import sys
from playground.Non_DAG.utils.tools import debugPrinter, infoPrinter

class Task(object):
    def __init__(self, env, job, task_config):
        self.env = env
        self.job = job
        self.task_index = task_config.task_index
        self.task_config = task_config
        self._ready = False
        self._parents = None

        # 注意，下面三个list中的TaskInstance是共享的，不要轻易delete
        # TODO(xiaolinchang): 更改成deepCopy版本
        self.task_instances = [] 
        task_instance_config = TaskInstanceConfig(task_config)
        for task_instance_index in range(int(self.task_config.instances_number)):
            tempInstance = TaskInstance(self.env, self, task_instance_index, task_instance_config)
            self.task_instances.append(tempInstance)

    @property
    def id(self):
        return str(self.job.id) + '-' + str(self.task_index)

    @property
    def parents(self):
        if self._parents is None:
            if self.task_config.parent_indices is None:
                raise ValueError("Task_config's parent_indices should not be None.")
            self._parents = []
            for parent_index in self.task_config.parent_indices:
                self._parents.append(self.job.tasks_map[parent_index])
        return self._parents

    @property
    def ready(self):
        if not self._ready:
            for p in self.parents:
                if not p.finished:
                    return False
            self._ready = True
        return self._ready

    @property
    def running_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.started and not task_instance.finished and not task_instance.paused:
                ls.append(task_instance)
        return ls

    @property
    def finished_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.finished:
                ls.append(task_instance)
        return ls
    
    @property
    def waiting_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if not task_instance.started and task_instance.paused and not task_instance.finished:
                ls.append(task_instance)
        return ls

    # the most heavy
    def start_task_instance(self, machine, instance):
        if instance in self.waiting_task_instances:
            instance.schedule(machine)

    def pause_task_instance(self, instance):
        if instance in self.running_task_instances:
            instance.interruptstop()

    @property
    def started(self):
        for task_instance in self.task_instances:
            if task_instance.started:
                return True
        return False

    @property
    def waiting_task_instances_number(self):
        return len(self.waiting_task_instances)

    @property
    def has_waiting_task_instances(self):
        return len(self.waiting_task_instances) > 0

    @property
    def finished(self):
        """
        A task is finished only if it has no waiting task instances and no running task instances.
        :return: bool
        """
        if self.has_waiting_task_instances:
            return False
        if len(self.running_task_instances) != 0:
            return False
        return True

    @property
    def finished_timestamp(self):
        if not self.finished:
            return None
        t = None
        for task_instance in self.task_instances:
            if (t is None) or (t < task_instance.finished_timestamp):
                t = task_instance.finished_timestamp
        return t


class Job(object):
    task_cls = Task

    def __init__(self, env, job_config):
        self.env = env
        self.job_config = job_config
        self.id = job_config.id

        self.tasks_map = {}
        for task_config in job_config.task_configs:
            task_index = task_config.task_index
            self.tasks_map[task_index] = Job.task_cls(env, self, task_config)

    @property
    def tasks(self):
        return self.tasks_map.values()

    @property
    def unfinished_tasks(self):
        ls = []
        for task in self.tasks:
            if not task.finished:
                ls.append(task)
        return ls

    @property
    def ready_unfinished_tasks(self):
        ls = []
        for task in self.tasks:
            if not task.finished and task.ready:
                ls.append(task)
        return ls

    @property
    def tasks_which_has_waiting_instance(self):
        ls = []
        for task in self.tasks:
            if task.has_waiting_task_instances:
                ls.append(task)
        return ls

    @property
    def ready_tasks_which_has_waiting_instance(self):
        ls = []
        for task in self.tasks:
            if task.has_waiting_task_instances and task.ready:
                ls.append(task)
        return ls

    @property
    def running_tasks(self):
        ls = []
        for task in self.tasks:
            if task.started and not task.finished:
                ls.append(task)
        return ls

    @property
    def finished_tasks(self):
        ls = []
        for task in self.tasks:
            if task.finished:
                ls.append(task)
        return ls

    @property
    def started(self):
        for task in self.tasks:
            if task.started:
                return True
        return False

    @property
    def finished(self):
        for task in self.tasks:
            if not task.finished:
                return False
        return True

    @property
    def finished_timestamp(self):
        if not self.finished:
            return None
        t = None
        for task in self.tasks:
            if (t is None) or (t < task.finished_timestamp):
                t = task.finished_timestamp
        return t


class TaskInstance(object):
    def __init__(self, env, task, task_instance_index, task_instance_config):
        self.env = env
        self.task = task
        self.task_instance_index = task_instance_index
        self.config = task_instance_config
        self.cpu = task_instance_config.cpu
        self.memory = task_instance_config.memory
        self.disk = task_instance_config.disk
        self.gpu = task_instance_config.gpu
        self.gpu_memory = task_instance_config.gpu_memory
        self.duration = task_instance_config.duration

        self.machine = None
        self.process = None
        self.new = True

        self.started = False
        self.paused = True
        self.finished = False

        self.first_started_timestamp = None
        self.last_started_timestamp = None # 只有调度上去才会开始计算，重新调度会更新
        self.last_checkpoint_timestamp = None
        self.finished_timestamp = None
        
        self.history_activated_time_length = 0 # 目前只会在结束和被抢占的时候更新，如果当前正在执行，则不会增加此项目

        self.preempt_count = 0
        self.resume_count = 0

        self.queue_index = None

    @property
    def id(self):
        return str(self.task.id) + '-' + str(self.task_instance_index)

    @property
    def activated_time_length(self):
        if self.started is True and self.paused is False and self.finished is False:
            return self.history_activated_time_length + self.last_active_time_length
        else:
            return self.history_activated_time_length

    @property
    def pending_time_length(self):
        # debugPrinter(__file__, sys._getframe(), "xiaolinchang: check {0}-{1}-{2}".format(self.env.now, self.last_started_timestamp, self.activated_time_length))
        if self.last_started_timestamp is None:
            return 0
        else:
            # TODO(xiaolinchang): 这里有点危险，基于的假设是job的所有tasks都在同一时刻到来，不断地进行向上检索
            return self.env.now - self.config.submit_time - self.activated_time_length

    @property
    def last_pending_time_length(self):
        # 只有当前是pending状态才能计算该值
        if self.paused is False or self.started is True or self.last_checkpoint_timestamp is None:
            raise RuntimeError('此时不处于paused状态 {0}'.format(self.info))
        else:
            return self.env.now - self.last_checkpoint_timestamp

    @property
    def last_active_time_length(self):
        if self.started is False or self.paused is True or self.finished is True or self.last_started_timestamp is None:
            raise RuntimeError('此时不处于started状态 {0}'.format(self.info))
        else:
            return self.env.now - self.last_started_timestamp

    @property
    def info(self):
        taskInstanceStr = 'jobID-taskID-instanceID: ' + self.id + '; '
        machineStr = 'machineID: ' + str(self.machine.id if self.machine is not None else 'None') + '; '
        startedStr = 'isStart: ' + str(self.started) + '; '
        pausedStr = 'isPaused: ' + str(self.paused) + '; '
        startTimeStr = 'last_started_timestamp: ' + str(self.last_started_timestamp if self.last_started_timestamp is not None else 'None') + '; '
        lastCheckTimeStr = 'last_checkpoint_timestamp: ' + str(self.last_checkpoint_timestamp if self.last_checkpoint_timestamp is not None else 'None') + '; '
        submitTimeStr = 'submit_time: ' + str(self.config.submit_time) + '; '
        activedTimeStr = 'activated_time_length: ' + str(self.activated_time_length) + '; '
        pendingTimeStr = 'pending_time_length: ' + str(self.pending_time_length) + '; '
        preemptCountStr = 'preempt_count: ' + str(self.preempt_count) + '; '
        resumeCountStr = 'resume_count: ' + str(self.resume_count) + '; '
        queueIndexStr = 'queue_index' + str(self.queue_index if self.queue_index is not None else 'None') + '; '
        return taskInstanceStr + machineStr + startedStr + pausedStr + startTimeStr + lastCheckTimeStr + submitTimeStr + activedTimeStr + pendingTimeStr + preemptCountStr + resumeCountStr + queueIndexStr

    def do_work(self):
        # self.cluster.waiting_tasks.remove(self)
        # self.cluster.running_tasks.append(self)
        # self.machine.run(self)
        # 增加一个抢占的设计
        beginTime = self.env.now
        currentWorkTime = 0
        isOK = False
        while not isOK:
            try:
                infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 执行self.env.timeout".format(self.env.now))
                yield self.env.timeout(self.duration - currentWorkTime) # 这里的设计天生不适合抢占设计...
                isOK = True
            except Interrupt as interrupt:
                cause = interrupt.cause
                currentWorkTime = self.env.now - beginTime
                infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 已经执行: {1}; 出现抢占测试: {2}".format(self.env.now, self.activated_time_length ,cause))
        self.history_activated_time_length = self.history_activated_time_length + self.last_active_time_length
        self.finished_timestamp = self.env.now

        self.machine.stop_task_instance(self)
        self.machine = None

        self.started = False
        self.paused = True
        self.finished = True
        infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 完成一个task_instance: {1}".format(self.env.now, self.info))

    def begin_work(self):
        try:
            infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 开启工作: {1}".format(self.env.now, self.info))
            yield self.env.timeout(self.duration - self.history_activated_time_length)
            self.finish_work()
        except Interrupt as interrupt:
            infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 任务{1}被抢占; 已经执行: {2}; 抢占原因: {3}".format(self.env.now, self.info, self.activated_time_length, interrupt.cause))
        
    def finish_work(self):
        self.history_activated_time_length = self.history_activated_time_length + self.last_active_time_length
        self.finished_timestamp = self.env.now

        self.machine.stop_task_instance(self)
        self.machine = None

        self.started = False
        self.paused = True
        self.finished = True
        infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 完成一个task_instance: {1}".format(self.env.now, self.info))


    def schedule(self, machine):
        # 该函数会重复调用
        self.machine = machine
        self.machine.run_task_instance(self)
        self.process = self.env.process(self.begin_work())

        self.last_started_timestamp = self.env.now
        if self.resume_count == 0:
            self.first_started_timestamp = self.env.now
        self.resume_count = self.resume_count + 1

        self.started = True
        self.paused = False
        infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 调度task的一个实例: {1}".format(self.env.now, self.info))

    def interruptstop(self):
        # 副作用损耗资源
        if (not self.started) or (self.paused) or (self.machine is None):
            raise RuntimeError("当前时间: {0}; 抢占task的一个实例: {1}; 不符合抢占状态".format(self.env.now, self.info))
        self.machine.stop_task_instance(self)
        self.machine = None 

        self.process.interrupt()

        self.history_activated_time_length = self.history_activated_time_length + self.last_active_time_length
        self.last_checkpoint_timestamp = self.env.now
        self.preempt_count = self.preempt_count + 1

        self.started = False
        self.paused = True
        infoPrinter(__file__, sys._getframe(), "当前时间: {0}; 抢占task的一个实例: {1}; 抢占成功".format(self.env.now, self.info))
        
        