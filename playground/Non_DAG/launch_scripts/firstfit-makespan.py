import os
import time
import sys
sys.path.insert(0, '/home/linchangxiao/labInDiWu/CloudSimPy')

from playground.Non_DAG.algorithm.first_fit import FirstFitAlgorithm

from playground.Non_DAG.utils.csv_reader import CSVReader, MachineConfigReader
from playground.Non_DAG.utils.tools import average_completion, average_slowdown
from playground.Non_DAG.utils.episode import Episode

machine_config_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/machines.csv'
machine_action_config_csv_reader = MachineConfigReader(machine_config_csv)
machine_action_configs = machine_action_config_csv_reader.generate(0, machine_action_config_csv_reader.action_size)

jobs_len = 10
jobs_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/jobs.csv'
csv_reader = CSVReader(jobs_csv)
jobs_configs = csv_reader.generate(0, jobs_len)

tic = time.time()
timeArray = time.localtime(tic)
fileStr = time.strftime('%Y%m%d-%H%M%S')
file_name = 'firstfit-event-' + str(fileStr) + '.log'
events_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/launch_scripts/events/' + file_name
algorithm = FirstFitAlgorithm()
episode = Episode(machine_action_configs, jobs_configs, algorithm, events_csv)
episode.run()
print(episode.env.now, time.time() - tic, average_completion(episode), average_slowdown(episode))