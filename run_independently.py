# date: 2021/8/10
# author: Lan_zhijiang
# description: 独立运行某个部分

import sys
from all_services_monitor.main import Base


if __name__ == "__main__":

    arg = sys.argv[1]
    print(1)
    if arg == "startup":
        print(0)
        Base().run_startup()
