import re
import requests
from time import sleep
from mysql.connector import *
from bs4 import BeautifulSoup

class POJStatus:

    def __init__(self):
        self.session = requests.session()
        self.statusUrl = 'http://poj.org/status'
        self.nextStatusUrl = 'http://poj.org/status'
        self.usallyList = {1, 4, 8, 12, 15, 17, 19, 21, 23}
        self.unusalList = {1, 4, 8, 13, 14, 15, 21, 23, 25}
        
    # 得到数据库的连接
    def getConn(self, userName, userPwd, host, db):
        createTable = """
        create table if not exists pojStatus(
            RunID int primary key not null,
            User char(20) not null,
            Problem int not null,
            Result char(30) not null,
            Memory char(10),
            Time char(10),
            Language char(10),
            CodeLength char(10),
            submitTime char(20)
        );"""

        conn = connect(user = userName, password = userPwd, host = host, database = db)
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor

        try:
            cursor.execute(createTable)
            conn.commit()
            print("createTable successful")
            return True

        except:
            print("createTable failure")
            return False


    # 将数据插入到数据库中
    # 正在判的题目也插入到数据库中了
    def insertData(self, statusList):
        try:
            conn = self.conn
            cursor = self.cursor
            for status in statusList:
                insertSql = "INSERT INTO pojStatus(RunId, User, Problem, Result, Memory, Time, Language, CodeLength, submitTime) VALUES ({}, '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}')".format(int(status[0]), status[1], int(status[2]), status[3], status[4], status[5], status[6], status[7], status[8])
                cursor.execute(insertSql)
            conn.commit()
            print("insert into db " + str(len(statusList)) +" rows")
            return True
        except:
            print("insert into db failure")
            return False


    # 解析网页得到当前页的 提交信息存在 statusList 中
    def getStatusList(self, page):
        try:
            if(re.search('\<a href=status(\?top\=.+?)\>', page.text)):
                self.nextStatusUrl = self.statusUrl + str(re.findall('\<a href=status(\?top\=.+?)\>', page.text)[0])
            else: 
                return []
            soup = BeautifulSoup(page.text, "html.parser")
            table = soup.findAll('table', {'class':'a'})
            soup = BeautifulSoup(str(table), "html.parser")
            allStatus = soup.findAll('tr', {'align':'center'})
            statusList = []
            for status in allStatus:
                model = "(?<=\>)(.*?)(?=\<)"
                tempList = re.findall(model, str(status))
                resuList = []
                if(len(tempList) == 27):
                    for i in self.unusalList:
                        resuList.append(tempList[int(i)])
                else:
                    for i in self.usallyList:
                        resuList.append(tempList[int(i)])
                statusList.append(resuList)

            print("get statusList: " + str(len(statusList)) +" records")
            return statusList
        except:
            print("get statusList failure")
            return []


    ## 抓了 100 页的信息
    def getStatus(self):
        if self.getConn('root', '', 'localhost', 'test'):
            for i in range(1, 100):
                page = self.session.get(self.nextStatusUrl)
                statusList = self.getStatusList(page)
                if(statusList == []):
                    sleep(5)
                    continue
                self.insertData(statusList)
                sleep(3)

            self.cursor.close()
            self.conn.close()


if __name__ == '__main__':

    poj = POJStatus()
    poj.getStatus()

