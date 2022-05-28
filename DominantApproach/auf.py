import pickle 
import numpy as np

with open('times_distribution_3.pkl', 'rb') as f:
	a = pickle.load(f)
	
with open('19_times_3.pkl', 'rb') as f:
	b = pickle.load(f)
	
print(a)
print('---------------------------')
print(b)