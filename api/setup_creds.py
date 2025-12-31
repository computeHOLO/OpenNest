from passlib.context import CryptContext
from cryptography.fernet import Fernet
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    if len(sys.argv) != 3:
        print("usage: python setup_creds.py <username> <password>")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    hashed = pwd_context.hash(password)
    key = Fernet.generate_key()
    with open("cred.key", "wb") as kf:
        kf.write(key)
    f = Fernet(key)
    data = f.encrypt(f"{username}:{hashed}".encode())
    with open("cred.store", "wb") as sf:
        sf.write(data)
    print("credentials initialized")

if __name__ == "__main__":
    main()
