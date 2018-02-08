import random
import string


def randomword(length=8):
    char_set = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join(random.choice(char_set) for i in range(length))
