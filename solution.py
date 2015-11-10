import re
import os
import requests
from time import sleep
from bs4 import BeautifulSoup

class POJSubmit:

    POJUrl = 'http://poj.org/'
    currPageUrl = 'http://poj.org/status'
    nextPageUrl = 'http://poj.org/status'
    usallyList = {1, 4, 8, 12, 15, 17, 20, 23, 25}
    hds = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}

    # 初始化参数
    def __init__(self, userName, password):
        self.userName = userName
        self.password = password
        self.sleepTime = 3
        self.session = requests.session()

    # 用来处理测评状态, 只保留结果的每个单词的首字母, 
    # 例如 Wrong Answer 处理为 WA
    def Map(self, Result):
        res = ""
        for string in Result.split(" "):
            res = res + string[0]
        if(len(res) == 1): res = res + "C"
        return res

    # 用户登录 
    def login(self):
        loginUrl = self.POJUrl + 'login'
        user_id1 = self.userName
        password1 = self.password
        hds = self.hds
        session = self.session
        userData = {'user_id1':user_id1, 'password1':password1, 'B1':'login', 'url':'submit?problem_id=0'};

        loginRes = session.post(url = loginUrl, data = userData, headers = hds);
        if re.search('Log Out', loginRes.text):
            print("login successful")
            return True
        else:
            print("login failure")
            return False
    

    # 得到用户通过的题目的题号  
    # return problemList:list
    def getProblemList(self):
        userName = self.userName
        url = 'http://poj.org/userstatus?user_id=' + userName;
        page = requests.get(url);
        if re.search('(?<=p\()(\d{4})(?=\))', page.text):
            print("getProblemList successful")
            return re.findall('(?<=p\()(\d{4})(?=\))', page.text)
        else: 
            print("getProblemList failure")
            return []


    # 得到某一页提交状态中的所有提交记录, 每条记录也是一个 list, 同时得到下一页提交状态的连接， 保存在 self.nextPageUrl 中
    # return solutionList = {{runId, user, problem_id, result, memory, time, language, codeLength, submitTime}}:list
    def getOneProSolutionList(self, page):

        if(re.search('\<a href=(status\?problem_id=\d{4}.user_id=' + self.userName + '.top=\d+?)\>', page.text)):
            self.nextPageUrl = self.POJUrl + str(re.findall('\<a href=(status\?problem_id=\d{4}.user_id=' + self.userName +'.top=\d+?)\>', page.text)[0])
        else: return []
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.findAll('table', {'class':'a'})
        soup = BeautifulSoup(str(table), "html.parser")
        allSolution = soup.findAll('tr', {'align':'center'})
        solutionList = []
        for solution in allSolution:
            model = "(?<=\>)(.*?)(?=\<)"
            tempList = re.findall(model, str(solution))
            resuList = []
            if(len(tempList) == 29): resuList = []
            else:
                for i in self.usallyList:
                    resuList.append(tempList[int(i)])
            solutionList.append(resuList)

        print("get oneProSolutionList: " + str(len(solutionList)) +" records")

        return solutionList

    
    # 得到某页提交状态上的所有显示代码的链接
    # return linkList:list
    def getLinkList(self, page):
        model = "\<a href=(showsource\?solution_id=.+?) target=_blank\>.+?\</a\>"
        if re.search(model, page.text):
            linkList = re.findall(model, page.text)
            return linkList
        else : return []

    # 得到代码内容
    # return text
    def getFileText(self, link):
        session = self.session
        sourceLink = self.POJUrl + link
        page = session.get(url = sourceLink);
        soup = BeautifulSoup(page.text, "html.parser")
        tag = soup.find_all("pre")[0]
        fileText = tag.get_text().replace('\r', '')
        return fileText;
    
    # 代码文件名 problem_id + "_" + yymmdd-hhmmss + "_" + memory +"_" + time +"_"+ result
    def getFileName(self, oneProSolution):
        submitTime = oneProSolution[8]
        ymd = submitTime.split(" ")[0]
        hms = submitTime.split(" ")[1]
        submitDay = ""
        for i in ymd.split("-"):
            submitDay = submitDay + i
        submitDay = submitDay +"-"
        for i in hms.split(":"):
            submitDay = submitDay + i
        fileName = oneProSolution[2]
        fileName = fileName + "_" + submitDay
        fileName = fileName + "_" + oneProSolution[4]
        fileName = fileName + "_" + oneProSolution[5]
        fileName = fileName + "_" + self.Map(oneProSolution[3])
        if(oneProSolution[6] == "G++" or oneProSolution[6] == "C++" or oneProSolution[6] == "C"):
            fileName = fileName + ".cpp"
        else: fileName = fileName +".java"

        print(fileName)

        return fileName

    # 创建文件夹，每道题一个文件夹
    def mkdir(self, path):
    	path = path.strip()
    	path = path.rstrip("\\")
    	isExists = os.path.exists(path)
    	if not isExists:
    		os.makedirs(path)
    		print("makedirs " + path +" successful")
    		return True
    	else:
    		print("makedirs " + path +" failure")
    		return False
        
    # 将代码文件保存下来
    def writIntoFile(self, fileText, filePath):
        fileName = filePath
        i = 0;
        # 解决重名问题
        while os.path.isfile(fileName):
            fileName = filePath.split(".")[0] + str(i) + "." + filePath.split(".")[1]
            i = i + 1
        fp = open(fileName, 'w', encoding="utf-8")
        fp.write(fileText)
        fp.close()

        print("write " + fileName +" file successful")


    # 解析并保存一页提交状态上的所有代码
    def getDataAndSave(self, problem_id, currPageUrl, filePath):

        session = self.session
        userName = self.userName
        page = session.get(url = currPageUrl);
        oneProSolutionList = self.getOneProSolutionList(page)
        linkList = self.getLinkList(page)

        pageSolutionNum = len(oneProSolutionList)
        linkNum = len(linkList)

        print("soluNum = " + str(pageSolutionNum))
        print("linkNum = " + str(linkNum))

        if linkNum == 0:
            sleep(10)
            print(page.text)
            self.login()
            sleep(10)
            return self.getDataAndSave(problem_id, currPageUrl, filePath)

        for i in range(0, pageSolutionNum):
            oneProSolution = oneProSolutionList[i]
            if len(oneProSolution) == 0: continue
            sleep(self.sleepTime)
            fileText = self.getFileText(linkList[i])
            fileName = self.getFileName(oneProSolution)
            self.writIntoFile(fileText, filePath + fileName)

        return pageSolutionNum


    # 遍历所有通过的题目, 保存代码
    def getSolution(self):
        userName = self.userName
        problemList = self.getProblemList()
        sleep(self.sleepTime)
        self.login()
        for problem_id in problemList:

            print("problem_id = " + str(problem_id))

            filePath = "D:\\" + self.userName + "_POJSubmit\\" + str(problem_id) +"\\"
            self.mkdir(filePath)
            currPageUrl = self.POJUrl + 'status?problem_id='+problem_id+'&user_id='+userName+'&result=&language='
            pageSolutionNum = self.getDataAndSave(problem_id, currPageUrl, filePath)
            sleep(self.sleepTime)
            while self.nextPageUrl != currPageUrl and pageSolutionNum == 20:
                currPageUrl = self.nextPageUrl
                pageSolutionNum = self.getDataAndSave(problem_id, currPageUrl, filePath)
                sleep(self.sleepTime)

            print("save " + problem_id + " code successful")

        print("allSolution save successful")



if __name__ == '__main__':

    userName = input("请输入用户名: ")
    password = input("请输入密码:   ")
    pojSubmit = POJSubmit(userName, password) 
    pojSubmit.getSolution() 

