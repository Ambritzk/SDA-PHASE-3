from collections import deque
import heapq
from multiprocessing import Queue








#NOTE:FUNCTIONAL CORE IS SUPPOSED TO CREATE A WINDOW AND CALCULATE ITS RUNNING AVERAGE


class FunctionalCore:
    def __init__(self,config,VerifiedQueue,ProcessedQueue):
        self.config = config
        self.VerifiedQueue = VerifiedQueue
        self.ProcessedQueue = ProcessedQueue
    def run(self):
        window_size = self.config["processing"]["stateful_tasks"].get("running_average_window_size")

        #deque is perfect for implementing windows because once you've allocated a maximum size for it...
        #it will automatically pop elements from the left as soon as the queue is full and a new packet has arrived
        #gibing you a fully functioning window. Yayyyyyyyyyyyyyyyyyyy UWAAAAAAAAAAA

        self.window = deque(maxlen=window_size)
        while True:
            packet: dict = self.VerifiedQueue.get()
            if packet is None:
                #This means that the imperative_shell has finished its execution
                #and the functional core's time has come to an end as well \*_w_*/
                return
            
            self.window.append(packet)
            sorted_window = sorted(self.window, key=lambda p: p.get('time_period'))
            running_average = self.Aggregator(sorted_window)

            latest_packet = sorted_window[len(sorted_window) - 1]

            self.ProcessedQueue.put((running_average,latest_packet))

    def Aggregator(self, window):
        #This makes a list of the metric_values of the data, and finds the average of that
        metric_list = list(map(lambda x: x.get('metric_value'),self.window))


        avg = sum(metric_list) / len(metric_list)
        return avg

#NOTE: I AM SENDING A TUPLE (RUNNING_AVERAGE, AND THE LATEST PACKET THAT CONTAINS THE TIME AVERAGE WAS CALCULATED)