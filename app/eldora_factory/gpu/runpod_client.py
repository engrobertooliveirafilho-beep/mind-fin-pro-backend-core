import requests

def send_job(endpoint, payload, api_key):
    headers = {'Authorization': api_key}
    return requests.post(endpoint, json=payload, headers=headers).json()
