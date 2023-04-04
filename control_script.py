import requests
from time import sleep
url = "http://192.168.137.13:8000/update"

while True:
    print("Sending Request")
    requests.get(url)
    sleep(0.5) #2Hz 