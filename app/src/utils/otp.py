from random import randint

def generate_otp():
    otp = randint(100000, 999999)
    return otp