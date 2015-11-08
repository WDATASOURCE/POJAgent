# -*- coding: utf-8 -*-
import re
import time
import requests

# 登录
def login(user_id1, password1, hds, session):
    loginUrl = 'http://poj.org/login';
    userData = {'user_id1':user_id1, 'password1':password1, 'B1':'login', 'url':'submit?problem_id=0'};
    try:
        loginRes = session.post(url = loginUrl, data = userData, headers = hds);
        if re.search('Log Out', loginRes.text):
            return True
        else:
            return False
    except:
        return False

# 提交程序
def submit(problem_id, language, source, hds, session):
    submitUrl = 'http://poj.org/submit';
    submitData = {'problem_id': problem_id,'language': language,'source': source, 'encoded':'0', 'submit':'Submit'};
    
    try:
        submitRes = session.post(url = submitUrl, data = submitData, headers = hds)
        return True
    except:
        return False

# 获取提交结果
def getResult(problem_id, user_id1, hds, session):
    statusUrl = 'http://poj.org/status?problem_id='+problem_id+'&user_id='+user_id1+'&result=&language='
    usallyList = {1, 4, 8, 12, 15, 17, 20, 23, 25}
    unusalList = {1, 4, 8, 13, 14, 15, 22, 25, 27}

    try:
        userAllStatus = session.get(url = statusUrl, headers = hds);
        model = "\<tr.+\>.+?"+user_id1+".+?\</tr\>"
        userLastStatus = (re.findall(model, userAllStatus.text))[0]
        model = "(?<=\>)(.*?)(?=\<)"
        tempList = re.findall(model, userLastStatus)
        status = []
        if(len(tempList) == 29):
            for i in unusalList:
                status.append(tempList[int(i)])
        else:
            for i in usallyList:
                status.append(tempList[int(i)])
        return status
    except:
        return []

# 将评判结果返回
def result(problem_id, user_id1, hds, session):
    resultCode = {'Accepted', 'Presentation Error', 'Time Limit Exceeded', 'Memory Limit Exceeded', 'Wrong Answer', 'Runtime Error', 'Output Limit Exceeded', 'Compile Error', 'System Error', 'Validator Error'}
    status = getResult(problem_id, user_id1, hds, session)
    while(len(status) and (status[3] not in resultCode)):
        time.sleep(3)
        status = getResult(problem_id, user_id1, hds, session)
    return status


if __name__ == '__main__':

    user_id1 = input("请输入用户名:")
    password1 = input("请输入密码:")
    session = requests.session()
    hds = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
    problem_id = '1000'
    language = '0'
    source = """
    #include <iostream>
    using namespace std;
    int main(){
        int a, b;
        while(cin >> a >> b){
            cout << a + b << endl;
        }
        return 0;
    }
    """

    if login(user_id1, password1, hds, session):
        print("登录成功")
        if submit(problem_id, language, source, hds, session):
            print("提交成功")
            print(result(problem_id, user_id1, hds, session))
        else: print("提交失败")
    else: print("登录失败")

