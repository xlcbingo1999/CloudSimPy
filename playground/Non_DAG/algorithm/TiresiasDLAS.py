from core.alogrithm import Algorithm
from core.scheduler import SchedulerOperation

class TiresiasDLASAlgorithm(Algorithm):
    def __init__(self, solve_starvation=None):
        super().__init__()
        self.queues_num = 4
        self.queues = [list() for i in range(self.queues_num)]
        self.queue_limit = [40, 80, 120] # 多级反馈队列的限制
        
        self.last_clock = None
        self.update_pri_operator_finished = False

        self.solve_starvation = solve_starvation

    def __call__(self, cluster, clock):
        # 每个clock会执行一次算法
        if self.last_clock is None or self.last_clock != clock:
            self.update_pri_operator_finished = False
        self.last_clock = clock
        # 返回值: operatorIndex, candidate_machine, candidate_task, candidate_task_instance
        # operatorIndex: 0 - 调度instance到新机器上去; 1 - 将instance从机器上抢占出来; 2 - 静默状态; 3 - 结束状态
        machines = cluster.machines # 总机器
        tasks = cluster.tasks_which_has_waiting_instance # 等待队列

        candidate_machine = None
        candidate_task = None
        candidate_task_instance = None

        # 1 遍历所有队列, 删除finished instance, 减少数量级
        for q in self.queues:
            for instance in q:
                if instance.finished is True:
                    instance.queue_index = None
            q = [instance for instance in q if instance.finished is False]


        # 2 修改原有工作的优先级，此步骤和机器无关，用一个标记可以避免多次重复执行
        if self.update_pri_operator_finished is False:
            for index in range(self.queues_num):
                if self.solve_starvation is not None and index == self.queues_num - 1: # 必须设置超参数才会有饥饿处理
                    first_hungry_instance = next((instance for instance in self.queues[index] if instance.started is False and instance.paused is True and instance.last_pending_time_length >= self.history_activated_time_length * self.solve_starvation), None)
                    if first_hungry_instance is not None:
                        first_hungry_instance.queue_index = 0
                        self.queues[index].remove(first_hungry_instance)
                        self.queues[0].append(first_hungry_instance)
                        # 返回直接执行算法, machine: None
                        return SchedulerOperation.SILENCE, first_hungry_instance.machine, first_hungry_instance.task, first_hungry_instance
                    else:
                        self.update_pri_operator_finished = True
                else:
                    # 将执行时间过长的instance降级到queue[index + 1]
                    first_above_limit_instances = next((instance for instance in self.queues[index] if instance.started is True and instance.paused is False and instance.last_active_time_length >= self.queue_limit[index]), None)
                    if first_above_limit_instances is not None:
                        first_above_limit_instances.queue_index = index + 1
                        self.queues[index].remove(first_above_limit_instances)
                        self.queues[index + 1].append(first_above_limit_instances)
                        
                        # 返回直接执行算法
                        return SchedulerOperation.TASK_INSTANCE_SCHEDULER_OUT, first_above_limit_instances.machine, first_above_limit_instances.task, first_above_limit_instances 
        
        # 3 新来的任务直接加入q[0]中
        for task in tasks:
            for instance in task.task_instances:
                if instance.queue_index is None:
                    instance.queue_index = 0
                    self.queues[0].append(instance)
        
        # 4 依次遍历queues，分配资源
        for machine in machines:
            for q in self.queues:
                for instance in q:
                    if instance.started is False and instance.paused is True and instance.finished is False and machine.accommodate(instance.task):
                        candidate_machine = machine
                        candidate_task = instance.task
                        candidate_task_instance = instance
                        return SchedulerOperation.TASK_INSTANCE_SCHEDULER_IN, candidate_machine, candidate_task, candidate_task_instance
        
        # 5 结束标识，后面三个全部为None
        return SchedulerOperation.OVER_SCHEDULER, candidate_machine, candidate_task, candidate_task_instance