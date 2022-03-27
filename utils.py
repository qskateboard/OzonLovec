import random
from datetime import datetime
import requests


def save_file(file, text):
    f = open("accounts/" + file + ".txt", "w")
    f.write(text)
    f.close()


def read_file(file):
    try:
        f = open("accounts/" + file + ".txt", "r")
        return f.read()
    except:
        f = open("accounts/" + file + ".txt", "w")
        f.close()
        return ""


def rnd_proxy(filename):
    proxies_read = open(filename)
    proxies_read = str(proxies_read.read()).split('\n')
    i = random.randint(0, len(proxies_read) - 1)
    return proxies_read[i]


def get_time():
    return datetime.now()


def get_product(uid):
    url = "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fproducts%2F{}%2F%3Fminiapp%3Dsupermarket%26stat%3DYW5fMQ%253D%253D".format(str(uid))
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_6_6 rv:6.0) Gecko/20150501 Firefox/36.0"
    }
    r = requests.get(url, headers=headers)
    r = r.json()
    product = None
    for param in r["pdp"]["addToFavorite"]:
        if product is None:
            product = r["pdp"]["addToFavorite"][param]['cellTrackingInfo']['product']
    img = None
    for gallery in r["pdp"]["webGallery"]:
        if img is None:
            img = r["pdp"]["webGallery"][gallery]["coverImage"]
    result = {
        "name": product["title"],
        "url": product["link"],
        "price": str(product["price"]),
        "img": img,
    }
    return result