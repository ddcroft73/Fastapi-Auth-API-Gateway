#from file_handler import filesys
import requests
import json
from pydantic import BaseModel

BASE_URL: str = 'http://web:8000/api/v1/' # Must use this address from within containers.

#BASE_URL: str = 'http://localhost:8015/api/v1/'

class UpdateUser(BaseModel):
    email: str = None
    password: str = None
    full_name: str = None
    phone_number: str = None
    is_verified: bool = True
    account_locked: bool = False
    failed_attempts: int = 0
    

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
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.for.debugging", verbose=False)}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    return response.json()


def update_me(user: User) -> dict:
    url = f"{BASE_URL}users/me"
    headers = {
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.for.debugging", verbose=False)}',
        'Content-Type': 'application/json'
    }
    response = requests.put(url, headers=headers, json=user.dict())  
    return response.json()

#
# Update Current user:
#
user = UpdateUser(
    full_name= "John P. Doefitch, Jr.",
    email=None,
    password=None,
    phone_number='2347894567',
    account_locked=False,
    failed_attempts=2
)

print(update_me(user))
