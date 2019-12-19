import requests
from bs4 import BeautifulSoup
import json
import subprocess
import os
import tkinter
import time

base_path = os.path.split(os.path.realpath(__file__))[0]
config_file = os.path.join(base_path, "ss/gui-config.json")
exe_file = os.path.join(base_path, "ss/Shadowsocks.exe")

pre_url = "http://isx.yt"
# url = "https://a.ishadowx.net"
pre = requests.get(pre_url, allow_redirects=False, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'})
url = pre.headers["Location"]

template = '''[[server:"{ip}",server_port:"{port}",password:"{psd}",method:"{method}"]]'''

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Host": url.split('://')[1][:-1],
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',

    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",

    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Cookie": "_gat=1; _ga=GA1.2.457697903.1522483798; _gid=GA1.2.789822428.1522483798",

    "If-None-Match": "6b8e-568b02f8eddb2-gzip",
    "If-Modified-Since": "Sat, 31 Mar 2018 07:20:04 GMT",
}


def getUrl():
    return url


def fetchConfig():
    print(url)
    try:
        r = requests.get(url, headers=header, timeout=15)

        document = BeautifulSoup(r.text, "html.parser")

        items = document.find_all(class_="portfolio-item")

        configs = []
        for i in items:
            try:
                h = i.find_all("h4")
                ip = h[0].span.text.strip().replace("\n", "")
                port = h[1].span.text.strip().replace("\n", "")
                psd = h[2].span.text.strip().replace("\n", "")
                method = h[3].text[7:].strip().replace("\n", "")
                if ip and port and psd and method:
                    item = {"server": ip,
                            "server_port": port,
                            "password": psd,
                            "method": method,
                            "plugin": "",
                            "plugin_opts": "",
                            "plugin_args": "",
                            "remarks": "",
                            "timeout": 5}
                    configs.append(item)
            except Exception as e:
                print("配置无效")

        with open(config_file, 'r') as f:
            content_json = json.load(f)
            content_json["configs"] = configs

        with open(config_file, 'w') as f:
            json.dump(content_json, f)

        return True
    except Exception as e:
        print(e)
        return False


def startProgram():
    return subprocess.Popen(exe_file)


if __name__ == '__main__':
    # fetchConfig()
    a = startProgram()
    time.sleep(1)
    print(a.kill())
