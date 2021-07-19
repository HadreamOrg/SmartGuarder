# AAASecuritySystem
- 服务器用AAA体系安全防护系统（病毒/DDoS/服务监控）
- 所谓AAA防护系统就是：
  - AntiDDoS
  - AntiVirus
  - AllServicesMonitor
 
### AntiDDoS
- 位于anti_ddos目录下
- 功能：
  - 对疑似DDoS行为的ip进行封禁
  - 记录网卡流量和ip连接状况
  - 全局检测ip连接变化，防止多ip总量巨的攻击行为
  - 对ip实行流量/速度白名单，实行限速
- 原理：
  - 使用tcpdump分析网络流量，智能分类ip连接作记录
  - 对ip连接的信息进行行为分析，跟踪行为，判断其是否是攻击
- 组成：
  - Collector
  - Analyzer
  - Monitor
  
### AntiVirus
- 位于anti_virus目录下
- 功能：
  - 自动应对记录在案的病毒
- 原理：
  - 检测：
    - 使用busybox top和htop检查cpu/内存/进程异常情况
    - 检查crontab
    - 检查systemctl
    - 检查init.d
    - 检查netstat
  - 对策：
    - 不同病毒不同
    - 删除异常cron任务/开机启动项/端口监听行为
    
### AllServicesMonitor
- 位于all_services_monitor目录下
- 功能：
  - 智能地从内网/外网/系统进程三个方面检测服务器上的服务状态并根据预设对策自动恢复
- 组成：
  - Monitor
    - Process Level
    - LAN Level
    - WAN Level
  - Maintainer
    - Cause Analysis 
    - Countermeasure group 
