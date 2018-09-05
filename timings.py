import  time
import numpy as np

times = {}
start_times = {}

def start(id):
    if not id in times:
        times[id] = []
    start_times[id] = time.time()

def end(id):
    times[id].append(time.time() - start_times[id])

def get(id):
    return times[id]

def average(id):
    return np.mean(times[id])
