from multiprocessing import Process
from pyparsing import Empty

from core.functional_core import FunctionalCore
from core.imperative_shell import ImperativeShell
from input import InputProcessor
from output import OutputProcessor

import json
from multiprocessing import Manager

from typing import Dict

config: dict = None;
def ReadConfig() -> dict:
    try:
        with open('config.json','r') as file:
            temp = json.load(file)
        return temp;
    except FileNotFoundError:
        print("Couldn't find config.json")
    except json.JSONDecodeError:
        print('Something seems to be wrong with "config.json"')

if __name__ == '__main__':
    config = ReadConfig()

    quesize = config['pipeline_dynamics'].get('stream_queue_max_size')

    manager = Manager()
    rawQueue = manager.Queue(maxsize=quesize)
    verified_queue = manager.Queue(maxsize=quesize)
    processed_Queue = manager.Queue(maxsize=quesize)


    #OBJECTS
    InputWorker = InputProcessor(config,rawQueue)
    Filter = ImperativeShell(config,verified_queue,processed_Queue,rawQueue)
    Functional = FunctionalCore(config,verified_queue,processed_Queue)
    OutputWorker = OutputProcessor(config,rawQueue,verified_queue,processed_Queue)

    #THE PROCESSES
    #WE SPECIFY WHAT FUNCTION A PROCESS WILL RUN, AND THE ARGUMENTS IT WILL TAKE
    InputProcess = Process(target = InputWorker.run, args = ())

    #WE CALCULATE THE NUMBER OF CORE WORKERS ACCORDING TO WHAT WAS GIVEN IN THE CONFIG
    NumberOfWorkers = config['pipeline_dynamics'].get('core_parallelism')
    CoreFilters = [Process(target=Filter.run, args = ()) for _ in range(NumberOfWorkers)]

    Aggregator = Process(target=Functional.run,args = ())
    Visualizer = Process(target=OutputWorker.run, args=())
    #FROM HERE ONWARDS, WE START THE PROCESSES
    InputProcess.start()
    for worker in CoreFilters:
        worker.start()
    Aggregator.start()
    Visualizer.start()

    InputProcess.join()#The mother of all processes waits for the process to finish before proceeding to the next line

    #By putting a None into these queues, we are signaling the following processes to finish execution
    #otherwise, the mother of all processes would wait indefinitely because each process has a while True loop

    for i in range(NumberOfWorkers):
        rawQueue.put(None)

    for worker in CoreFilters:
        worker.join()

    verified_queue.put(None)
    Aggregator.join()

    processed_Queue.put(None)
    Visualizer.join()

#NOTE: HERE'S HOW THE CODE FLOWS:
#      THERE IS ONE InputProcess that reads the csv file line by line and sends it to the rawQueue
#      THERE ARE 4 CORE WORKERS that read the rawQueue , and filters them based on whether their hashes match
#      THE WORKERS THEN SEND THAT TO THE VERIFIED QUEUE
#      THE VERIFIED QUEUE IS READ BY THE FUNCITONAL CORE, THAT CREATES A WINDOW, SORTS THE DATA...
#      AND SENDS IT TO THE PROCESSED QUEUE
#      THE PROCESSED QUEUE IS READ BY OUTPUT, THAT IS SUPPOSED TO DISPLAY THE DATA



#IN TERMS OF THE SCATTER GATHER THING:


#                                (IMPERATIVE SHELL)(VERIFIED QUEUE)
#                            /->CORE_FILTER1----------------------\
#                           /                                      \
#                          /                                        \             (PROCESSED QUEUE)
#INPUT PROCESS (RAW QUEUE)/---->CORE_FILTER2------------------------- AGGREGATOR(FUNCTIONAL_CORE)------->OUTPUT.PY
#                         \                                          //
#                          \->CORE_FILTER3--------------------------//
#                           \                                       /
#                            \->CORE_FILTER4-----------------------/





