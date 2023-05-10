import json

import requests
from prefect import flow

@flow(name="Simple Flow", log_prints=True)
def call_api(url: str = "http://time.jsontest.com/"):
    """Sends a GET request to the provided URL and returns the JSON response"""
    resp = requests.get(url).json()
    print(resp)
    return resp
