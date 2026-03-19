from multiprocessing import Process
from multiprocessing import Pool
from multiprocessing import Queue
from collections import deque
import heapq
from functools import reduce
from typing import Dict
import hashlib


#This module should perform 2 functions:
#1)Verify that the data packet is authentic
#2)Perform average of the window or whatever




def generate_signature(raw_value_str: str, key: str, iterations: int) -> str:
    """
    Generates a PBKDF2 HMAC SHA-256 signature for the given value.
    Treats the secret key as the password and the raw value as the salt.
    """
    password_bytes = key.encode('utf-8')
    salt_bytes = raw_value_str.encode('utf-8')
    
    # Generate the hash
    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name='sha256', 
        password=password_bytes, 
        salt=salt_bytes, 
        iterations=iterations
    )
    return hash_bytes.hex()

def Authenticator(config: Dict, metric_value):
    SECRET_KEY = config["processing"]["stateless_tasks"].get("secret_key")
    ITERATIONS = config["processing"]["stateless_tasks"].get("iterations")
    rounded_value = str(round(metric_value,2))
    return generate_signature(rounded_value,SECRET_KEY,ITERATIONS)






def Aggregator(window: deque,i):
    sorted_window = [(packet.get('time_period'),packet) for packet in window]
    heapq.heapify(sorted_window)
    
    snapshot = [packet.get('metric_value') for val,packet in sorted_window]
    avg = sum(snapshot) / len(snapshot) if len(snapshot) != 0 else 0
    print(i,"Running average =",avg)
#THE MAIN FUNCTION
#THIS ALSO ACTS AS THE IMPERATIVE SHELL
#THE IMPURE TING

def run(config: Dict, InputQueue: Queue, VerifiedQueue:Queue, OutputQueue: Queue) -> None:
    window_size = config["processing"]["stateful_tasks"].get("running_average_window_size")
    window = deque(maxlen=window_size)
    i = 0
    while True:
        packet = InputQueue.get()
        if packet is None:
            break

        #Added the print just to show how this function is receiving packets from the input module
        if Authenticator(config,packet.get('metric_value')) == packet.get('security_hash'):
            #The packet has been verified
            #Now we need to implement a sliding window, and pass it to the aggregator
            #That's going to give us the running average
            if len(window) < window_size:
                window.append(packet)
            else:
                window.popleft()
                window.append(packet)

            Aggregator(window,i)
            
        i = i + 1