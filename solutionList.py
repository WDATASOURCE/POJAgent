# -*- coding: utf-8 -*-

import re
import requests

userName = input('请输入用户名：')
url = 'http://poj.org/userstatus?user_id=' + userName;
r = requests.get(url);
data = r.text

problemList = re.findall('(?<=p\()(\d{4})(?=\))', data)

print (problemList)
