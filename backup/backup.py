# date: 2021/8/11
# author: Lan_zhijiang
# description: 备份数据脚本，将所有要备份地数据移动到一个地方

import os
import schedule
import time
import datetime as dt
from log import Log

### CONFIG
log = Log()
log.log_setting["logPath"] = "./logs/"
VERSION_LASTING_COUNT = 5
BACKUP_DIC = "/home/storage_disk/backup"

DOCKER_NAME_LIST = ["ergo_irc", "wallabag", "wallabag-db", "tube", "lychee", "etherpad", "netdata"]
STORAGE_DISK_BACKUP_DIC_LIST = ["chevereto", "nginx_sharing", "wget", "aria2", "Emby"]
###


def execute(command):
    """
    在终端执行命令
    :param command: 命令
    :return:
    """
    log.add_log("Backup: executing: '%s'" % command, 0)
    terminate = os.popen(command)
    result = terminate.read()
    terminate.close()

    return result


def difference_between_2_date(d1, d2):
    """
    计算两个日期的天数差
    :param d1: format: yyyy-mm-dd
    :param d2:
    :return:
    """
    date1 = dt.datetime.strptime(d1, "%Y-%m-%d").date()
    date2 = dt.datetime.strptime(d2, "%Y-%m-%d").date()
    return (date2 - date1).days


def backup_database():
    """
    备份数据库
    :return:
    """
    log.add_log("BackupDatabase: backup database start", 1)
    file_path = "/www/backup/database"
    file_list = os.listdir(file_path)
    for file in file_list:
        log.add_log("BackupDatabase: now processing: %s" % file, 0)
        execute("cp %s/%s %s/database/%s" % (file_path, file, BACKUP_DIC, file))
        execute("rm -rf %s/%s" % (file_path, file))

    # had_backup_list = os.listdir(BACKUP_DIC + "/database")
    # today_date = log.get_date()
    # for file in had_backup_list:
    #     c_date = time.strftime("%Y-%m-%d", time.localtime(os.stat(BACKUP_DIC + "/database/" + file).st_mtime))
    #     if today_date -


def backup_website():
    """
    备份网站
    :return:
    """
    log.add_log("BackupWebsite: backup website start", 1)
    file_path = "/www/backup/site"
    file_list = os.listdir(file_path)
    for file in file_list:
        log.add_log("BackupWebsite: now processing: %s" % file, 0)
        execute("cp %s/%s %s/website/%s" % (file_path, file, BACKUP_DIC, file))
        execute("rm -rf %s/%s" % (file_path, file))


def backup_docker():
    """
    备份docker镜像
    :return:
    """
    log.add_log("BackupDocker: backup docker container start", 1)
    for name in DOCKER_NAME_LIST:
        log.add_log("BackupDocker: container-%s is now backup" % name, 1)
        command = "docker export %s > %s" % (name, BACKUP_DIC + "/docker/%s.tar" % name)
        execute(command)


def backup_disk():
    """
    备份分区内容：develop_disk drive_disk storage_disk(chevereto, nginx_sharing, wget, aria2, Emby) apps hadream
    :return:
    """
    log.add_log("BackupDisk: backup disk start", 1)
    base_command = "tar -czvf "
    # DEVELOP_DISK
    log.add_log("BackupDisk: backup develop_disk for full version", 1)
    execute(base_command + BACKUP_DIC + "/disk/develop_disk.tar.gz /home/develop_disk/")
    # DRIVE_DISK
    log.add_log("BackupDisk: backup drive_disk for full version", 1)
    execute(base_command + BACKUP_DIC + "/disk/drive_disk.tar.gz /home/drive_disk/")
    # # APPS
    # log.add_log("BackupDisk: backup /home/apps for full version", 1)
    # execute(base_command + BACKUP_DIC + "/disk/apps.tar.gz /home/apps/")
    # HADREAM
    log.add_log("BackupDisk: backup /home/hadream for full version", 1)
    execute(base_command + BACKUP_DIC + "/disk/hadream.tar.gz /home/hadream/")
    # STORAGE_DISK
    for path in STORAGE_DISK_BACKUP_DIC_LIST:
        log.add_log("BackupDisk: backup /home/storage_disk/%s for full version" % path, 1)
        execute(base_command + BACKUP_DIC + "/disk/storage_disk_%s.tar.gz /home/storage_disk/%s" % (path, path))


if __name__ == "__main__":
    log.add_log("-------START BACKUP SYSTEM-------", 1)

    def run():
        today_date = log.get_date()

        f = open("./last_small_backup.txt", "r")
        last_backup_date = f.read()
        f.close()

        if last_backup_date == "" or abs(int(difference_between_2_date(last_backup_date, today_date))) >= 3:
            f = open("./last_small_backup.txt", "w")
            f.write(today_date)
            f.close()
            backup_database()
            backup_website()
            backup_docker()

        f = open("./last_big_backup.txt", "r")
        last_backup_date = f.read()
        f.close()

        if last_backup_date == "" or abs(int(difference_between_2_date(last_backup_date, today_date))) >= 15:
            f = open("./last_big_backup.txt", "w")
            f.write(today_date)
            f.close()
            backup_disk()

    schedule.every().day.at("02:00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(3400)
