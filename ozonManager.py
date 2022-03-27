import multiprocessing
import sys
import time
import traceback
import json
from urllib.parse import unquote

import discordManager
import utils
import requests


class ozonManager:

    def __init__(self, account_file):
        self.account_file = account_file
        self.phone_number = account_file
        self.session = requests.Session()

        self.status = "Initialization"
        try:
            account = utils.read_file(account_file).split("```", 4)

            self.proxy = account[0]
            self.access_token = account[1]
            self.refresh_token = account[2]
            self.cookies = account[3]

            proxies = {"http": self.proxy}
            self.session.proxies.update(proxies)
            print(proxies)
        except:
            pass

    def __del__(self):
        try:
            account = "{}```{}```{}```{}".format(self.proxy, self.access_token, self.refresh_token, self.cookies)
            utils.save_file(self.account_file, account)
        except:
            pass

    def set_status(self, action):
        self.status = action

    def get_status(self):
        return self.status

    def set_cookies(self):
        try:
            self.session.cookies.clear_session_cookies()
            rcookies = self.cookies.replace("\n", "").split(";")
            for k in rcookies:
                k = k.split('=', 1)
                self.session.cookies.update({k[0]: k[1]})
        except:
            pass

    def update_cookies(self):
        cookies = ""
        for c in self.session.cookies:
            if c.value == "":
                c.value = "0"
            cookies = c.name + "=" + str(c.value) + ";" + cookies
        self.cookies = cookies[:-1]
        account = "{}```{}```{}```{}".format(self.proxy, self.access_token, self.refresh_token, self.cookies)
        utils.save_file(self.account_file, account)

    def refreshToken(self):
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            "refreshToken": self.refresh_token
        }
        self.status = "Refreshing auth token"
        self.session.cookies.clear_session_cookies()
        response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/initAuthRefresh", json=data,
                                     headers=headers)
        print(response.text)
        self.access_token = response.json()["authToken"]["accessToken"]
        self.refresh_token = response.json()["authToken"]["refreshToken"]
        self.update_cookies()
        self.status = "Idle"

    def get_user(self):
        try:
            self.set_cookies()
            headers = {
                "x-o3-app-name": "ozonapp_android",
                "User-Agent": "ozonapp_android/13.6+1532",
                "Authorization": "Bearer {}".format(self.access_token),
                "x-o3-device-type": "mobile",
                "x-o3-app-version": "13.6(1532)",
                "Content-Type": "application/json;charset=UTF-8",
                "Accept": "application/json;charset=utf-8",
                "Accept-Encoding": "gzip",
                "x-o3-sample-trace": "false",
                "Connection": "Keep-Alive",
                "Host": "api.ozon.ru",
            }
            self.status = "Get user information"
            self.session.headers = headers
            response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/getUserV2",
                                         data='{"contacts":false,"email":true,"phone":true,"profile":true,"public":false}',
                                         headers=headers)
            print(response.text)
            if response.text == "" or response.text == "{\"error\":\"unauthorized\"}":
                self.refreshToken()
                return self.get_user()
            try:
                response = response.json()
                print("[+] Logged in: " + response["credentials"]["phone"])
                try:
                    if response["profile"]["firstName"]:
                        pass
                except:
                    self.set_user_name("Иван", "Иванов")
                return True
            except:
                try:
                    if response["errorCode"]:
                        self.status = "Incapsula error while auth"
                        return False
                except:
                    print("[-] Cant get user data: " + str(response["error"]))
                    self.status = "Cant get user data"
                    return False
        except Exception as e:
            self.status = "Eror while log in"

    def set_user_name(self, name, surname):
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            "lastName": surname,
            "firstName": name,
            "middleName": ""
        }
        self.status = "Setting up account name"
        self.session.post("https://api.ozon.ru/composer-api.bx/_action/patchUserProfile", headers=headers, json=data)
        self.status = "Idle"

    def go_checkoutV4(self, proxy=""):
        if proxy:
            proxies = dict.fromkeys(('http', 'https', 'ftp'), proxy)
            print(proxies)
            self.session.proxies.update(proxies)
        checkout_headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        checkout_data = {
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "nativePaymentEnabled": True,
            "nativePaymentConfigured": False
        }

        r = self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fstart%3D0",
                              headers=checkout_headers, json=checkout_data, timeout=5)
        if r.status_code == 401 or r.text == "":
            return True

        tracking_payloads = r.json()["trackingPayloads"]
        found = False
        for quote_payload in tracking_payloads:
            if "products" in tracking_payloads[quote_payload]:
                found = True
                run = utils.get_time()
                if proxy:
                    proxies = {"http": self.proxy}
                    self.session.proxies.update(proxies)
                response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/createOrder",
                                             headers=checkout_headers)

                success = str((utils.get_time() - run).seconds) + str(
                    int(str((utils.get_time() - run).microseconds)[:3])) + "ms"
                print(success)
                print(response)
                print(response.text)
                print(response.headers)

                payload = json.loads(tracking_payloads[quote_payload])['products'][0]
                item = {'id': payload['sku'], 'name': payload['title'], 'price': payload['finalPrice'],
                        'availability': payload['availability']}
                try:
                    if response.json()['link']:
                        print("[+] Успешный check out!")
                        self.status = "Success checkout"
                        discordManager.success_checkout(self.account_file, success, item)
                except Exception as e:
                    print("[-] error: " + str(e) + " line: " + str(sys.exc_info()[-1].tb_lineno) + " traceback: " + str(
                        traceback.print_exc()))
                    try:
                        if response.json()['error']['message']:
                            discordManager.bad_checkout(self.account_file, str(success),
                                                        response.json()['error']['message'], item, express=False)
                    except:
                        discordManager.bad_checkout(self.account_file, str(success),
                                                    "Неизвестная ошибка. Код ответа: {}".format(
                                                        str(response.status_code)), item, express=False)
                        pass
                    self.status = "Error while checkout"
                    pass
                self.status = "Idle"
                print("Time: {}".format(str(success)))
        if not found:
            print("[{}] Nothing found".format(self.account_file))
        if proxy:
            proxies = {"http": self.proxy}
            self.session.proxies.update(proxies)
        return False

    def requests_post(self, return_dict, url, headers, data=""):
        return_dict[0] = self.session.post(url, headers=headers, json=data)

    def progrev_checkout(self):
        run = utils.get_time()
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            # "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "nativePaymentEnabled": True,
            "nativePaymentConfigured": False
        }
        self.status = "Preparing checkout"
        self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fcart", headers=headers, json=data)
        try:
            response = self.session.post(
                "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fstart%3D0",
                allow_redirects=False, headers=headers, json=data)
            apply_address = response.headers['Location'].split("apply_address=")[1]
            print(apply_address)
            # apply_address = "3085a84f-58a7-4969-8688-d8b0f1aca3ce" f0925f68-9362-4fe3-a6ba-4561b10e5cb8
        except:
            data = {
                "map": {
                    "viewport": {
                        "leftBottom": {
                            "latitude": 60.031477063448676,
                            "longitude": 30.422410098147907
                        },
                        "rightTop": {
                            "latitude": 60.036304009066974,
                            "longitude": 30.42799390185212
                        }
                    },
                    "zoom": 16.88328,
                    "isGeoLocation": True,
                }
            }
            self.session.post(
                "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%2Fdelivery%2Fmap%3Fpid%3D10%26place%3Dcurtain%26pp%3D7682%26ppex%3Dt%26tab%3Dpp",
                allow_redirects=False, headers=headers, json=data)
            data = {
                "form": {
                    "receiverName": "Иван Иванов",
                    "receiverPhone": self.phone_number,
                }
            }
            response = self.session.post(
                "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%2Fdelivery%3Fpid%3D7%26place%3Dcurtain%26pp%3D95444%26ppex%3Dt%26tab%3Dpp",
                allow_redirects=False, headers=headers, json=data)
            apply_address = response.headers['Location'].split("apply_address=")[1]
            print("2: " + apply_address)

        self.status = "Creating order"
        self.session.post(
            "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fapply_address=" + apply_address,
            allow_redirects=False, headers=headers, json=data)

        self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout", allow_redirects=False,
                          headers=headers, json=data)

    def go_checkoutV3(self, item):
        run = utils.get_time()
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "nativePaymentEnabled": True,
            "nativePaymentConfigured": False
        }
        link1 = "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fstart%3D0"
        # link2 = "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout"
        link3 = "https://api.ozon.ru/composer-api.bx/_action/createOrder"
        manager = multiprocessing.Manager()
        shit = manager.dict()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=self.requests_post, args=(shit, link1, headers, data,))
        # p2 = multiprocessing.Process(target=self.requests_post, args=(shit, link2, headers, data,))
        p3 = multiprocessing.Process(target=self.requests_post, args=(return_dict, link3, headers,))
        p.start()
        # time.sleep(0.04)
        # p2.start()
        time.sleep(0.04)
        p3.start()

        while len(return_dict) == 0:
            time.sleep(0.01)

        success = str(utils.get_time() - run)
        response = return_dict[0]

        try:
            if response.json()['link']:
                self.status = "Success checkout"
                payload = json.loads(response.json()['trackingInfo']['purchase']['payload'])
                discordManager.success_checkout(self.account_file, success,
                                                payload['cell']['items'][0]['id'])
                print("[+] Успешный check out!")
        except:
            try:
                if response.json()['error']['message']:
                    discordManager.bad_checkout(self.account_file, str(utils.get_time() - run),
                                                response.json()['error']['message'], item)
            except:
                discordManager.bad_checkout(self.account_file, str(utils.get_time() - run), "Неизвестная ошибка", item)
                pass
            self.status = "Error while checkout"
            pass
        self.status = "Idle"
        print("Time: {}".format(str(success)))

    def go_checkoutV2(self, item):
        run = utils.get_time()
        checkout_headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        checkout_data = {
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "nativePaymentEnabled": True,
            "nativePaymentConfigured": False
        }
        express = False
        r = self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fstart%3D0",
                              headers=checkout_headers, json=checkout_data, stream=False)
        print(r)
        print(r.text)
        print(r.headers)
        if r.status_code == 302 and "gocheckout" not in r.headers.get("Location"):
            express = True
            address = "https://api.ozon.ru/composer-api.bx/page/json/v1?url=" + \
                      r.headers.get("Location").split("on://")[1]
            self.session.post(address, headers=checkout_headers, json=checkout_data, stream=False)
            self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout",
                              headers=checkout_headers, json=checkout_data, stream=False)

        response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/createOrder",
                                     headers=checkout_headers)
        success = str((utils.get_time() - run).seconds) + str(
            int(str((utils.get_time() - run).microseconds)[:3])) + "ms"
        print(response)
        print(response.text)
        print(response.headers)
        print(utils.get_time() - run)

        try:
            if response.json()['link']:
                self.status = "Success checkout"
                payload = json.loads(response.json()['trackingInfo']['purchase']['payload'])
                discordManager.success_checkout(self.account_file, success,
                                                payload['cell']['items'][0]['id'], express=express)
                print("[+] Успешный check out!")
        except:
            try:
                if response.json()['error']['message']:
                    discordManager.bad_checkout(self.account_file, str(success),
                                                response.json()['error']['message'], item, express=express)
            except:
                discordManager.bad_checkout(self.account_file, str(success),
                                            "Неизвестная ошибка. Код ответа: {}".format(str(response.status_code)),
                                            item, express=express)
                pass
            self.status = "Error while checkout"
            pass
        self.status = "Idle"
        print("Time: {}".format(str(success)))

    def go_checkout(self, item):
        run = utils.get_time()
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            # "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "nativePaymentEnabled": True,
            "nativePaymentConfigured": False
        }
        self.status = "Preparing checkout"
        self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fcart", headers=headers, json=data)
        try:
            response = self.session.post(
                "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fstart%3D0",
                allow_redirects=False, headers=headers, json=data)
            apply_address = response.headers['Location'].split("apply_address=")[1]
            print(apply_address)
            # apply_address = "3085a84f-58a7-4969-8688-d8b0f1aca3ce" f0925f68-9362-4fe3-a6ba-4561b10e5cb8
        except:
            data = {
                "map": {
                    "viewport": {
                        "leftBottom": {
                            "latitude": 60.031477063448676,
                            "longitude": 30.422410098147907
                        },
                        "rightTop": {
                            "latitude": 60.036304009066974,
                            "longitude": 30.42799390185212
                        }
                    },
                    "zoom": 16.88328,
                    "isGeoLocation": True,
                }
            }
            self.session.post(
                "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%2Fdelivery%2Fmap%3Fpid%3D10%26place%3Dcurtain%26pp%3D7682%26ppex%3Dt%26tab%3Dpp",
                allow_redirects=False, headers=headers, json=data)
            data = {
                "form": {
                    "receiverName": "Иван Иванов",
                    "receiverPhone": self.phone_number,
                }
            }
            response = self.session.post(
                "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%2Fdelivery%3Fpid%3D7%26place%3Dcurtain%26pp%3D95444%26ppex%3Dt%26tab%3Dpp",
                allow_redirects=False, headers=headers, json=data)
            apply_address = response.headers['Location'].split("apply_address=")[1]
            print("2: " + apply_address)

        self.status = "Creating order"
        self.session.post(
            "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout%3Fapply_address=" + apply_address,
            allow_redirects=False, headers=headers, json=data)

        self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fgocheckout", allow_redirects=False,
                          headers=headers, json=data)

        response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/createOrder", headers=headers)
        success = str((utils.get_time() - run).seconds) + str(
            int(str((utils.get_time() - run).microseconds)[:3])) + "ms"
        try:
            if response.json()['link']:
                self.status = "Success checkout"
                payload = json.loads(response.json()['trackingInfo']['purchase']['payload'])
                discordManager.success_checkout(self.account_file, success, payload['cell']['items'][0]['id'])
                print("[+] Успешный check out!")
        except:
            try:
                if response.json()['error']['message']:
                    discordManager.bad_checkout(self.account_file, success, response.json()['error']['message'], item)
            except:
                discordManager.bad_checkout(self.account_file, success, "Неизвестная ошибка", item)
                pass
            self.status = "Error while checkout"
            pass
        self.status = "Idle"
        print("Time: {}".format(success))

    def add_to_cart(self, uid):
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        self.status = "Add item to cart"
        self.session.post('https://api.ozon.ru/composer-api.bx/_action/addToCart', headers=headers,
                          data='[{"id":' + uid + ',"quantity":1}]')
        self.status = "Idle"

    def check_cart(self, proxy=""):
        if proxy:
            proxies = dict.fromkeys(('http', 'https', 'ftp'), proxy)
            print(proxies)
            self.session.proxies.update(proxies)
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        rcookies = self.cookies.replace("\n", "").split(";")
        self.status = "Checking cart"
        cookies = {}
        for k in rcookies:
            k = k.split('=', 1)
            cookies.update({k[0]: k[1]})

        response = self.session.post(
            'https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fcart%3Fpage_changed%3Dtrue',
            headers=headers, cookies=cookies, timeout=5)
        if response.text == "" or response.status_code == 401:
            self.refreshToken()
            return []
        try:
            cart = response.json()["cart"]["shared"]["itemsTrackingInfo"]
            items = []
            for item in range(len(cart)):
                items.append({'id': cart[item]['id'], 'name': cart[item]['title'], 'price': cart[item]['finalPrice'],
                              'availability': cart[item]['availability']})
            self.status = "Idle"
            if proxy:
                proxies = {"http": self.proxy}
                self.session.proxies.update(proxies)
            return items
        except:
            if response.json()["errorCode"]:
                print("[{}] Incapsula error {}".format(self.account_file, str(response.json()["errorCode"])))
        return []

    def cancelOrder(self, uid):
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            "cancellationReasonId": 507,
            "cancellationReasonMessage": "",
            "orderId": str(uid)
        }
        self.status = "Cancel order"
        response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/cancelOrderHandler", json=data,
                                     headers=headers).json()
        self.status = "Idle"

    def removeCart(self, uid):
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            "ru.ozon.app.android.checkout.cart.splitcart.SplitCartItemViewHolderKt.KEY_ACTION_TYPE": "ru.ozon.app.android.checkout.cart.splitcart.SplitCartItemViewHolderKt.ACTION_REMOVE_ITEM",
            "ru.ozon.app.android.checkout.cart.splitcart.SplitCartItemViewHolderKt.KEY_SPLIT_ID": "{}".format(uid),
            "ru.ozon.app.android.commonwidgets.quantity.QuantityDialog.KEY_SELECTED_QUANTITY": -1
        }
        self.status = "Remove item from cart"
        response = self.session.post(
            "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fcart%3Fdelete%3D{}".format(uid), json=data,
            headers=headers).json()
        self.status = "Idle"

    def myOrders(self):
        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "x-o3-app-version": "13.6(1532)",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json;charset=utf-8",
            "Accept-Encoding": "gzip",
            "x-o3-sample-trace": "false",
            "Connection": "Keep-Alive",
            "Host": "api.ozon.ru",
        }
        data = {
            "hasSmartLock": True,
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "biometryType": "FINGER_PRINT",
            "hasBiometrics": False,
            "version": "7.1.2",
            "vendor": "samsung",
            "model": "Samsung SM-N975F"
        }
        self.status = "My orders"
        response = self.session.post("https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fmy", json=data,
                                     headers=headers)
        # print(response.text)
        response = response.json()
        orders = []
        try:
            for item in response['csma']['orderTracking']:
                for order in range(len(response['csma']['orderTracking'][item]['ordersWithoutShipments'])):
                    product = response['csma']['orderTracking'][item]['ordersWithoutShipments'][order]
                    arr = {
                        "id": product['id'],
                        "hint": unquote(product['hint']).replace("\xa0", ""),
                    }
                    orders.append(arr)
        except:
            pass
        self.status = "Idle"
        return orders

    def auth(self):
        self.status = "Preparing authorization"
        if len(utils.read_file(self.account_file)) == 0:
            headers = {
                "Accept": "application/json;charset=utf-8",
                "x-o3-device-type": "mobile",
                "User-Agent": "ozonapp_android/13.6+1532",
                "x-o3-app-name": "ozonapp_android",
                "x-o3-app-version": "13.6(1532)",
                "Content-Type": "application/json;charset=utf-8",
                "Content-Length": "25",
                "Host": "api.ozon.ru",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
            }
            data = {
                "clientId": "androidapp"
            }
            response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/initAuth", json=data,
                                         headers=headers).json()
            print(response)
            try:
                self.access_token = response["authToken"]["accessToken"]
                self.refresh_token = response["authToken"]["refreshToken"]
            except:
                pass

        headers = {
            "x-o3-app-name": "ozonapp_android",
            "User-Agent": "ozonapp_android/13.6+1532",
            "Authorization": "Bearer {}".format(self.access_token),
            "x-o3-device-type": "mobile",
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "hasSmartLock": "true",
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "biometryType": "FINGER_PRINT",
            "hasBiometrics": "false",
            "version": "7.1.2",
            "vendor": "samsung",
            "model": "Samsung SM-N975F"
        }
        self.status = "Device confirm.."
        response = self.session.post(
            "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fmy%2Fentry%2Fcredentials-required", json=data,
            headers=headers)
        response = response.json()
        entry = False
        for item in response["csma"]["entryCredentialsRequired"]:
            if not entry:
                entry = response["csma"]["entryCredentialsRequired"][item]
        csrf_token = entry["submitButton"]["action"]

        data = {
            "phone": self.phone_number,
            "biometryType": "FINGER_PRINT",
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "hasBiometrics": "false",
            "version": "7.1.2",
            "vendor": "samsung",
            "model": "Samsung SM-N975F",
            "hasSmartLock": "true"
        }
        self.status = "Send SMS code.."
        response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/" + csrf_token, json=data,
                                     headers=headers)
        print(response.text)
        deeplink = unquote(response.json()["status"]["deeplink"]).split("?action=")[1]

        self.status = "Waiting for sms code"
        otp = input("[{}] Введите OTP код: ".format(self.account_file))

        data = {
            "state": "",
            "phone": self.phone_number,
            "ozonIdRequestToken": "",
            "isStatusSuccess": "false",
            "isAlphanumericOtp": "false",
            "isOtpExpired": "false",
            "otp": str(otp),
            "biometryType": "FINGER_PRINT",
            "deviceId": "e14290b5-98b5-4635-a3f3-42a923756c57",
            "hasBiometrics": "false",
            "version": "7.1.2",
            "vendor": "samsung",
            "model": "Samsung SM-N975F",
            "hasSmartLock": "true"
        }
        self.status = "Login.."
        response = self.session.post("https://api.ozon.ru/composer-api.bx/_action/" + deeplink, json=data,
                                     headers=headers)
        print(response.text)
        self.access_token = response.json()["data"]["authToken"]["accessToken"]
        self.refresh_token = response.json()["data"]["authToken"]["refreshToken"]
        self.update_cookies()
        self.status = "Idle"
