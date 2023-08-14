from file_handler import filesys
import requests
import json
from pydantic import BaseModel

BASE_URL: str = 'http://web:8000/api/v1/' # Must use this address from within containers.

#BASE_URL: str = 'http://localhost:8015/api/v1/'

class CreateUser(BaseModel):
    email: str = None
    password: str = None
    full_name: str = None
    #phone_number: str = None
   # is_verified: bool = True
    #account_locked: bool = False
    #failed_attempts: int = 0

new_user =  CreateUser(
    email="user@Email.com",
    password="super.secret.password",
    full_name="Valued User num"
)   


class UpdateUserMe(BaseModel):
    email: str = None
    password: str = None
    full_name: str = None
    phone_number: str = None
    is_verified: bool = True
    account_locked: bool = False
    failed_attempts: int = 0    

#
# Update Current user:
#
userUp = UpdateUserMe(
    full_name= "John P. Doefitch, Jr.",
    email=None,
    password=None,
    phone_number='2347894567',
    account_locked=False,
    failed_attempts=0
)

class UpdateUserID(BaseModel):
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

def update_user(user_id: int):
    url = f"{BASE_URL}users/{user_id}"
    headers = {
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.for.debugging", verbose=False)}',
        'Content-Type': 'application/json'
    }

    update_user = UpdateUserID(
         full_name="New User Full Name"         
    )
    payload = {
        'full_name': "Ordinary User",
        'email': "johnDoe@jdoe.com"
    }
    response = requests.put(url, headers=headers, json=payload)

    return response.json()


def get_all_users():
    url = f"{BASE_URL}users"

    headers = {
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.for.debugging", verbose=False)}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    return response.json()

def get_me():
    url = f"{BASE_URL}users/me"

    headers = {
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.for.debugging", verbose=False)}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    return response.json()

def update_me(user: UpdateUserMe) -> dict:
    url = f"{BASE_URL}users/me"
    headers = {
        'Authorization': f'Bearer {login(user_id="ddc.dev.python@gmail.com", password="password.for.debugging", verbose=False)}',
        'Content-Type': 'application/json'
    }
    response = requests.put(url, headers=headers, json=user.dict())  
    return response.json()


def create_normal_user(new_user: CreateUser):
    url = f"{BASE_URL}users"
    response = requests.post(url, json=new_user.dict())
    if response.status_code == 200:
        print("User registered successfully!")
        print(response.json())
    else:
        print(f"Failed to register user. Status code: {response.status_code}")
        print(response.text)


#print(update_me(userUp))
#create_normal_user(new_user)
#print(get_all_users())
print(update_user(2))
#print(get_me())