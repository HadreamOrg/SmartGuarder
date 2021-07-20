# Date: 2021/7/19
# Author: Lan_zhijiang
# Description: AntiDDoS的Base

import queue
import threading
import time

from log import Log
from anti_ddos.collector import Collector
from anti_ddos.analyzer import Analyzer
from anti_ddos.monitor import Monitor


class Base:

    def __init__(self):

        self.log = Log()
        self.log.log_setting["logPath"] = "./data/logs/anti_ddos/"

        self.raw_queue = queue.Queue()
        self.basic_analyze_result_queue = queue.Queue()
        self.complex_analyze_result = {
            "overall": {
                "total_traffic": "",
                "in_traffic": "",
                "out_traffic": "",
                "recent_traffic": {},
                "new_connections": None,
                "new_connections_warning": False,
                "under_tracking_connections": []
            }
        }
        self.public_event = {
            "toMonitor": [],
            "toAnalyzer": [],
            "toCollector": []
        }

        self.settings = {
            "network_card": "enp34s0",
            "host": "192.168.3.156",
            "new_connections_limit": 12
        }


if __name__ == "__main__":

    base = Base()
    collector = Collector(base)
    analyzer = Analyzer(base)
    monitor = Monitor(base)

    thread1 = threading.Thread(target=collector.run, args=())
    thread2 = threading.Thread(target=analyzer.run, args=())
    thread3 = threading.Thread(target=monitor.run, args=())
    thread1.run()
    time.sleep(10)
    thread2.run()
    time.sleep(10)
    thread3.run()
