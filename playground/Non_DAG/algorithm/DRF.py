from core.alogrithm import Algorithm


class DRF(Algorithm):
    def __call__(self, cluster, clock):
        machines = cluster.machines
        unfinished_tasks = cluster.unfinished_tasks
        candidate_task = None
        candidate_machine = None
        schedule_candidate_task_instance = None

        for machine in machines:
            for task in unfinished_tasks:
                if machine.accommodate(task):
                    candidate_machine = machine
                    candidate_task = task
                    schedule_candidate_task_instance = task.waiting_task_instances[0]
                    break
        operator_index = 3
        if candidate_machine != None and candidate_task != None and schedule_candidate_task_instance != None:
            operator_index = 0
        else:
            operator_index = 3
        return operator_index, candidate_machine, candidate_task, schedule_candidate_task_instance
