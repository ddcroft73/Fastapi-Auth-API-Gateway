
# This is mearly a script I can run by itself to test out code.

import json
from datetime import datetime, timezone
from typing import Optional, Union

'''def format_dict_string(data_dict: dict) -> str:        
    data_dict = str(data_dict)
    lines = data_dict.split(', ')
    formatted_lines = ['\t' + line for line in lines]
    formatted_data = '\n' + ',\n'.join(formatted_lines) + '\n'

    return formatted_data


user_dict = {
    "username": "userdeftOne@email.com",
    "login_time": datetime.now(timezone.utc),
    "ip_address": "209.34.55.124"
}

user_data = format_dict_string(user_dict)
print(user_data)'''

def format_dict_string(data_dict: dict) -> str:
    json_string = json.dumps(data_dict, indent=4, default=str)
    return json_string

user_dict = {
    "username": "userdeftOne@email.com",
    "login_time": datetime.now(timezone.utc),
    "ip_address": "209.34.55.124"
}

user_data = format_dict_string(user_dict)
print(user_data)