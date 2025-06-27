from math import floor
from urllib.request import urlopen
from ujson import loads
import json
import os
import aiohttp

month = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]

ordinal = lambda n: "%d%s" % (
    n,
    "tsnrhtdd"[(floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
)

def pformat(s):
    s = s.replace(" ", "_")
    for eachchar in "%()":
        s = s.replace(eachchar, "")
    return s

def makelist(arr):
    output = ""
    for i in range(len(arr)):
        output += arr[i]
        if i < len(arr) - 1 and len(arr) > 2:
            output += ", "
        if i == len(arr) - 2:
            if len(arr) <= 2:
                output += " "
            output += "and "
    return output

def realtime(time):
    ms = int(time * 1000)
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    ms = "{:03d}".format(ms)
    s = "{:02d}".format(s)
    if h > 0:
        m = "{:02d}".format(m)
    return (
        ((h > 0) * (str(h) + "h "))
        + str(m)
        + "m "
        + str(s)
        + "s "
        + ((str(ms) + "ms") * (ms != "000"))
    )  # src formatting

def userid(username):
    with urlopen("https://www.speedrun.com/api/v1/users/" + username) as url:
        userdata = loads(url.read().decode())
        return userdata["data"]["id"]
    
def username(userid):
    with urlopen("https://www.speedrun.com/api/v1/users/" + userid) as url:
        userdata = loads(url.read().decode())  # gets information from speedrun.com api
        return userdata["data"]["names"][
            "international"
        ]  # reads the international name from api
    
def userdata(userid):
    with urlopen("https://www.speedrun.com/api/v1/users/" + userid) as url:
        userdata = loads(url.read().decode())  # gets information from speedrun.com api
        return userdata["data"]  # returns the data dictionary of the user
    
async def get_top_runs(url):
    with open("users.json", "r", encoding="utf-8") as f:
        users_data = json.load(f)["users"]
    id_to_name = {user["id"]: user["name"] for user in users_data}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    runs = data["data"]["runs"]
    results = []
    for run in runs:
        run_data = run["run"]
        time = run_data["times"]["primary_t"]
        run_link = run_data.get("weblink", "")
        for player in run_data["players"]:
            if player["rel"] == "user":
                user_id = player["id"]
                if user_id in id_to_name:
                    username = id_to_name[user_id]
                    user_link = f"https://www.speedrun.com/user/{username}"
                    results.append((time, username, run_link, user_link))
    results.sort()
    return results

def get_yt_tt_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'yt_tt_links.json')

def save_yt_tt_links(data):
    path = get_yt_tt_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_yt_tt_links():
    path = get_yt_tt_path()
    if not os.path.exists(path):
        return {"youtube": None, "twitch": None, "tiktok": None}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")