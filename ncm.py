from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style
from core import *

# 创建控制台对象
console = Console()

# 设置样式
title_style = Style(color="cyan", bold=True)
info_style = Style(color="white")
error_style = Style(color="red")

# 显示标题
console.print("网易云音乐", style=title_style)

# 创建用户对象
user = User()

# 检查登录状态
if jsonReader("cookie", "user.json") == "EmptyFile":
    console.print("Not login, please login now.")
    if user.getCookie():
        console.print("Login finished.")
else:
    console.print("Login status detected.")

console.print("Reading user info.")
user.getUserDetails()

console.print("Updating playlist")
user.getPlaylist()


console.print("Update playlist finished.",)
