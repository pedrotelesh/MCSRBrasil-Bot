from math import floor
from urllib.request import urlopen
from ujson import loads
import json
import os
import aiohttp
import urllib.parse
from cachetools import TTLCache

RSG_CACHE = TTLCache(maxsize=1024, ttl=600)
SSG_CACHE = TTLCache(maxsize=1024, ttl=600)

from utilities import config_loader as config

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

async def fetch_google_script_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=False) as resp:
            if resp.status in (301, 302, 303, 307, 308):
                redirect_url = resp.headers.get('Location')
                if redirect_url:
                    async with session.get(redirect_url) as final_resp:
                        return await final_resp.json(content_type=None)
                else:
                    raise Exception('Redirecionamento sem Location header')
            else:
                return await resp.json(content_type=None)

async def get_top_runs(tipo: str):
    runners_url = None
    try:
        runners_url = config.config.get('RUNNERS_API')
    except Exception:
        pass
    runners_data = []
    runners_map = {}
    if runners_url:
        try:
            runners_data = await fetch_google_script_json(runners_url)
        except Exception:
            runners_data = []
    if isinstance(runners_data, dict) and 'runners' in runners_data:
        runners_data = runners_data['runners']
    for entry in runners_data:
        if len(entry) >= 4:
            nome_runner, estado, cor, runner_id = entry[:4]
            runners_map[nome_runner.lower()] = runner_id
    url = tipo
    cache = None
    if 'getrsg116' in tipo:
        cache = RSG_CACHE
    elif 'getssg116' in tipo:
        cache = SSG_CACHE

    if cache is not None and tipo in cache:
        data = cache[tipo]
    else:
        data = await fetch_google_script_json(url)
        if cache is not None:
            cache[tipo] = data
    results = []
    runs = data["runs"] if isinstance(data, dict) and "runs" in data else data
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    action = query.get('action', [''])[0].lower()
    is_rsg = action == 'getrsg116'
    is_ssg = action == 'getssg116'

    top_emotes = [
        '<:gold_ingot:1390146844344062055>',
        '<:iron_ingot:1390146833485140018>',
        '<:copper_ingot:1390146817173360700>'
    ]
    emote_gold_block = '<:gold_block:1390147037902803084>'
    emote_clock = '<:clock:1390146877009170483>'
    emote_seed = '<:seed:1390146860697784370>'

    if cache is not None and tipo not in cache:
        cache[tipo] = data

    for idx, run in enumerate(runs):
        place_emote = top_emotes[idx] if idx < 3 else f'#{idx+1}'
        if is_rsg:
            if len(run) == 8:
                nome, tempo, bastion, data_run, verificada, seed, video, comentario = run
            elif len(run) == 7:
                nome, tempo, bastion, data_run, verificada, seed, video = run
                comentario = ''
            else:
                print('[ERRO] Erro ao desempacotar RSG: formato inesperado', run)
                continue
            runner_id = runners_map.get(nome.lower())
            username_str = None
            profile_url = None
            if runner_id:
                try:
                    username_str = username(runner_id)
                    if username_str:
                        profile_url = f"https://www.speedrun.com/users/{username_str}"
                except Exception as e:
                    print(f"[ERRO] Exception ao buscar username/profile: {e}")
            results.append({
                "place": place_emote,
                "nome": nome,
                "profile": profile_url,
                "tempo": tempo,
                "bastion": bastion,
                "data": data_run,
                "verificada": verificada,
                "seed": seed,
                "video": video,
                "comentario": comentario
            })
        elif is_ssg:
            # SSG: 7 ou 6 colunas
            if len(run) == 7:
                nome, tempo, seed_name, data_run, verificada, video, comentario = run
            elif len(run) == 6:
                nome, tempo, seed_name, data_run, verificada, video = run
                comentario = ''
            else:
                print('[ERRO] Erro ao desempacotar SSG: formato inesperado', run)
                continue
            runner_id = runners_map.get(nome.lower())
            username_str = None
            profile_url = None
            if runner_id:
                try:
                    username_str = username(runner_id)
                    if username_str:
                        profile_url = f"https://www.speedrun.com/users/{username_str}"
                except Exception as e:
                    print(f"[ERRO] Exception ao buscar username/profile: {e}")
            results.append({
                "place": place_emote,
                "nome": nome,
                "profile": profile_url,
                "tempo": tempo,
                "seed_name": seed_name,
                "data": data_run,
                "verificada": verificada,
                "video": video,
                "comentario": comentario
            })
        else:
            print('[ERRO] Tipo de run desconhecido para parsing:', url)
            continue
    return results

def get_links_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'links.json')

def save_links(data):
    path = get_links_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_links():
    path = get_links_path()
    if not os.path.exists(path):
        return {"youtube": None, "twitch": None, "tiktok": None}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")