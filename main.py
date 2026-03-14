from multiprocessing import Queue
from multiprocessing import Process
import input
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
    raw_values = Queue()
    input.run(config,raw_values)

