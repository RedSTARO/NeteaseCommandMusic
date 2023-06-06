import requests
import configparser
import json
import time
import webbrowser
import os
config = configparser.ConfigParser()

# Read config
path = "./config.ini"
config.read(path)
server = config['system']['server']

# Login
def login():
    # via QR code
    # ask for login unikey
    req = requests.get(server + f"/login/qr/key?timestamp={int(time.time() * 1000)}")
    qrCodeKey = json.loads(req.text)["data"]["unikey"]
    # generate QR base64
    req = requests.get(server + f"/login/qr/create?key={qrCodeKey}&qrimg=ture&timestamp={int(time.time() * 1000)}")
    qrImg = json.loads(req.text)["data"]["qrimg"]
    # open QR code in browser
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Code</title>
    </head>
    <body>
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
            if "user" in config:
                config.set("user", "cookie", scanStauts["cookie"])
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            print("Login successful.")
            break
        elif scanStauts["code"] == 801:
            print("Code not usable.")
    # TODO:wirtten into json
# Account detail
def accountDetail():
    req = requests.get(server + f"/user/account?cookie={config['user']['cookie']}")
    data = json.loads(req.text)
    config.set("user", "id", str(data["account"]["id"]))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    # TODO:wirtten into json

# User playlist
def getPlaylist():
    req = requests.get(server + f"/user/playlist?cookie={config['user']['cookie']}&uid={config['user']['id']}")
    data = json.loads(req.text)
    # TODO:wirtten into json