from multiprocessing import Process
from multiprocessing import Pool
from multiprocessing import Queue
import heapq
from functools import reduce
from typing import Dict
import hashlib



#FUNCTIONS GIVEN IN ZE PROJECT FOLDER BY ZE SIR

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







#THE MAIN FUNCTION
#THIS ALSO ACTS AS THE IMPERATIVE SHELL
#THE IMPURE TING

def run(config: Dict, InputQueue: Queue, VerifiedQueue:Queue, OutputQueue: Queue) -> None:

    None_counter = 0
    while True:
        packet = InputQueue.get()
        if packet is None:
            break

        if Authenticator(config,packet.get('metric_value')) == packet.get('security_hash'):
            #The packet has been verified
            VerifiedQueue.put(packet)
            