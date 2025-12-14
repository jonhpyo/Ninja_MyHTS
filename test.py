import bcrypt

password = "1234".encode("utf-8")
hashed = bcrypt.hashpw(password, bcrypt.gensalt())  # cost=12 기본

print(hashed.decode("utf-8"))