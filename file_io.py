import csv
import sys
import os
import datetime
import random

def read_data_csv(filename):
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append([float(s) for s in row])
    
    if len(data) != 2:
        print("corrupted csv file", file=sys.stderr)
    
    return data[0], data[1]


def save_data_csv(dir, x_data, y_data):
    if len(x_data) != len(y_data):
        print("Error when saving file! The dimensions of x_data and y_data are unequal", file=sys.stderr)
    
    filename = dir + "mock_run_" + str(datetime.datetime.now()) + ".csv"
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(x_data)
        writer.writerow(y_data)
        file.close()


def get_random_file(path): #grabs a random file from the directory set by path
    dir_list = os.listdir(path)
    return random.choice(dir_list)

