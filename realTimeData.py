from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass


class Subject(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)


# Telemetry Monitor
class PipelineTelemetry(Subject):
    def __init__(self, raw_q, verified_q, processed_q, max_size):
        super().__init__()
        self.queues = {
            'raw': raw_q,
            'verified': verified_q,
            'processed': processed_q
        }
        self.max_size = max_size
        self.q_states = {'raw': 0, 'verified': 0, 'processed': 0}

    def poll(self):
        """Polls the sizes of the multiprocessing queues."""
        for name, q in self.queues.items():
            try:
                self.q_states[name] = q.qsize()
            except NotImplementedError:
                self.q_states[name] = 0
        self.notify()

    def statusColor(self, size):
        if self.max_size == 0: return 'green'
        ratio = size / self.max_size

        if ratio < 0.5: return 'green'
        if ratio < 0.8: return 'yellow'
        return 'red'