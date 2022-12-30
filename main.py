import configparser
import sqlite3
import time
import uuid
from sys import argv

# 当前时间
currentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# 分组列表
tableName = list()

# shell表字段
shellDict = {
    "id": "",
    "url": "",
    "password": "",
    "secretKey": "",
    "payload": "",
    "cryption": "",
    "encoding": "",
    "headers": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\nAccept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "reqLeft": "",
    "reqRight": "",
    "connTimeout": "",
    "readTimeout": "",
    "proxyType": "",
    "proxyHost": "",
    "proxyPort": "",
    "remark": "",
    "note": "",
    "createTime": "",
    "updateTime": "",
    "group": "/"
}


# 读取shellUrl文本，返回每个url对应uuid的列表
def readShell(filename: str):
    """
    :param filename: shell链接文件
    :return: 每个shell链接对应uuid的列表
    """
    temp = dict()
    urlList = list()
    with open(filename, "r", encoding="utf-8") as f:
        for u in f.readlines():
            us = u.strip()
            temp["id"] = uuidEncode(us)
            temp["url"] = us
            urlList.append(temp)
            temp = dict()

    return urlList


# 根据链接生成专属的uuid值
def uuidEncode(name: str):
    """
    :param name: 名字
    :return: 加密后的值
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))


# 获取配置文件，并将配置信息更新到字典变量中
def getConfig():
    # 实例化
    cf = configparser.ConfigParser()
    # 键值保持大小写
    cf.optionxform = str
    # 读取配置文件
    cf.read(filenames="config.ini", encoding="utf-8")
    # 获取配置文件中的选项名
    sec = cf.sections()
    # print(sec)
    #  获取配置文件中指定选项的配置信息的键值对
    items = cf.items(sec[0])
    items = dict(items)
    # print(items)
    # 将配置信息更新到字典变量
    shellDict.update(items)
    # 添加更新时间
    shellDict["createTime"] = currentTime
    shellDict["updateTime"] = currentTime


# db数据查询
def dataDbRead(Db: ...):
    # 创建游标执行sql语句
    cursor = Db.cursor()
    # 查询指定表中的列【获取现有的组】
    cursor.execute("SELECT groupid from shellGroup")
    print("当前已有分组：")
    print("-" * 30)
    for row in cursor:
        print(f"    {row[0]}")
        tableName.append(row[0])
    print("-" * 30)
    group = input("[?] 选择导入的分组或创建新的分组，默认分组为[/]：")
    if group != "":
        shellDict["group"] = group
        cursor.execute(f"INSERT INTO shellGroup VALUES ('{group}');")


# db数据写入
def dataDbWrite(Db: ..., sDict: dict):
    # 创建游标执行sql语句
    cursor = Db.cursor()
    # 插入shell表数据
    cursor.execute(
        f"INSERT INTO shell VALUES ('{sDict['id']}','{sDict['url']}','{sDict['password']}','{sDict['secretKey']}','{sDict['payload']}','{sDict['cryption']}','{sDict['encoding']}','{sDict['headers']}','{sDict['reqLeft']}','{sDict['reqRight']}','{sDict['connTimeout']}','{sDict['readTimeout']}','{sDict['proxyType']}','{sDict['proxyHost']}','{sDict['proxyPort']}','{sDict['remark']}','{sDict['note']}','{sDict['createTime']}','{sDict['updateTime']}');")

    # 插入shellEnv表数据
    cursor.execute(f"INSERT INTO shellEnv VALUES ('{sDict['id']}','ENV_GROUP_ID','{sDict['group']}');")
    cursor.execute(
        f"INSERT INTO shellEnv VALUES ('{sDict['id']}','ENV_ShellExecCommandPanel_Command_KEY','sh -c \"{{command}}\" 2>&1');")

    # 提交数据
    Db.commit()

if __name__ == '__main__':
    # 文件路径获取
    urlFile = input("[!] 输入shell链接文本路径：")
    Godzilla_db = input("[!] 输入Godzilla的data.db路径：")
    # 读取shell链接返回url列表
    url_list = readShell(urlFile)
    # 连接读取sqlite数据
    coon = sqlite3.connect(Godzilla_db)
    # 获取配置信息并更新到字典变量
    getConfig()
    # 读取已有的分组
    dataDbRead(coon)
    # print(shellDict)
    # 数据写入
    for u in url_list:
        shellDict.update(u)
        dataDbWrite(coon, shellDict)

    # 关闭连接
    coon.close()
    print("[*] 写入完成")
