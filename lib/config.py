import os.path

CONFIG_DIR = os.path.expanduser("~/.config/spotify-auth")
try:
    os.makedirs(CONFIG_DIR)
except FileExistsError:
    pass

REFRESH_TOKEN_FILE = os.path.join(CONFIG_DIR, 'refresh_token')
AUTH_TOKEN_FILE = os.path.join(CONFIG_DIR, 'auth_token')


def get_auth_token():
    with open(AUTH_TOKEN_FILE, 'r') as f:
        return f.read()

def get_refresh_token():
    with open(REFRESH_TOKEN_FILE, 'r') as f:
        return f.read()

def save_auth_token(auth_token):
    with open(AUTH_TOKEN_FILE, 'w') as f:
        f.write(auth_token)
        
def save_refresh_token(refresh_token):
    with open(REFRESH_TOKEN_FILE, 'w') as f:
        f.write(refresh_token)

