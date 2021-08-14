# coding=utf-8
# date: 2021/8/8
# author: Lanzhijiang
# description: the main logical of ALL_SERVICES_ON

import json
import time
import os


class AllServicesStartup:
    '''auto startup all the service'''

    def __init__(self, base):

        self.base = base
        self.log = base.log
        self.services_conf = base.services_conf

    def execute(self, command):

        """
        在终端执行命令
        :param command: 命令
        :return:
        """
        self.log.add_log("AllServicesStartup: executing: '%s'" % command, 0)
        terminate = os.popen(command)
        result = terminate.read()
        terminate.close()

        return result

    def run(self):

        """
        执行全套自启动
        :return:
        """
        self.log.add_log("AllServicesStartup: start all the services...", 1)

        services_list = self.services_conf["servicesList"]
        self.services_conf["servicesList"].remove("DOCKER")
        self.services_conf["servicesList"].remove("NETDATA")
        self.services_conf["servicesList"].remove("HTTPD")

        for service in services_list:
            time.sleep(0.5)
            self.log.add_log("AllServicesStartup: starting %s..." % service, 1)
            self.execute(self.services_conf[service]["serviceOpe"]["start"])

