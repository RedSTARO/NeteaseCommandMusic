from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style
from rich.color import Color
from rich import print
import cv2
import numpy as np
from sklearn.cluster import KMeans
import builtins
from core import *

# 创建控制台对象
console = Console()

# 设置样式
title_style = Style(color="cyan", bold=True)
info_style = Style(color="green")
error_style = Style(color="red")
input_style = Style(color="magenta")


def picColor(path):
    # Read image
    image = cv2.imread("./config/user/avatar.jpg")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Adjust image shapr to (n_pixels, 3), use every pixel
    pixels = image_rgb.reshape(-1, 3)

    # Run K-Means
    n_colors = 1  # K-Means amount, also output color amount
    kmeans = KMeans(n_clusters=n_colors, n_init=10)
    kmeans.fit(pixels)

    # Extract the center points of the clustering result, which are the accent colors
    colors = kmeans.cluster_centers_.astype(int)

    # Output
    for color in colors:
        r, g, b = color
    return color


def show(text, sleep=0, refresh=False, style=Style(color="green")):
    if refresh:
        builtins.print("\033[F\033[K", end="")
    console.print(text, style=style)
    time.sleep(sleep)


# Clear screen
console.clear()
# Show title
show("NeteaseCommandMusic", style=title_style)
# Create user
user = User()
# Check login status
if jsonReader("cookie", "user.json") == "EmptyFile":
    show("Not login, please login now.")
    if user.getCookie():
        show("Login finished.")
else:
    show("Login status detected.")

show("Reading user info.")
user.getUserDetails()

show("Updating playlist")
show("Total list: " + str(user.getPlaylist()), refresh=True)

show("Update playlist finished.", sleep=1)

# Get user info
user.getUserDetails()

# Show user info
downloader(jsonReader('avatarUrl', 'user.json'), "./config/user/avatar.jpg")
# Get pic theme color
rgb = picColor("./config/user/avatar.jpg")
show(f"Welcome, {jsonReader('name', 'user.json')}!", style=Style(color=Color.from_rgb(rgb[0], rgb[1], rgb[2])))
show("")


# Command functions
class Command:
    def execute(self):
        pass

class DownloadAll(Command):
    def execute(self):
        song = Song()
        song.getMusicByJson(download=True)
# command list
commands = {
    "download all": DownloadAll()
}

# main cycle
while True:
    console.print("NeteaseCommandMusic> ", style=input_style, end="")
    command_input = input().lower()

    if command_input in commands:
        command = commands[command_input]
        command.execute()
    elif command_input == "quit":
        console.print("Although life is hard, music always waits for you here. Bye~",
                      style=Style(color=Color.from_rgb(255, 105, 180)))
        break
    else:
        console.print("Command Not Found.")
