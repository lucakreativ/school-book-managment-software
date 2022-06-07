import hashlib

def hash_func(text):
    i=0
    while i < 500:
        i+=1
        text=hashlib.sha512(str(text).encode("utf-8")).hexdigest()

    return text