from multiprocessing import Process
from multiprocessing import Queue
from typing import Dict
def run(config: Dict, InputQueue: Queue, OutputQueue: Queue) -> None:
    while True:
        packet = InputQueue.get()
        if packet is None:
            break
        print(packet)