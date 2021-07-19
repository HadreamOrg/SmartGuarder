# Date: 2021/7/19
# Author: Lan_zhijiang
# Description: AntiDDoS对数据进行加工

import threading
import time


class Analyzer:

    def __init__(self, base):

        self.base = base
        self.log = base.log
        self.raw_queue = base.raw_queue
        self.basic_analyze_result_queue = base.basic_analyze_result_queue
        self.complex_analyze_result = base.complex_analyze_result

    def basic_analyze(self):

        """
        对每条数据进行粗加工，提取信息并以dict形式存储
        :return:
        """
        self.log.add_log("Analyzer: start basic analyzing", 1)

        count = 0
        line = self.raw_queue.get()
        while line != "":
            time.sleep(0.1)
            count += 1
            #             if count == len(data):
            #                 break
            output = {
                "id": "",
                "who": {"src": "", "src_port": "", "dst": "", "dst_port": ""},
                "what": {"timestamp": "", "flags": "", "ack": "", "seq": [0, 1], "length": ""},
                "more": {"options": []}
            }

            print("analyzing data-%s" % count)
            output["id"] = count
            # phase 1
            part = line.split(": ")
            #         print(part)
            part1 = part[0].split(" ", 2)
            part2 = part[1].split(", ")
            #         print(part1, "\n", part2)
            part3 = part1[2].split(" > ")
            #         print(part3)
            a, b = part3[0].rsplit(".", 1), part3[1].rsplit(".", 1)
            output["who"]["src"], output["who"]["src_port"] = a[0], a[1]
            output["who"]["dst"], output["who"]["dst_port"] = b[0], b[1]
            #         print(src_ip, src_port)
            #         print(dst_ip, dst_port)
            output["what"]["timestamp"] = part1[0]
            for j in part2:
                if "Flags" in j:
                    output["what"]["flags"] = j.split(" ")[1]
                elif "seq" in j:
                    output["what"]["seq"] = j.split(" ")[1].split(":")
                elif "ack" in j:
                    output["what"]["ack"] = j.split(" ")[1]
                elif "options" in j:
                    output["more"]["options"] = j.split(" ", 1)[1]
                elif "length" in j:
                    output["what"]["length"] = j.split(" ")[1]

            self.basic_analyze_result_queue.put(output)
            line = self.raw_queue.get()

    def advanced_analyze(self):

        """
        对粗加工过后的数据进行归类、分析、计算
        desc:
            高级分析包括「对ip连接分类、出入分类、」「更新每个连接和总情况的实时速度与总流量」「ip连接总数/变化（ip的，每个ip的）」「删除过时数据」
        :return:
        """
        self.log.add_log("Analyzer: start advanced analyzing", 1)
        record_template = {
            "src": "",
            "dst": "",
            "total_traffic": "",
            "in_traffic": "",
            "out_traffic": "",
            "now_speed": "",
            "connection_count": "",
            "records": [],

        }

        now_connection_ids = list(self.complex_analyze_result.keys())
        line = self.basic_analyze_result_queue.get()
        while line != "":
            time.sleep(0.15)
            src = line["who"]["src"] + ":" + line["who"]["src_port"]
            dst = line["who"]["dst"] + ":" + line["who"]["dst_port"]
            connection_id = src + " > " + dst
            # ---------------classify---------------
            self.log.add_log("Analyzer: AA stage 1, classify c_id-%s" % connection_id, 1)
            if connection_id not in now_connection_ids:
                now_connection_ids.append(connection_id)
                self.complex_analyze_result[connection_id] = record_template

            self.complex_analyze_result[connection_id]["records"].insert(0, line)
            self.complex_analyze_result[connection_id]["src"] = src
            self.complex_analyze_result[connection_id]["dst"] = src



    def run(self):

        """
        启动分析
        :return:
        """
        basic_analyze = threading.Thread(target=self.basic_analyze, args=())
        advanced_analyze = threading.Thread(target=self.advanced_analyze, args=())
        basic_analyze.run()
        time.sleep(5)
        advanced_analyze.run()
