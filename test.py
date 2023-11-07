

import string
from random import randint 

upper_alph: str = list(string.ascii_uppercase)

for i in range(len(upper_alph)):    
    if i %2==0: 
        upper_alph[i] = str(randint(0,9))

upper_alph = "".join(upper_alph)
code_2FA = [upper_alph[randint(0,len(upper_alph))] for _ in range(6)]
code_2FA = "".join(code_2FA)            
print(code_2FA)