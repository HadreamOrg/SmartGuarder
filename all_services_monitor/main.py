# date: 2021/8/10
# author: Lan_zhijiang
# description: all_services_monitor 启动

import json
from log import Log
from all_services_monitor.startup import AllServicesStartup


class Base:

    def __init__(self):

        self.log = Log()
        self.log.log_setting["logPath"] = "./data/logs/all_services_monitor/"

        self.services_conf = json.load(open("./all_services_monitor/service_conf.json", "r", encoding="utf-8"))

    def run_startup(self):

        """
        启动自启动所有服务脚本
        :return:
        """
        AllServicesStartup(self).run()
