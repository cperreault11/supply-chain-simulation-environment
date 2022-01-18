import csv
from IPython import embed
import numpy as np
import matplotlib.pyplot as plt

matrix = np.zeros((10,10))
matrix -= 1

renewables_axis = np.array([3, 4, 5, 6, 7, 8]) * 3
renewables_axis = list(map(str, renewables_axis))
renewables_axis = list(map(lambda x: x + " GW", renewables_axis))

storage_axis = [ "0 GWh",  "2 GWh",  "4 GWh",  "6 GWh",  "8 GWh", "10 GWh", "12 GWh", "14 GWh"]


with open('shortages.csv', newline='') as csvfile:
    rows = []

    

    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        storage_index = int(int(row[2]) / 2000000) 
        baseline_index = int((int(row[1]) - 500000) / 0.4 / 7000000) - 3
        val = int(row[0])

        matrix[storage_index, baseline_index] = val 


    fig, ax = plt.subplots()
    im = ax.imshow(matrix[0:8,0:6], cmap='viridis', interpolation='nearest')
    
    

    ax.set_xticks(np.arange(len(renewables_axis)), labels=renewables_axis)
    ax.set_yticks(np.arange(len(storage_axis)), labels=storage_axis)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")


    for i in range(8):
        for j in range(6):
            text = ax.text(j, i, matrix[i, j],
                        ha="center", va="center", color="w")


    fig.tight_layout()
    plt.show()