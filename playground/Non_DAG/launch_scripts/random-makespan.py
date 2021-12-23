import os
import time
import sys
sys.path.insert(0, '/home/linchangxiao/labInDiWu/CloudSimPy')

from core.machine import MachineConfig
from playground.Non_DAG.algorithm.random_algorithm import RandomAlgorithm

from playground.Non_DAG.utils.csv_reader import CSVReader
from playground.Non_DAG.utils.feature_functions import features_extract_func, features_normalize_func
from playground.Non_DAG.utils.tools import average_completion, average_slowdown
from playground.Non_DAG.utils.episode import Episode

machines_number = 5
jobs_len = 10
jobs_csv = '/home/linchangxiao/labInDiWu/CloudSimPy/playground/Non_DAG/jobs_files/jobs.csv'


machine_configs = [MachineConfig(64, 1, 1) for i in range(machines_number)]
csv_reader = CSVReader(jobs_csv)
jobs_configs = csv_reader.generate(0, jobs_len)

tic = time.time()
algorithm = RandomAlgorithm()
episode = Episode(machine_configs, jobs_configs, algorithm, None)
episode.run()
print(episode.env.now, time.time() - tic, average_completion(episode), average_slowdown(episode))