from multiprocessing import Process
from multiprocessing import Pool
from multiprocessing import Queue
import heapq
from functools import reduce
from typing import Dict
import hashlib
import time


#FUNCTIONS GIVEN IN ZE PROJECT FOLDER BY ZE SIR

# def generate_signature(raw_value_str: str, key: str, iterations: int) -> str:
#     """
#     Generates a PBKDF2 HMAC SHA-256 signature for the given value.
#     Treats the secret key as the password and the raw value as the salt.
#     """
#     password_bytes = key.encode('utf-8')
#     salt_bytes = raw_value_str.encode('utf-8')
    
#     # Generate the hash
#     hash_bytes = hashlib.pbkdf2_hmac(
#         hash_name='sha256', 
#         password=password_bytes, 
#         salt=salt_bytes, 
#         iterations=iterations
#     )
#     return hash_bytes.hex()

# def Authenticator(config: Dict, metric_value):
#     SECRET_KEY = config["processing"]["stateless_tasks"].get("secret_key")
#     ITERATIONS = config["processing"]["stateless_tasks"].get("iterations")
#     rounded_value = str(round(metric_value,2))
#     return generate_signature(rounded_value,SECRET_KEY,ITERATIONS)







# #THE MAIN FUNCTION
# #THIS ALSO ACTS AS THE IMPERATIVE SHELL
# #THE IMPURE TING

# def run(config: Dict, InputQueue: Queue, VerifiedQueue: Queue, OutputQueue: Queue) -> None:
#     while True:
#         packet = InputQueue.get()
#         if packet is None:
#             break

#         if Authenticator(config, packet.get('metric_value')) == packet.get('security_hash'):
#             time.sleep(0.05)
#             VerifiedQueue.put(packet)


class ImperativeShell:
    def __init__(self,config,VerifiedQueue,OutputQueue,InputQueue):
        self.InputQueue = InputQueue
        self.OutputQueue = OutputQueue
        self.VerifiedQueue = VerifiedQueue

    def run(self) -> None:
        while True:
            packet = self.InputQueue.get()
            if packet is None:
                break

            if self.Authenticator(self.config, packet.get('metric_value')) == packet.get('security_hash'):
                time.sleep(0.05)
                self.VerifiedQueue.put(packet)

    def Authenticator(self,metric_value):
        SECRET_KEY = self.config["processing"]["stateless_tasks"].get("secret_key")
        ITERATIONS = self.config["processing"]["stateless_tasks"].get("iterations")
        rounded_value = str(round(metric_value,2))
        return self.generate_signature(rounded_value,SECRET_KEY,ITERATIONS)
    

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