import re


MIN_LENGTH = 6

def validate_password(password) -> bool|str:
    strength = 0

    if not re.search("[a-zA-Z]", password):
        return "Password must contain an alphabet"

    if len(password) > MIN_LENGTH:
        strength += 1 + _length_additional_point(password)
    else:
        return f"Password must longer than {MIN_LENGTH}"

    if re.search("[!#$%&?@_]", password):
        strength += 1
#    else:
#        return "Password must contain a special character ( !#$%&?@_ )"

    if re.search("[0-9]", password):
        strength += 1
#    else:
#        return "Password must contain a number"

    if strength > 3:
        return True
    return "Please provide stronger password ( longer, complex )"

def _length_additional_point(password):
    addition = len(password) - MIN_LENGTH
    return ( addition / 2 ) / MIN_LENGTH
