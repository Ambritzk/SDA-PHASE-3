from multiprocessing import Queue
from multiprocessing import Process
import input
import core
import json
from typing import Dict

config: dict = None
def ReadConfig() -> dict:
    try:
        with open('config.json','r') as file:
            temp = json.load(file)
        return temp
    except FileNotFoundError:
        print("Couldn't find config.json")

if __name__ == '__main__':
    config = ReadConfig()
    quesize = config['pipeline_dynamics'].get('stream_queue_max_size')
    raw_values = Queue(maxsize=quesize)
    processed_Queue = Queue(maxsize=quesize)
    
    InputProcess = Process(target = input.run, args = (config, raw_values))


    NumberOfWorkers = config['pipeline_dynamics'].get('core_parallelism')
    CoreWorkers = [Process(target=core.run, args = (config, raw_values, processed_Queue)) for _ in range(NumberOfWorkers)]


    InputProcess.start()
    for worker in CoreWorkers:
        worker.start()
    

    InputProcess.join()
    for worker in CoreWorkers:
        worker.join()






