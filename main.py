import glob
import sys
import threading, queue
import multiprocessing
import time
import traceback

import discordManager
import utils
from ozonManager import ozonManager
from ozonWorker import ozonWorker

items = [
    "178337786",
    "178715781",
    "207702520",
    "207702519",
    "216940493",
    "173667655",
]

accounts = []
api = []
workers = []


def progrev(apis):
    apis.add_to_cart("228058566")
    apis.progrev_checkout()
    apis.removeCart("228058566")


def check_account(apis):
    user = apis.get_user()
    if user is None:  # auth
        apis.auth()
        time.sleep(1)
        user = apis.get_user()
    time.sleep(1)
    # print(apis.myOrders())
    if user:
        cart = apis.check_cart()
        print(cart)
        ids = []
        for item in cart:
            ids.append(str(item['id']))
        to_add = list(set(items) - set(ids))
        for item in to_add:
            print("[+] Adding to cart item " + item)
            apis.add_to_cart(item)
    else:
        print("[-] Removing account {} due to error".format(apis.account_file))
        api.remove(apis)


def add_items(api):
    for i in items:
        api.add_to_cart(i)


def check_single(return_dict, proxy, api):
    try:
        cart = api[0].check_cart(proxy)
        if len(cart) > 0:
            print("[+] Valid: {} ".format(proxy))
            return_dict[len(return_dict)] = proxy
    except:
        print("[-] Non valid: {} ".format(proxy))


def proxy_checker(f):
    fl = open(f, "r")
    proxies = fl.readlines()
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for proxy in proxies:
        p = multiprocessing.Process(target=check_single, args=(return_dict, proxy.replace("\n", ""), api,))
        p.start()
        jobs.append(p)
        time.sleep(0.0005)

    for job in jobs:
        job.join()

    txt = ""
    for valid in range(len(return_dict)):
        txt = txt + return_dict[valid] + "\n"
    f = open("result.txt", "w")
    f.write(txt)
    f.close()
    print("Checked: " + str(len(proxies)))
    print("Valid: " + str(len(return_dict)))


def lovlya():
    jobs = []
    for worker in workers:
        for i in range(3):
            p = multiprocessing.Process(target=worker.logicV4, args=(i,))
            jobs.append(p)
            p.start()

    for j in jobs:
        j.join()


def checker():
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for worker in workers:
        for i in range(4):
            p = multiprocessing.Process(target=worker.logic2, args=(return_dict,))
            jobs.append(p)
            p.start()
        time.sleep(1)

    while len(return_dict) == 0:
        time.sleep(0.02)

    if return_dict[0]:
        threading.Thread(target=discordManager.detected_product, args=(return_dict[0],)).start()
        for t in jobs:
            t.kill()


def init():
    global api, workers, accounts
    api = []
    workers = []
    accounts = []

    files = glob.glob("accounts/*.txt")
    for file in files:
        name = file.split("\\")[1].split(".txt")[0]
        accounts.append(name)

    discordManager.start()

    for account in accounts:
        acc = ozonManager(account)
        check_account(acc)
        api.append(acc)
        # print(acc.myOrders())
        # add_items(acc)
        workers.append(ozonWorker(acc))


if __name__ == '__main__':
    # tui = consoleApp()
    # threading.Thread(target=tui.run).start()

    # init()
    # proxy_checker("proxylist.txt")
    # checker()

    while True:
        init()
        lovlya()
