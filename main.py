from multiprocessing import Queue
from multiprocessing import Process
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


config = ReadConfig()
print(config)