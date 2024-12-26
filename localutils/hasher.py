from django.conf import settings

from hashlib import sha512
from secrets import token_hex



def custom_hasher(password, salt=None, _batch=1000) -> [str, 146]:
    if not salt:
        salt = token_hex(settings.SALT_BYTE)
    password = f"{salt}{password}".encode('utf-8')
    for _ in range(_batch):
        password = sha512(password).hexdigest().encode('utf-8')
    password = password.decode('utf-8')
    return f"{salt}{settings.SALT_SEP}{password}"

def check_password(password, target_str) -> bool:
    salt, _ = target_str.split(settings.SALT_SEP)
    if custom_hasher(password, salt=salt) == target_str:
        return True
    return False


'''
def _my_hash(password, salt=None) -> [str, 146]:
    if not salt:
        salt = token_hex(8)
    salted_str = f"{salt}{password}".encode('utf-8')
    result_str = sha512(salted_str).hexdigest()
    return f"{salt}::{result_str}"

def _pw_check(password, target_str) -> bool:
    salt, _ = target_str.split("::")
    if _my_hash(password, salt=salt) == target_str:
        return True
    return False
'''
