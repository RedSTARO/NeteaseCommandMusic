import configparser
import json
import os
import time
import webbrowser
import requests
import threading
import subprocess

configPath = "./config/"

config = configparser.ConfigParser()
config.read(configPath + "config.ini")
server = config['system']['server']


def DEBUG(info):
    print(f"DEBUG: {info}")


def show(text, sleep=0, refresh=False):
    if refresh:
        print("\033[F\033[K", end="")
    print(text)
    time.sleep(sleep)


def jsonUpdater(newKey, newValue, file, mode="w"):
    file = configPath + file
    with open(file, "r", encoding="utf-8") as f:
        file_content = f.read().strip()
        if len(file_content) == 0:
            existing_data = {}
        else:
            existing_data = json.loads(file_content)
    existing_data[newKey] = newValue
    with open(file, mode, encoding="utf-8") as f:
        f.write(json.dumps(existing_data, ensure_ascii=False))
        f.write('\n')


def jsonReader(key, file):
    file = configPath + file
    with open(file, 'r', encoding="utf-8") as f:
        file_content = f.read().strip()
        if len(file_content) == 0:
            return "EmptyFile"
        else:
            data = json.loads(file_content)
    return data[key]

def downloader(url, pathToFile):
    command = f'aria2c -x 16 -s 16 -d "{pathToFile}" "{url}" --file-allocation=none '
    subprocess.call(command, shell=True)
    # Disable output info
    # with open(os.devnull, 'w') as devnull:
    #     subprocess.run(command, shell=True, stdout=devnull, stderr=subprocess.STDOUT)

class User():

    # Login
    def getCookie(self):
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
        # Check if login successful
        while True:
            time.sleep(1)
            req = requests.get(server + f"/login/qr/check?key={qrCodeKey}&timestamp={int(time.time() * 1000)}")
            scanStauts = json.loads(req.text)
            if scanStauts["code"] == 803:
                # Write cookie as a mode to clear history
                jsonUpdater("cookie", scanStauts["cookie"], "user.json", mode="w")
                return True

    # User profile
    def getUserDetails(self):
        # Get user details
        req = requests.get(server + f"/user/account?cookie={jsonReader('cookie', 'user.json')}")
        data = json.loads(req.text)
        # DEBUG(data)
        jsonUpdater("id", data["account"]["id"], "user.json")
        jsonUpdater("name", data["profile"]["nickname"], "user.json")
        jsonUpdater("avatarUrl", data["profile"]["avatarUrl"], "user.json")
        jsonUpdater("backgroundUrl", data["profile"]["backgroundUrl"], "user.json")

    # User playlist
    def getPlaylist(self):
        # Get play list info
        req = requests.get(
            server + f"/user/playlist?cookie={jsonReader('cookie', 'user.json')}&uid={jsonReader('id', 'user.json')}&timestamp={int(time.time() * 1000)}")
        data = json.loads(req.text)["playlist"]
        # Get songs in playlist
        for listCount in range(0, len(data)):
            show(f"Getting list: {data[listCount]['name']}", refresh=True)
            req = requests.get(
                server + f"/playlist/track/all?cookie={jsonReader('cookie', 'user.json')}&id={data[listCount]['id']}")
            details = json.loads(req.text)
            jsonUpdater(listCount, {"id": f"{data[listCount]['id']}",
                                    "name": f"{data[listCount]['name']}",
                                    "backgroundUrl": f"{data[listCount]['coverImgUrl']}",
                                    "details": details},
                        "playList.json")
        return len(data)

class Song():
    def getMusicByJson(self, download=True):
        with open(configPath + "playList.json", 'r', encoding="utf-8") as f:
            file_content = f.read().strip()
            fileData = json.loads(file_content)
        # Search song list
        for i in range(0, len(fileData)):
            # Search songs in list
            for j in range(0, len(fileData[str(i)]["details"]["songs"]) - 1):
                try:
                    if download == True:
                        folderName = str(fileData[str(i)]["details"]["songs"][j]["id"])
                        folderPath = os.path.join("./songs/", folderName)
                        # Create folder
                        if (not os.path.exists(folderPath)):
                            os.makedirs(folderPath)
                        # if folder is empty
                        if len(os.listdir(folderPath)) == 0:
                            data = self.getPlayURLByID(folderName)
                            link = data["data"][0]["url"]
                            show("Downloading " +  str(fileData[str(i)]["details"]["songs"][j]["name"]) + f" ({folderName}{os.path.splitext(link)[1]})", refresh=True)
                            downloader(link, f"./songs/{folderName}/{folderName}{os.path.splitext(link)[1]}")
                except TypeError:
                    DEBUG(os.path.splitext(link)[1])

    def getPlayURLByID(self, id, level="jymaster"):
        # standard => 标准,higher => 较高, exhigh=>极高, lossless=>无损, hires=>Hi-Res, jyeffect => 鲸云臻音, jymaster => 鲸云母带
        req = requests.get(server + f"/song/url/v1?id={id}&level={level}&cookie={jsonReader('cookie', 'user.json')}")
        data = json.loads(req.text)
        return data


if __name__ == "__main__":
    # user = User()
    song = Song()
    song.getMusicByJson()
