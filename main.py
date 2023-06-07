import requests
import configparser
import json
import time
import webbrowser
import os
config = configparser.ConfigParser()
DEBUG = True

# Read config
path = "./config/"
config.read(path + "config.ini")
server = config['system']['server']


def jsonUpdater(newKey, newValue, file, mode="w"):
    file = path + file
    with open(file, "r") as f:
        file_content = f.read().strip()
        if len(file_content) == 0:
            existing_data = {}
        else:
            existing_data = json.loads(file_content)
    existing_data[newKey] = newValue
    with open(file, mode) as f:
        f.write(json.dumps(existing_data))
        f.write('\n')


def jsonReader(key, file):
    file = path + file
    with open(file, 'r') as f:
        data = json.load(f)
    return data[key]


# Login
def login():
    # via QR code
    # ask for login unikey
    req = requests.get(server + f"/login/qr/key?timestamp={int(time.time() * 1000)}")
    if DEBUG:
        print("reqAdd: " + f"/login/qr/key?timestamp={int(time.time() * 1000)}")
    qrCodeKey = json.loads(req.text)["data"]["unikey"]
    if DEBUG:
        print("qrCodeKey: " + qrCodeKey)
    # generate QR base64
    req = requests.get(server + f"/login/qr/create?key={qrCodeKey}&qrimg=ture&timestamp={int(time.time() * 1000)}")
    qrImg = json.loads(req.text)["data"]["qrimg"]
    # open QR code in browser
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login QR Code</title>
    </head>
    <body>
        <h1>Plz scan this code to login.</h1>
        <img id=qrImg alt="QR Code" src={qrImg}>
    </body>
    </html>
    """
    html_filename = f"{os.path.dirname(os.path.abspath(__file__))}/temp/qrcode.html"
    with open(html_filename, "w") as html_file:
        html_file.write(html_content)
    webbrowser.open(html_filename)
    print("Plz scan code in browser.")
    # Check if login successful
    while True:
        time.sleep(1)
        req = requests.get(server + f"/login/qr/check?key={qrCodeKey}&timestamp={int(time.time() * 1000)}")
        scanStauts = json.loads(req.text)
        if scanStauts["code"] == 802:
            print("Scan successful, click button on your phone.")
        elif scanStauts["code"] == 803:
            # Write cookie as a mode to clear history
            jsonUpdater("cookie", scanStauts["cookie"], "user.json", mode="w")
            print("Login successful.")
            print("Reading user info.")
            # Get user id
            req = requests.get(server + f"/user/account?cookie={jsonReader('cookie', 'user.json')}")
            data = json.loads(req.text)
            jsonUpdater("id", data["account"]["id"], "user.json")
            break


# User playlist
def getPlaylist():
    req = requests.get(server + f"/user/playlist?cookie={jsonReader('cookie', 'user.json')}&uid={jsonReader('id', 'user.json')}")
    data = json.loads(req.text)["playlist"]
    for listCount in range(0, len(data)):
        req = requests.get(server + f"/playlist/track/all?cookie={jsonReader('cookie', 'user.json')}&id={data[listCount]['id']}")
        details = json.loads(req.text)
        jsonUpdater(listCount, {"id": f"{data[listCount]['id']}",
                                "name": f"{data[listCount]['name']}",
                                "backgroundUrl": f"{data[listCount]['coverImgUrl']}",
                                "details": details},
                    "playList.json")
    print("Get play list finished.")


if __name__ == "__main__":
    # login()
    getPlaylist()