# Date: 2021/7/20
# Author: Lan_zhijiang
# Description: AntiDDoS的监控系统

import os
import time
import json


class Monitor:

    def __init__(self, base):

        self.base = base
        self.log = base.log
        self.complex_analyze_result = base.complex_analyze_result
        self.settings = base.settings

        self.old_data = {}

    def new_connections_monitor(self):

        """
        跟踪诡异的新连接组
        :return:
        """

    def every_connection_monitor(self):

        """
        对每个连接进行监控，包括：「删除长时间没有新记录的连接」「监控每个连接基本属性与上次的变化」
        :return:
        """
        self.log.add_log("Monitor: start every connection monitor", 1)

    def overall_monitor(self):

        """
        对全局状况的监控
        :return:
        """
        self.log.add_log("Monitor: start overall monitor", 1)

    def run(self):

        """
        启动
        :return:
        """
