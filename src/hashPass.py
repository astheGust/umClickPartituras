import bcrypt
def hashPassword(password):
    pswBytes = password.encode("utf-8")
    salt = bcrypt.gensalt(10)
    hashedPassword = bcrypt.hashpw(pswBytes, salt)
    return hashedPassword.decode("utf-8")

def comparePassword(password,hash):
    psw = password.encode("utf-8")
    hashed = hash.encode("utf-8")
    if bcrypt.checkpw(psw, hashed):
        return True
    else:
        return False
