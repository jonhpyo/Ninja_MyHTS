import bcrypt

raw = "admin"
db_hash = "$2b$12$kEa9Vg9PDB28ymb4dNLAdeUoMa9gHIFfzSstIo3dEyGZlR3fMgjCW"
print(raw.encode())
print(bcrypt.checkpw(raw.encode(), db_hash.encode()))
