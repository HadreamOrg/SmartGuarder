# Date: 2021/7/19
# Author: Lan_zhijiang
# Description: AntiDDoS的数据收集部分

import os
import time


class Collector:

    def __init__(self, base):

        self.base = base
        self.settings = base.settings
        self.log = base.log
        self.raw_queue = base.raw_queue
        self.basic_analyze_result_queue = base.basic_analyze_result_queue
        self.complex_analyze_result = base.complex_analyze_result

        self.tcpdump_pid = ""
        self.tcpdump_stop = False

    def get_flow_data(self, command):

        """
        使用tcpdump抓取流数据
        :param command: 抓取命令
        :return:
        """
        terminal = os.popen(command)

        terminal = os.popen(command + " > ./data/tcpudmp.out 2>./data/tcpdump_error.out &")
        self.tcpdump_pid = terminal.read().replace("[1] ", "")
        self.log.add_log("Collector: tcpdump is running, pid: %s" % self.tcpdump_pid, 1)
        terminal.close()

        # wait for data
        time.sleep(5)

        # read data and put to raw_queue
        file = open("./data/tcpdump.out", "r")
        feed = file.readline()
        while feed != "" and not self.tcpdump_stop:
            # print("put")
            self.raw_queue.put(feed)

        os.system("kill -9 %s" % self.tcpdump_pid)
        self.log.add_log("Collector: tcpdump had stopped", 1)
        file.close()
        terminal.close()

    def run(self):

        """
        启动collector
        :return:
        """
        self.log.add_log("Collector: start collect data in default", 1)
        self.get_flow_data("nohup tcpdump -i %s" % self.settings["network_card"])
        self.log.add_log("Collector: collector had stopped", 1)
