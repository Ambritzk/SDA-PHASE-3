from collections import deque
import heapq
from multiprocessing import Queue








#NOTE:FUNCTIONAL CORE IS SUPPOSED TO CREATE A WINDOW AND CALCULATE ITS RUNNING AVERAGE



def Aggregator(window: list):
    #This makes a list of the metric_values of the data, and finds the average of that
    metric_list = list(map(lambda x: x.get('metric_value'),window))


    avg = sum(metric_list) / len(metric_list)
    return avg


def run(config: dict, VerifiedQueue: Queue, ProcessedQueue: Queue) -> None:
    window_size = config["processing"]["stateful_tasks"].get("running_average_window_size")

    #deque is perfect for implementing windows because once you've allocated a maximum size for it...
    #it will automatically pop elements from the left as soon as the queue is full and a new packet has arrived
    #gibing you a fully functioning window. Yayyyyyyyyyyyyyyyyyyy UWAAAAAAAAAAA

    window = deque(maxlen=window_size)
    while True:
        packet: dict = VerifiedQueue.get()
        if packet is None:
            #This means that the imperative_shell has finished its execution
            #and the functional core's time has come to an end as well \*_w_*/
            return
        
        window.append(packet)
        sorted_window = sorted([(packet.get('time_period'),packet) for packet in window])
        sorted_window = list(map(lambda x: x[1],sorted_window))
        running_average = Aggregator(sorted_window)

        latest_packet = sorted_window[len(sorted_window) - 1]

        ProcessedQueue.put((running_average,latest_packet))

#NOTE: I AM SENDING A TUPLE (RUNNING_AVERAGE, AND THE LATEST PACKET THAT CONTAINS THE TIME AVERAGE WAS CALCULATED)