import pickle
from copy import deepcopy
from time import time
from joblib import Parallel, delayed
import numpy as np

from config import read_TOPTW_file
from utils import normalize, check_cost, position_profit, position_cost

dir_name = 'c_r_rc_100_100'
filename = 'c109'

_, _, t_max = read_TOPTW_file(f'data/TOPTW/{dir_name}/{filename}.txt',
                              save_graph=f'data/TOPTW_PROCESSED/{dir_name}/graph_{filename}.txt',
                              save_times=f'data/TOPTW_PROCESSED/{dir_name}/times_{filename}.txt')

with open(f'data/TOPTW_PROCESSED/{dir_name}/graph_{filename}.txt', 'rb') as f:
    graph_config = pickle.load(f)
with open(f'data/TOPTW_PROCESSED/{dir_name}/times_{filename}.txt', 'rb') as f:
    times_config = pickle.load(f)
print(position_cost([63,  62,  74,  25,  15,  16,  93,  88,  2,  75,  21], times_config['times'], graph_config['points_coordinates']))
print(position_profit([63,  62,  74,  25,  15,  16,  93,  88,  2,  75,  21], graph_config['profits']))
