import multiprocessing as mp
import queue
from queue import Queue
from multiprocessing.managers import BaseManager
class Worker(mp.Process):
    def __init__(self, message_queue):
        self.message_queue = message_queue
        super(Worker, self).__init__()
    def run(self):
        result = self.message_queue.get()
        result.append('Worker: Hello!')
        self.message_queue.put(result)
        queue = mp.Queue()
        queue.put([])
        worker = Worker(queue)
        worker.start()
class QueueManager(BaseManager):
    pass
if __name__ == '__main__':
    QueueManager.register('get_queue', callable=lambda: queue)
    manager = QueueManager(address=('localhost', 50000),
    authkey=b'your_secret_key')
    server = manager.get_server()
    server.serve_forever()
