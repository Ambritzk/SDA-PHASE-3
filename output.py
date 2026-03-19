from multiprocessing import Queue
from datetime import datetime
def run(ProcessedQueue: Queue):
    i = 0 #this is for printing the line and for getting a sense of how many packets made it through
    while True:
        processed_tuple = ProcessedQueue.get()
        if processed_tuple is None:
            break
        running_avg , packet = processed_tuple
        print(i,"Running avg =",running_avg, "at Time=",datetime.fromtimestamp(packet.get('time_period')))
        i = i + 1

#NOTE:
#PROCESSED QUEUE RECEIVES TWO ITEMS:
#1)RUNNING AVERAGE
#2)THE LATEST PACKET THAT WAS LAST READ AND PROCESSED, THIS WILL HELP YOU TRACK IT BY THE SECOND, SO YOU CAN DRAW A LINE GRAPH