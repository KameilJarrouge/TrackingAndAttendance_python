from email import header
import urllib3
import json
import requests

baseUrl = "http://127.0.0.1:8000"


count = 0
api = urllib3.PoolManager(
    headers={"content-type": "application/json", "Accept": "application/json"})
res = api.request('POST', baseUrl+"/api/login",
                  {"username": "kamil", "password": "kamil"})
user = json.loads(res.data.decode('utf-8'))
heads = {"Authorization": "Bearer " + user['token']}

# def login():
#     res = api.request('POST', baseUrl + "/api/login",
#                       {"username": "python_main", "password": "Breaking the habit 2n8"})
#     user = json.loads(res.data.decode('utf-8'))
#
# print("fuck you I'm logged in")


def getData(url):
    res = api.request('GET', baseUrl+url, headers=heads)
    if (res.status == "500"):
        return "error 500"
    return json.loads(res.data.decode('utf-8'))


def dumpJson(jsonData):
    return json.dumps(jsonData, indent=2, sort_keys=True)


def sendRequest(method, url, data, headers, isJson):
    global count
    if isJson:
        res = api.request(method=method, url=baseUrl +
                          url, body=data, headers=heads | headers)
    else:

        res = api.request(method=method, url=baseUrl +
                          url, body=data, headers=heads | headers)

    if (res.status == "500" or res.status == 500):
        count += 1
        print('writing error to output.html')
        file = open('output'+str(count)+'.html', 'w')
        file.write(res.data.decode('utf-8'))
        file.flush()
        file.close()
    else:
        print(res.status)
    # print(res.data.decode('utf-8'))
