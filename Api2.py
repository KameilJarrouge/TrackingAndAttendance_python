import requests
import io
import matplotlib.pyplot as plt

baseUrl = "http://127.0.0.1:8000"


res = requests.post(baseUrl+"/api/login",
                    {"username": "kamil", "password": "kamil"})
user = res.json()
heads = {"Authorization": "Bearer " + user['token']}


def getData(url):
    res = requests.get(baseUrl+url, headers=heads)

    if (res.status_code == "500" or res.status_code == 500):
        return "error 500"
    return res.json()


# def sendGetRequest(url):
#     res = requests.get(baseUrl + url,  headers=heads)
#     return res.json()


# def sendPostRequest(url, data, files, headers={}):
#     res = requests.post(baseUrl + url, data, files=files,
#                         headers=heads | headers)
#     if res.status_code == 500 or res.status_code == "500":
#         print("error 500")
# "Content-Type": "multipart/form-data"


def sendRequest(url, data, files):
    res = requests.post(url=baseUrl + url, params=data, files=files,
                        headers=heads)
    # print(res.json())
    if res.status_code == 500 or res.status_code == "500":
        print(res.json())


def sendRequestWithoutFiles(url, data):
    res = requests.post(url=baseUrl + url, params=data,
                        headers=heads)
    # print(res.json())
    if res.status_code == 500 or res.status_code == "500":
        print(res.json())


def fetchASubjectById(id):
    res = requests.get(baseUrl+"/api/given-subjects/" +
                       str(id)+"/python-subject", headers=heads)
    print(res.json())
    if res.status_code == 500 or res.status_code == "500":
        print(res.json())
    return res.json()


# fetchASubjectById(2)
# cap = cv2.VideoCapture(0)
# ret, camFrame = cap.read()


def getSendableImage(frame):
    buf = io.BytesIO()
    plt.imsave(buf, frame, format='png')
    image_data = buf.getvalue()
    return image_data


def getSendableList(list):
    listAsString = ""
    for l in list:
        listAsString += str(l) + ","
    if listAsString == "":
        return "empty"
    return listAsString[:-1]


# sendRequest('/api/given-subjects/2/attendance-python', {
#     'recognitions': json.dumps([1, 13, 122]),
#     'profAttId': 12,
#     'isAttended': True
# }, {"frame":  getSendableImage(camFrame)})
