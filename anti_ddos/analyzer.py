# Date: 2021/7/19
# Author: Lan_zhijiang
# Description: AntiDDoS对数据进行加工

import threading
import time
import os


class Analyzer:

    def __init__(self, base):

        self.base = base
        self.log = base.log
        self.raw_queue = base.raw_queue
        self.basic_analyze_result_queue = base.basic_analyze_result_queue
        self.complex_analyze_result = base.complex_analyze_result
        self.settings = base.settings

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
            self.log.add_log("Analyzer: now: %s" % line, 0)
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

            date = time.strftime("%Y-%m-%d", time.localtime()) + " " + part1[0]
            time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
            output["what"]["timestamp"] = str(time.mktime(time_array))

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

    def compute_now_speed(self, connection_id):

        """
        计算当前速度
        :param connection_id: 要计算的这个连接的id
        desc: 维持最近2s的数据，以此计算每秒速度
        :return:
        """
        connection_data = self.complex_analyze_result[connection_id]
        recent_traffic = connection_data["recent_traffic"]
        a = list(recent_traffic.keys())
        difference = abs(float(recent_traffic[1]) - float(recent_traffic[-1]))

        if difference < 1 or len(recent_traffic) < 3:
            speed = None
        else:
            total = 0
            for i in a:
                total += recent_traffic[i]
            speed = total/difference
            del self.complex_analyze_result[connection_id]["recent_traffic"][
                list(recent_traffic.keys())[1]
            ]

        return speed

    def advanced_analyze(self):

        """
        对粗加工过后的数据进行归类、分析、计算
        desc:
            高级分析包括「对ip连接分类、出入分类、」「更新每个连接和总情况的实时速度与总流量」「对连接类型/数量进行标记/统计」「记录当前连接状态」「ip连接总数/变化（ip的，每个ip的）」「删除过时数据」
        :return:
        """
        self.log.add_log("Analyzer: start advanced analyzing", 1)
        record_template = {
            "src": "",
            "dst": "",
            "status": "",  # handshaking1/2/3 data_transportation fin rst
            "protocol": "",
            "total_traffic": "",
            "now_speed": "",
            "connection_count": "",
            "handshake_status_count": {
                "1": "",
                "2": "",
                "3": ""
            },
            "records": [],
            "recent_traffic": {}
        }

        now_connection_ids = list(self.complex_analyze_result.keys())
        line = self.basic_analyze_result_queue.get()
        while line != "":
            is_new = False
            time.sleep(0.15)

            src = line["who"]["src"] + ":" + line["who"]["src_port"]
            dst = line["who"]["dst"] + ":" + line["who"]["dst_port"]
            connection_id = src + " > " + dst
            # ---------------classify---------------
            self.log.add_log("Analyzer: AA stage 1, classify c_id-%s" % connection_id, 1)
            if connection_id not in now_connection_ids:
                is_new = True
                now_connection_ids.append(connection_id)
                self.complex_analyze_result[connection_id] = record_template
            self.complex_analyze_result[connection_id]["records"].insert(0, line)
            self.complex_analyze_result[connection_id]["src"] = src
            self.complex_analyze_result[connection_id]["dst"] = dst

            # ---------------compute base status---------------
            self.complex_analyze_result[connection_id]["total_traffic"] += line["what"]["length"]
            self.complex_analyze_result[connection_id]["recent_traffic"][line["what"]["timestamp"]] = line["what"]["length"]
            self.complex_analyze_result[connection_id]["now_speed"] = self.compute_now_speed(connection_id)

            self.complex_analyze_result["overall"]["recent_traffic"][line["what"]["timestamp"]] = line["what"]["length"]
            self.complex_analyze_result[connection_id]["now_speed"] = self.compute_now_speed("overall")
            self.complex_analyze_result["overall"]["total_traffic"] += line["what"]["length"]
            if dst == self.settings["host"]: # in traffic
                self.complex_analyze_result["overall"]["in_traffic"] += line["what"]["length"]
            elif src == self.settings["host"]: # out traffic
                self.complex_analyze_result["overall"]["out_traffic"] += line["what"]["length"]

            # count now ip connections
            # single ip
            if dst == self.settings["host"]:
                connections = os.popen("netstat -ntu | awk '{print $5}' | cut -d: -f1 | uniq -c | sort -n | awk '{print $1}'").read().split("\n")[1:-1]
                address = os.popen("netstat -ntu | awk '{print $5}' | cut -d: -f1 | uniq -c | sort -n | awk '{print $2}").read().split("\n")[1:-1]
                if src in address:
                    self.complex_analyze_result[connection_id]["connection_count"] = connections[address.index(src)]
                else:
                    self.complex_analyze_result[connection_id]["connection_count"] = None
            else:
                self.complex_analyze_result[connection_id]["connection_count"] = None
            # overall(2s之内新建的ip连接将被重点关注）
            if is_new:
                if not self.complex_analyze_result["overall"]["new_connections"]:
                    self.complex_analyze_result["overall"]["new_connections"] = []
                    self.complex_analyze_result["overall"]["new_connections"].append(connection_id)
                else:
                    difference = abs(float(self.complex_analyze_result[self.complex_analyze_result["overall"]["new_connections"][0]]["what"]["timestamp"]) - \
                        float(self.complex_analyze_result[connection_id]["what"]["timestamp"]))
                    if difference > 2:
                        del self.complex_analyze_result["overall"]["new_connections"][0:]
                    else:
                        del self.complex_analyze_result["overall"]["new_connections"][0]
                    self.complex_analyze_result["overall"]["new_connections"].append(connection_id)
                    if len(self.complex_analyze_result["overall"]["new_connections"]) >= self.settings["new_connections_limit"]:
                        self.log.add_log("Analyzer: new_connections was over the limit", 2)
                        self.complex_analyze_result["overall"]["new_connections_warning"] = True
                        self.complex_analyze_result["overall"]["under_tracking_connections"].append(self.complex_analyze_result["overall"]["new_connections"])
                        del self.complex_analyze_result["overall"]["new_connections"][0:]

            # delete outdated records
            record_length = len(self.complex_analyze_result[connection_id]["records"])
            if record_length > 60:
                now_timestamp = time.time()
                node = None
                for index in range(0, record_length):
                    if now_timestamp - float(self.complex_analyze_result[connection_id]["records"][index]["what"]["timestamp"]) >= 20:
                        node = index
                        break
                if node != 0:
                    for index in range(node, record_length+1):
                        del self.complex_analyze_result[connection_id]["records"][index]

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
