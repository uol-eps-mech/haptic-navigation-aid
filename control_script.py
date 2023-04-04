import requests
from time import sleep
url = "http://192.168.137.13:8000/update"

print("Sending Request")
requests.get(url)
# sleep(1)