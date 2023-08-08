import requests
import json

BASE_URL: str = 'http://localhost:8015/api/v1/'

#Login and get token
def login(user_id: str, password: str, verbose: bool=True):
    url = f"{BASE_URL}auth/login/access-token"

    payload = {
        "username": user_id,
        "password": password,
    }
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        if verbose: print("Access token:", access_token)
    else:
       if verbose: print("Failed to authenticate:", response.text)

    return access_token


def get_me():
    url = f"{BASE_URL}users/me"

    headers = {
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.superserial.safe", verbose=False)}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    return response.json()

print(get_me())
