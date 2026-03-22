from multiprocessing import Queue
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MaxNLocator, FuncFormatter
import queue
from realTimeData import PipelineTelemetry, Observer

def formatTime(x, pos):
    try:
        return datetime.fromtimestamp(x).strftime('%H:%M:%S')
    except:
        return ""

class DashboardUI(Observer):
    def __init__(self, telemetry: PipelineTelemetry, config: dict):
        self.telemetry = telemetry
        self.telemetry.attach(self)
        self.config = config
        self.maxSize = config['pipeline_dynamics']['stream_queue_max_size']

        self.timePoints = []
        self.rawValues = []
        self.avgValues = []

        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(14, 8))
        self.fig.canvas.manager.set_window_title('Pipeline Dashboard')
        self.gridSpec = gridspec.GridSpec(2, 3, figure=self.fig)

        self.axRaw = self.fig.add_subplot(self.gridSpec[0, 0])
        self.axVerified = self.fig.add_subplot(self.gridSpec[0, 1])
        self.axProcessed = self.fig.add_subplot(self.gridSpec[0, 2])

        self.axValueChart = self.fig.add_subplot(self.gridSpec[1, 0:1])
        self.axAverageChart = self.fig.add_subplot(self.gridSpec[1, 1:3])

        self.fig.tight_layout(pad=3.0)
        self.tracker = 0

    def update(self, subject):
        self.drawBar(self.axRaw, 'raw_stream', subject.q_states['raw'])
        self.drawBar(self.axVerified, 'intermediate_stream', subject.q_states['verified'])
        self.drawBar(self.axProcessed, 'processed_stream', subject.q_states['processed'])

    def drawBar(self, ax, streamKey, size):
        ax.clear()

        streamConfig = self.config['visualizations']['realTimeData'][streamKey]
        if not streamConfig.get('show', False):
            return

        displayTitle = streamConfig.get('display_title', streamKey)
        safeLimit = streamConfig['thresholds']['safe']
        warningLimit = streamConfig['thresholds']['warning']

        capacityRatio = size / self.maxSize

        if capacityRatio < safeLimit:
            barColor = 'green'
        elif capacityRatio < warningLimit:
            barColor = 'yellow'
        else:
            barColor = 'red'

        ax.bar(['Capacity'], [size], color=barColor, edgecolor='white', linewidth=1)
        ax.bar(['Capacity'], [self.maxSize], color='white', alpha=0.1, edgecolor='none', zorder=0)

        ax.set_ylim(0, self.maxSize)
        ax.set_title(f"{displayTitle}\n{size} / {self.maxSize}", color=barColor, fontweight='bold', pad=10)
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white')

        for spine in ax.spines.values():
            spine.set_color('#333333')

    def animate(self, frame, processedQueue: Queue):
        self.telemetry.poll()

        while True:
            try:
                incomingData = processedQueue.get_nowait()

                if incomingData is None:
                    print()
                    print("Telemetry Data stream complete. Dashboard frozen for final review... check")
                    print("Please close the dashboard window manually to terminate the program.")

                    if hasattr(self, 'ani'):
                        self.ani.pause()

                    return

                runningAvg, packet = incomingData

                print(self.tracker, "Running avg =", runningAvg, "at Time=", datetime.fromtimestamp(packet.get('time_period')))
                self.tracker += 1

                self.timePoints.append(packet.get('time_period'))
                self.rawValues.append(packet.get('metric_value'))
                self.avgValues.append(runningAvg)

                if len(self.timePoints) > 50:
                    self.timePoints.pop(0)
                    self.rawValues.pop(0)
                    self.avgValues.pop(0)

            except queue.Empty:
                break
            except Exception as e:
                if 'Empty' in type(e).__name__:
                    break
                else:
                    raise

        if self.timePoints:
            self.axValueChart.clear()
            self.axValueChart.plot(self.timePoints, self.rawValues, color='cyan', marker='o', label='Sensor Data')
            self.axValueChart.set_title(self.config['visualizations']['data_charts'][0]['title'])
            self.axValueChart.set_facecolor('#111111')
            self.axValueChart.legend(loc='upper left', frameon=False, labelcolor='white')
            self.axValueChart.xaxis.set_major_locator(MaxNLocator(nbins=10, integer=True))
            self.axValueChart.xaxis.set_major_formatter(FuncFormatter(formatTime))
            self.axValueChart.tick_params(axis='x', rotation=45, colors='white')
            self.axValueChart.tick_params(axis='y', colors='white')

            self.axAverageChart.clear()
            self.axAverageChart.plot(self.timePoints, self.avgValues, color='magenta', linewidth=2, label='Computed Average')
            self.axAverageChart.set_title(self.config['visualizations']['data_charts'][1]['title'])
            self.axAverageChart.set_facecolor('#111111')
            self.axAverageChart.legend(loc='upper left', frameon=False, labelcolor='white')
            self.axAverageChart.xaxis.set_major_locator(MaxNLocator(nbins=20, integer=True))
            self.axAverageChart.xaxis.set_major_formatter(FuncFormatter(formatTime))
            self.axAverageChart.tick_params(axis='x', rotation=45, colors='white')
            self.axAverageChart.tick_params(axis='y', colors='white')

def run(config, rawQueue: Queue, verifiedQueue: Queue, processedQueue: Queue):
    maxSize = config['pipeline_dynamics']['stream_queue_max_size']

    telemetrySubject = PipelineTelemetry(rawQueue, verifiedQueue, processedQueue, maxSize)
    dashboard = DashboardUI(telemetrySubject, config)

    dashboard.ani = FuncAnimation(dashboard.fig, dashboard.animate, fargs=(processedQueue,), interval=100, cache_frame_data=False)
    plt.show()