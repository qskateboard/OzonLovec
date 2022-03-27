import threading

import discordManager
import utils
from ozonManager import ozonManager
import time

class ozonWorker:

    def __init__(self, api):
        self.api = api


    def logic2(self, return_dict):
        found = False
        while not found:
            try:
                cart = self.api.check_cart(utils.rnd_proxy("result.txt"))
                print("[{}] {}:".format(self.api.phone_number, utils.get_time()))
                for item in cart:
                    print("[~] {}: {} ({})".format(item['name'], str(item['price']), item['availability']))
                    if item['availability'] > 0:
                        found = item
                        print("[+] Found restock!")
                        self.api.status = "Found restock!"
                if found:
                    break
            except:
                if found:
                    break
        return_dict[0] = found
        return found


    def logic(self, return_dict):
        found = False
        while not found:
            try:
                cart = self.api.check_cart(utils.rnd_proxy("result.txt"))
                print("[{}] {}:".format(self.api.phone_number, utils.get_time()))
                for item in cart:
                    print("[~] {}: {} ({})".format(item['name'], str(item['price']), item['availability']))
                    if item['availability'] > 0:
                        found = item
                        print("[+] Found restock!")
                        self.api.status = "Found restock!"
                if found:
                    break
                time.sleep(1)
            except:
                if found:
                    break
                time.sleep(1)

        if len(found) > 0:
            self.api.go_checkoutV2(found)
            threading.Thread(target=discordManager.detected_product, args=(found,)).start()
        return found


    def logicV3(self, return_dict):
        found = False
        while not found:
            try:
                self.api.go_checkoutV4(utils.rnd_proxy("result.txt"))
            except:
                if found:
                    break
                time.sleep(1)
        return found


    def logicV4(self, return_dict):
        found = False
        while not found:
            try:
                found = self.api.go_checkoutV4(utils.rnd_proxy("result.txt"))
            except:
                if found:
                    break
                time.sleep(1)
        return found