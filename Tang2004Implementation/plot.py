import numpy as np
import matplotlib.pyplot as plt
with open('exceeds.npy', 'rb') as outfile:
    exceeds = np.load(outfile)
    
plt.figure(figsize = (15, 15))
plt.plot(np.log10([10, 100, 1000, 10000, 100000, 200000, 1000000]), exceeds)
plt.xlabel('Penalty')
plt.ylabel('Exceed probabilty')
plt.savefig('exceeds.png', dpi=300)
